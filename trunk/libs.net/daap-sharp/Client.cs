/*
 * daap-sharp
 * Copyright (C) 2005  James Willcox <snorp@snorp.net>
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */

using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.IO;
using System.Web;
using System.Net;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using Nwc.XmlRpc;
using DMP;
using DMP.Data;

namespace DAAP {

    public class Client : IDisposable {
        private const int UpdateSleepInterval = 2 * 60 * 1000; // 2 minutes

        private int id; //the library id
        private IPAddress address;
        private UInt16 port;
        private ContentCodeBag bag;
        private ServerInfo serverInfo;
        //private List<ClientDatabase> databases = new List<ClientDatabase> ();
        private ClientDatabase database;
        private ContentFetcher fetcher;
        private int revision;
        private bool updateRunning;
        //Added from the old BridgeDatabase.Library
        public string username;
        public string password;
        public int lastSync;
        public int lastSeen;

        public event EventHandler Updated;

        public int Id
        {
            get { return id; }
            set { id = value; }
        }

        public string Username
        {
            get { return username; }
        }

        public string Password
        {
            get { return password; }
        }

        internal int Revision {
            get { return revision; }
        }

        public string Name {
            get { return serverInfo.Name; }
        }

        public IPAddress Address {
            get { return address; }
        }

        public ushort Port {
            get { return port; }
        }

        public AuthenticationMethod AuthenticationMethod {
            get { return serverInfo.AuthenticationMethod; }
        }

        public ClientDatabase Database {
            get { return database; }
        }

        internal ContentCodeBag Bag {
            get { return bag; }
        }

        internal ContentFetcher Fetcher {
            get { return fetcher; }
        }

        public Client (Service service) : this (service.Address, service.Port) {
        }
        
        /// <summary>
        /// Takes DNS name, finds IP, and calls regular constructor
        /// </summary>
        /// <param name="host">DNS name</param>
        /// <param name="port"></param>
        public Client (string host, UInt16 port) : this (Dns.GetHostEntry(host).AddressList[0], port) {
        }

        public Client (IPAddress address, UInt16 port) {
            BridgeDatabase theData = new BridgeDatabase();
            this.address = address;
            this.port = port;
            fetcher = new ContentFetcher (address, port);

            bag = ContentCodeBag.ParseCodes (fetcher.Fetch ("/content-codes"));

            ContentNode node = ContentParser.Parse (ContentCodeBag.Default, fetcher.Fetch ("/server-info"));
            serverInfo = ServerInfo.FromNode (node);

            int libraryId = theData.getRemoteLibraryId(this.Name);
            if(libraryId == -1){
                //Puts this instance of the client in the SQLite database
                theData.addLibrary(this);
            }
            else
                this.Id = libraryId;
        }

        ~Client () {
            Dispose ();
        }

        public void Dispose () {
            updateRunning = false;
            
            if (fetcher != null) {
                fetcher.Dispose ();
                fetcher = null;
            }
        }

        private void ParseSessionId (ContentNode node) {
            fetcher.SessionId = (int) node.GetChild ("dmap.sessionid").Value;
        }

        public void Login ()
        {
            Login (null, null);
        }

        public void Login(string password) {
            Login (null, password);
        }

        public void Login(string username, string password) {
            fetcher.Username = username;
            fetcher.Password = password;

            try {
                ContentNode node = ContentParser.Parse (bag, fetcher.Fetch ("/login"));
                ParseSessionId (node);

                FetchDatabase ();
                Refresh ();
                
                if (serverInfo.SupportsUpdate) {
                    updateRunning = true;
                    Thread thread = new Thread (UpdateLoop);
                    thread.IsBackground = true;
                    thread.Start ();
                }
            } catch (WebException e) {
                if (e.Response != null && (e.Response as HttpWebResponse).StatusCode == HttpStatusCode.Unauthorized)
                    throw new AuthenticationException ("Username or password incorrect");
                else
                    throw new LoginException ("Failed to login", e);
            } catch (Exception e) {
				Console.WriteLine("DAAP Client: " + e.Message);
				Console.WriteLine(e.StackTrace);
                throw new LoginException ("Failed to login2", e);
            }
        }

        public void Logout () {
            try {
                updateRunning = false;
                fetcher.KillAll ();
                fetcher.Fetch ("/logout");
            } catch (WebException e) {
                // some servers don't implement this, etc.
            }
            
            fetcher.SessionId = 0;
        }

        private void FetchDatabase () {
            ContentNode dbnode = ContentParser.Parse (bag, fetcher.Fetch ("/databases"));

            foreach (ContentNode child in (ContentNode[]) dbnode.Value) {
                if (child.Name != "dmap.listing")
                    continue;

                //we only support 1 database, so it's whatever the last
                //one they sent us was
                foreach (ContentNode item in (ContentNode[]) child.Value) {
                    database = new ClientDatabase (this, item);
                }
            }
        }

        private int GetCurrentRevision () {
            ContentNode revNode = ContentParser.Parse (bag, fetcher.Fetch ("/update"), "dmap.serverrevision");
            return (int) revNode.Value;
        }

        private int WaitForRevision (int currentRevision) {
            ContentNode revNode = ContentParser.Parse (bag, fetcher.Fetch ("/update",
                                                                           "revision-number=" + currentRevision));

            return (int) revNode.GetChild ("dmap.serverrevision").Value;
        }

        private void Refresh()
        {
            int newrev = revision;

            if (serverInfo.SupportsUpdate) {
                if (revision == 0)
                    newrev = GetCurrentRevision ();
                else
                    newrev = WaitForRevision (revision);

                if (newrev == revision){
                    return;
                }
            }
                
            // Console.WriteLine ("Got new revision: " + newrev);
            database.Refresh (newrev);
            
            revision = newrev;
            if (Updated != null)
                Updated (this, new EventArgs ());
        }

        private void UpdateLoop () {
            while (true) {
                try {
                    if (!updateRunning)
                        break;
                    
                    Refresh();
                } catch (WebException e) {
                    if (!updateRunning)
                        break;
                    
                    // chill out for a while, maybe the server went down
                    // temporarily or something.
                    Thread.Sleep (UpdateSleepInterval);
                } catch (Exception e) {
                    if (!updateRunning)
                        break;
                    
                    Console.Error.WriteLine ("Exception in update loop: " + e);
                    Thread.Sleep (UpdateSleepInterval);
                }
            }
        }

        public Object XmlRpcRequest(string methodName, params object[] paramValues)
        {
            //Set up the XmlRpcRequest to construct an XML-RPC message
            XmlRpcRequest xmlClient = new XmlRpcRequest();

            xmlClient.MethodName = methodName;
            xmlClient.Params.Clear();

            foreach (object parameter in paramValues)
            {
                xmlClient.Params.Add(parameter);
            }
            //Construct the message
            string xmlRequest = HttpUtility.UrlEncode(xmlClient.ToString());

            //Send the message
            ContentNode xmlNode = 
                ContentParser.Parse(bag, fetcher.Fetch("/xmlrpc","request=" + xmlRequest));

            //Put message in a stream so the the XML-RPC library can handle it
            string xmlStringResponse = (string)xmlNode.GetChild("dmp.xmlresponsemessage").Value;
            byte[] xmlStringBytes = Encoding.ASCII.GetBytes(xmlStringResponse);
            MemoryStream xmlStream = new MemoryStream(xmlStringBytes);
            StreamReader xmlData = new StreamReader(xmlStream);

            //Relay the returned value back to our caller
            XmlRpcResponse xmlResponse = XmlRpcResponseDeserializer.Parse(xmlData);

            if (xmlResponse.IsFault)
            {
                return new Error(xmlResponse.FaultString, xmlResponse.FaultCode);
            }
            else
                return xmlResponse.Value;
        }
    }
}
