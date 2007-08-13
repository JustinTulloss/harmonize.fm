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
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using System.Threading;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Collections.Specialized;
using System.Net;
using System.Net.Sockets;
using System.Web;
using Nwc.XmlRpc;
using DMP.Server;

#if ENABLE_MDNSD
using Mono.Zeroconf;
#else
using Avahi;
#endif

namespace DAAP {

    internal delegate bool WebHandler (Socket client, string user, string path, NameValueCollection query, int range);

    internal class WebServer {

        private const int ChunkLength = 8192;

        private UInt16 port;
        private Socket server;
        private WebHandler handler;
        private bool running;
        private List<NetworkCredential> creds = new List<NetworkCredential> ();
        private ArrayList clients = new ArrayList ();
        private string realm;
        private AuthenticationMethod authMethod = AuthenticationMethod.None;
        
        public ushort RequestedPort {
            get { return port; }
            set { port = value; }
        }

        public ushort BoundPort {
            get { return (ushort) (server.LocalEndPoint as IPEndPoint).Port; }
        }

        public IList<NetworkCredential> Credentials {
            get { return new ReadOnlyCollection<NetworkCredential> (creds); }
        }

        public AuthenticationMethod AuthenticationMethod {
            get { return authMethod; }
            set { authMethod = value; }
        }

        public string Realm {
            get { return realm; }
            set { realm = value; }
        }
        
        public WebServer (UInt16 port, WebHandler handler) {
            this.port = port;
            this.handler = handler;
        }

        public void Start () {
            server = new Socket (AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
            server.Bind (new IPEndPoint (IPAddress.Any, port));
            server.Listen (10);

            running = true;
            Thread thread = new Thread (ServerLoop);
            thread.IsBackground = true;
            thread.Start ();
        }

        public void Stop () {
            running = false;
            
            if (server != null) {
                server.Close ();
                server = null;
            }

            foreach (Socket client in (ArrayList) clients.Clone ()) {
                // do not pass go, do not collect $200...
                client.Close ();
            }
        }

        public void AddCredential (NetworkCredential cred) {
            creds.Add (cred);
        }

        public void RemoveCredential (NetworkCredential cred) {
            creds.Remove (cred);
        }
        
        public void WriteResponse (Socket client, ContentNode node) {
            WriteResponse (client, HttpStatusCode.OK,
                           ContentWriter.Write (ContentCodeBag.Default, node));
        }

        public void WriteResponse (Socket client, HttpStatusCode code, string body) {
            WriteResponse (client, code, Encoding.UTF8.GetBytes (body));
        }
        
        public void WriteResponse (Socket client, HttpStatusCode code, byte[] body) {
            if (!client.Connected)
                return;
            
            using (BinaryWriter writer = new BinaryWriter (new NetworkStream (client, false))) {
                writer.Write (Encoding.UTF8.GetBytes (String.Format ("HTTP/1.1 {0} {1}\r\n", (int) code, code.ToString ())));
                writer.Write (Encoding.UTF8.GetBytes ("DAAP-Server: daap-sharp\r\n"));
                writer.Write (Encoding.UTF8.GetBytes ("Content-Type: application/x-dmap-tagged\r\n"));
                writer.Write (Encoding.UTF8.GetBytes (String.Format ("Content-Length: {0}\r\n", body.Length)));
                writer.Write (Encoding.UTF8.GetBytes ("\r\n"));
                writer.Write (body);
            }
        }

        public void WriteResponseFile (Socket client, string file, long offset) {
            FileInfo info = new FileInfo (file);

            FileStream stream = info.Open(FileMode.Open, FileAccess.Read, FileShare.Read);
            WriteResponseStream (client, stream, info.Length, offset);
        }

        public void WriteResponseStream (Socket client, Stream response, long len) {
            WriteResponseStream (client, response, len, -1);
        }

        public void WriteResponseStream (Socket client, Stream response, long len, long offset) {
            using (BinaryWriter writer = new BinaryWriter (new NetworkStream (client, false))) {

                if (offset > 0) {
                    writer.Write (Encoding.UTF8.GetBytes ("HTTP/1.1 206 Partial Content\r\n"));
                    writer.Write (Encoding.UTF8.GetBytes (String.Format ("Content-Range: bytes {0}-{1}/{2}\r\n",
                                                                         offset, len, len + 1)));
                    writer.Write (Encoding.UTF8.GetBytes ("Accept-Range: bytes\r\n"));
                    len = len - offset;
                } else {
                    writer.Write (Encoding.UTF8.GetBytes ("HTTP/1.1 200 OK\r\n"));
                }

                writer.Write (Encoding.UTF8.GetBytes (String.Format ("Content-Length: {0}\r\n", len)));
                writer.Write (Encoding.UTF8.GetBytes ("\r\n"));

                using (BinaryReader reader = new BinaryReader (response)) {
                    if (offset > 0) {
                        reader.BaseStream.Seek (offset, SeekOrigin.Begin);
                    }

                    long count = 0;
                    while (count < len) {
                        byte[] buf = reader.ReadBytes (Math.Min (ChunkLength, (int) len - (int) count));
                        if (buf.Length == 0) {
                            break;
                        }
                        
                        writer.Write (buf);
                        count += buf.Length;
                    }
                }
            }
        }

        public void WriteAccessDenied (Socket client) {
            string msg = "Authorization Required";
            
            using (BinaryWriter writer = new BinaryWriter (new NetworkStream (client, false))) {
                writer.Write (Encoding.UTF8.GetBytes ("HTTP/1.1 401 Denied\r\n"));
                writer.Write (Encoding.UTF8.GetBytes (String.Format ("WWW-Authenticate: Basic realm=\"{0}\"",
                                                                     realm)));
                writer.Write (Encoding.UTF8.GetBytes ("Content-Type: text/plain\r\n"));
                writer.Write (Encoding.UTF8.GetBytes (String.Format ("Content-Length: {0}\r\n", msg.Length)));
                writer.Write (Encoding.UTF8.GetBytes ("\r\n"));
                writer.Write (msg);
            }
        }

        private bool IsValidAuth (string user, string pass) {
            if (authMethod == AuthenticationMethod.None)
                return true;

            foreach (NetworkCredential cred in creds) {

                if ((authMethod != AuthenticationMethod.UserAndPassword || cred.UserName == user) &&
                    cred.Password == pass)
                    return true;
            }

            return false;
        }

        private bool HandleRequest (Socket client) {

            if (!client.Connected)
                return false;
            
            bool ret = true;
            
            using (StreamReader reader = new StreamReader (new NetworkStream (client, false))) {

                string request = reader.ReadLine ();
                if (request == null)
                    return false;
                
                string line = null;
                string user = null;
                string password = null;
                int range = -1;
                
                // read the rest of the request
                do {
                    line = reader.ReadLine ();

                    if (line == "Connection: close") {
                        ret = false;
                    } else if (line != null && line.StartsWith ("Authorization: Basic")) {
                        string[] splitLine = line.Split (' ');

                        if (splitLine.Length != 3)
                            continue;

                        string userpass = Encoding.UTF8.GetString (Convert.FromBase64String (splitLine[2]));

                        string[] splitUserPass = userpass.Split (new char[] {':'}, 2);
                        user = splitUserPass[0];
                        password = splitUserPass[1];
                    } else if (line != null && line.StartsWith ("Range: ")) {
                        // we currently expect 'Range: bytes=<offset>-'
                        string[] splitLine = line.Split ('=');

                        if (splitLine.Length != 2)
                            continue;

                        string rangestr = splitLine[1];
                        if (!rangestr.EndsWith ("-"))
                            continue;

                        try {
                            range = Int32.Parse (rangestr.Substring (0, rangestr.Length - 1));
                        } catch (FormatException) {
                        }
                    }
                } while (line != String.Empty && line != null);

                string[] splitRequest = request.Split ();
                if (splitRequest.Length < 3) {
                    WriteResponse (client, HttpStatusCode.BadRequest, "Bad Request");
                } else {
                    try {
                        string path = splitRequest[1];
						Console.WriteLine("Path: {0}", path);
                        if (!path.StartsWith ("daap://")) {
                            path = String.Format ("daap://localhost{0}", path);
                        }

                        Uri uri = new Uri (path);
                        NameValueCollection query = new NameValueCollection ();

                        if (uri.Query != null && uri.Query != String.Empty) {
                            string[] splitquery = uri.Query.Substring (1).Split ('&');

                            foreach (string queryItem in splitquery) {
                                if (queryItem == String.Empty)
                                    continue;
                                
                                string[] splitQueryItem = queryItem.Split ('=');
                                query[splitQueryItem[0]] = splitQueryItem[1];
                            }
                        }

                        if (authMethod != AuthenticationMethod.None && uri.AbsolutePath == "/login" &&
                            !IsValidAuth (user, password)) {
                            WriteAccessDenied (client);
                            return true;
                        }

                        return handler (client, user, uri.AbsolutePath, query, range);
                    } catch (IOException e) {
                        ret = false;
                        Console.Error.WriteLine("IOException: {0}", e);
                    } catch (Exception e) {
                        ret = false;
                        Console.Error.WriteLine ("Trouble handling request {0}: {1}", splitRequest[1], e);
                    }
                }
            }

            return ret;
        }

        private void HandleConnection (object o) {
            Socket client = (Socket) o;

            try {
                while (HandleRequest (client)) { }
            } catch (IOException e) {
                // ignore
            } catch (Exception e) {
                Console.Error.WriteLine ("Error handling request: " + e);
            } finally {
                clients.Remove (client);
                client.Close ();
            }
        }

        private void ServerLoop () {
            while (true) {
                try {
                    if (!running)
                        break;
                    
                    Socket client = server.Accept ();
                    clients.Add (client);
                    ThreadPool.QueueUserWorkItem (HandleConnection, client);
                } catch (SocketException e) {
                    break;
                }
            }
        }
    }
    /*
    internal class RevisionManager {

        public int Current {
            get { return current; }
        }

        public int HistoryLimit {
            get { return limit; }
            set { limit = value; }
        }
        
        public void AddRevision (List<Database> databases) {
            revisions[++current] = databases;

            if (revisions.Keys.Count > limit) {
                // remove the oldest

                int oldest = current;
                foreach (int rev in revisions.Keys) {
                    if (rev < oldest) {
                        oldest = rev;
                    }
                }

                RemoveRevision (oldest);
            }
        }

        public void RemoveRevision (int rev) {
            revisions.Remove (rev);
        }

        public List<Database> GetRevision (int rev) {
            if (rev == 0)
                return revisions[current];
            else
                return revisions[rev];
        }

        public Database GetDatabase (int rev, int id) {
            List<Database> dbs = GetRevision (rev);

            if (dbs == null)
                return null;
            
            foreach (Database db in dbs) {
                if (db.Id == id)
                    return db;
            }

            return null;
        }
    }*/

    public class TrackRequestedArgs : EventArgs {

        private string user;
        private IPAddress host;
        private Database db;
        private Track track;

        public string UserName {
            get { return user; }
        }

        public IPAddress Host {
            get { return host; }
        }

        public Database Database {
            get { return db; }
        }

        public Track Track {
            get { return track; }
        }
        
        public TrackRequestedArgs (string user, IPAddress host, Database db, Track track) {
            this.user = user;
            this.host = host;
            this.db = db;
            this.track = track;
        }
    }

    public delegate void TrackRequestedHandler (object o, TrackRequestedArgs args);

    public class Server {

        internal static readonly TimeSpan DefaultTimeout = TimeSpan.FromMinutes (30);
        
        private static Regex dbItemsRegex = new Regex ("/databases/([0-9]*?)/items$");
        private static Regex dbTrackRegex = new Regex ("/databases/([0-9]*?)/items/([0-9]*).*");
        private static Regex dbContainersRegex = new Regex ("/databases/([0-9]*?)/containers$");
        private static Regex dbContainerItemsRegex = new Regex ("/databases/([0-9]*?)/containers/([0-9]*?)/items$");
        
        private WebServer ws;
        private XmlRpcServer xmlResponder = new XmlRpcServer();
        private Database theDatabase = new Database("Default");
        private Dictionary<int, User> sessions = new Dictionary<int, User> ();
        private Random random = new Random ();
        private UInt16 port = 3689;
        private ServerInfo serverInfo = new ServerInfo ();
        private bool publish = true;
        private int maxUsers = 0;
        private bool running;

#if !ENABLE_MDNSD
        private Avahi.Client client;
        private EntryGroup eg;
#else
        private RegisterService zc_service;
#endif

        private object eglock = new object ();
        //private RevisionManager revmgr = new RevisionManager ();

        public event EventHandler Collision;
        public event TrackRequestedHandler TrackRequested;
        public event UserHandler UserLogin;
        public event UserHandler UserLogout;

        public IList<User> Users {
            get {
                lock (sessions) {
                    return new ReadOnlyCollection<User> (new List<User> (sessions.Values));
                }
            }
        }

        public string Name {
            get { return serverInfo.Name; }
            set {
                serverInfo.Name = value;
                ws.Realm = value;

                if (publish)
                    RegisterService ();
            }
        }

        public UInt16 Port {
            get { return port; }
            set {
                port = value;
                ws.RequestedPort = value;
            }
        }

        public bool IsPublished {
            get { return publish; }
            set {
                publish = value;

                if (running && publish)
                    RegisterService ();
                else if (running && !publish)
                    UnregisterService ();
            }
        }

        public bool IsRunning {
            get { return running; }
        }

        public AuthenticationMethod AuthenticationMethod {
            get { return serverInfo.AuthenticationMethod; }
            set {
                serverInfo.AuthenticationMethod = value;
                ws.AuthenticationMethod = value;
            }
        }

        public IList<NetworkCredential> Credentials {
            get { return ws.Credentials; }
        }

        public Database Database
        {
            get
            {
                return theDatabase;
            }
            set
            {
                theDatabase = value;
            }
        }

        public int MaxUsers {
            get { return maxUsers; }
            set { maxUsers = value; }
        }

        public Server (string name) {
            ws = new WebServer (port, OnHandleRequest);
            serverInfo.Name = name;
            ws.Realm = name;

            //Default the name of the database to that of the server
            theDatabase.Name = name;

            //*********Add exposure to XML-RPC here****************************
            xmlResponder.Add("Metadata", new Metadata());
        }

        public void Start () {
            running = true;
            ws.Start ();

#if !ENABLE_MDNSD
            client = new Avahi.Client ();
            client.StateChanged += OnClientStateChanged;
#endif

            if (publish)
                RegisterService ();
        }

        public void Stop () {
            running = false;

            ws.Stop ();
            UnregisterService ();
                
            // get that thread to wake up and exit
            //lock (revmgr) {
            //    Monitor.PulseAll (revmgr);
            //}

#if !ENABLE_MDNSD
            if (client != null) {
                client.Dispose ();
                client = null;
            }
#endif
        }

        /*
        public void AddDatabase (Database db) {
            databases.Add (db);
        }

        public void RemoveDatabase (Database db) {
            databases.Remove (db);
        }
         * */

        public void AddCredential (NetworkCredential cred) {
            ws.AddCredential (cred);
        }

        public void RemoveCredential (NetworkCredential cred) {
            ws.RemoveCredential (cred);
        }

        public void Commit () {
            //List<Database> clones = new List<Database> ();
           // foreach (Database db in databases) {
           //     clones.Add ((Database) db.Clone ());
            //}

            //lock (revmgr) {
            //    revmgr.AddRevision (clones);
            //    Monitor.PulseAll (revmgr);
            //}
        }

#if ENABLE_MDNSD
        private void RegisterService () {
            lock (eglock) {
                if (zc_service != null) {
                    UnregisterService ();
                }
                
                string auth = serverInfo.AuthenticationMethod == AuthenticationMethod.None ? "false" : "true";
                
                zc_service = new RegisterService (serverInfo.Name, null, "_daap._tcp");
                zc_service.Port = (short)ws.BoundPort;
                zc_service.TxtRecord = new TxtRecord ();
                zc_service.TxtRecord.Add ("Password", auth);
                zc_service.TxtRecord.Add ("Machine Name", serverInfo.Name);
                zc_service.TxtRecord.Add ("txtvers", "1");
                zc_service.Response += OnRegisterServiceResponse;
                zc_service.AutoRename = false;
                zc_service.RegisterAsync ();
            }
        }
        
        private void UnregisterService () {
            lock (eglock) {
                if (zc_service == null) {
                    return;
                }
                
                try {
                    zc_service.Dispose ();
                } catch {
                }
                zc_service = null;
            }
        }
        
        private void OnRegisterServiceResponse (object o, RegisterServiceEventArgs args) {
            if (args.NameConflict && Collision != null) {
                Collision (this, new EventArgs ());
            }
        }
#else
        private void OnClientStateChanged (object o, ClientStateArgs args) {
            if (publish && args.State == ClientState.Running) {
                RegisterService ();
            }
        }
        
        private void RegisterService () {
            lock (eglock) {
                
                if (eg != null) {
                    eg.Reset ();
                } else {
                    eg = new EntryGroup (client);
                    eg.StateChanged += OnEntryGroupStateChanged;
                }

                try {
                    string auth = serverInfo.AuthenticationMethod == AuthenticationMethod.None ? "false" : "true";
                    eg.AddService (serverInfo.Name, "_daap._tcp", "", ws.BoundPort,
                                   new string[] { "Password=" + auth, "Machine Name=" + serverInfo.Name,
                                                  "txtvers=1" });
                    eg.Commit ();
                } catch (ClientException e) {
                    if (e.ErrorCode == ErrorCode.Collision && Collision != null) {
                        Collision (this, new EventArgs ());
                    } else {
                        throw e;
                    }
                }
            }
        }

        private void UnregisterService () {
            lock (eglock) {
                if (eg == null)
                    return;

                eg.Reset ();
                eg.Dispose ();
                eg = null;
            }
        }

        private void OnEntryGroupStateChanged (object o, EntryGroupStateArgs args) {
            if (args.State == EntryGroupState.Collision && Collision != null) {
                Collision (this, new EventArgs ());
            }
        }
#endif

        private void ExpireSessions () {
            lock (sessions) {
                foreach (int s in new List<int> (sessions.Keys)) {
                    User user = sessions[s];
                    
                    if (DateTime.Now - user.LastActionTime > DefaultTimeout) {
                        sessions.Remove (s);
                        OnUserLogout (user);
                    }
                }
            }
        }

        private void OnUserLogin (User user) {
            UserHandler handler = UserLogin;
            if (handler != null) {
                try {
                    handler (this, new UserArgs (user));
                } catch (Exception e) {
                    Console.Error.WriteLine ("Exception in UserLogin event handler: " + e);
                }
            }
        }

        private void OnUserLogout (User user) {
            UserHandler handler = UserLogout;
            if (handler != null) {
                try {
                    handler (this, new UserArgs (user));
                } catch (Exception e) {
                    Console.Error.WriteLine ("Exception in UserLogout event handler: " + e);
                }
            }
        }

        internal bool OnHandleRequest (Socket client, string username, string path, NameValueCollection query, int range) {
            int session = 0;
            Metadata db = new Metadata(); //create this once for the life of the thread

            if (query["session-id"] != null) {
                session = Int32.Parse (query["session-id"]);
            }
            
            if (!sessions.ContainsKey (session) && path != "/server-info" && path != "/content-codes" &&
                path != "/login") {
                ws.WriteResponse (client, HttpStatusCode.Forbidden, "invalid session id");
                return true;
            }

            if (session != 0) {
                sessions[session].LastActionTime = DateTime.Now;
            }

            int clientRev = 0;
            if (query["revision-number"] != null) {
                clientRev = Int32.Parse (query["revision-number"]);
            }

            int delta = 0;
            if (query["delta"] != null) {
                delta = Int32.Parse (query["delta"]);
            }

            if (path == "/server-info") {
                ws.WriteResponse (client, GetServerInfoNode ());
            } else if (path == "/content-codes") {
                ws.WriteResponse (client, ContentCodeBag.Default.ToNode ());
            } else if (path == "/login") {
                ExpireSessions ();
                
                if (maxUsers > 0 && sessions.Count + 1 > maxUsers) {
                    ws.WriteResponse (client, HttpStatusCode.ServiceUnavailable, "too many users");
                    return true;
                }
                
                session = random.Next ();
                User user = new User (DateTime.Now, (client.RemoteEndPoint as IPEndPoint).Address, username);
                
                lock (sessions) {
                    sessions[session] = user;
                }
                
                ws.WriteResponse (client, GetLoginNode (session));

                OnUserLogin (user);
            } else if (path == "/logout") {
                User user = sessions[session];
                
                lock (sessions) {
                    sessions.Remove (session);
                }
                
                ws.WriteResponse (client, HttpStatusCode.OK, new byte[0]);
                OnUserLogout (user);
                
                return false;
            } else if (path == "/databases") {
                ws.WriteResponse (client, GetDatabasesNode ());
            } 
            //Request for all the tracks (also passes which ones have been deleted)
            else if (dbItemsRegex.IsMatch (path)) {
                int dbid = Int32.Parse (dbItemsRegex.Match (path).Groups[1].Value);

                ArrayList deletedIds = db.GetDeletedIds(clientRev-delta, clientRev);

                ContentNode node = theDatabase.ToTracksNode (query["meta"].Split (','),
                                                      (int[]) deletedIds.ToArray (typeof (int)), clientRev);
                ws.WriteResponse (client, node);
            }
            //request a specific track to stream
            else if (dbTrackRegex.IsMatch (path)) {
                Match match = dbTrackRegex.Match (path);
                int dbid = Int32.Parse (match.Groups[1].Value);
                int trackid = Int32.Parse (match.Groups[2].Value);

                Track track = new Track(db.GetSong(trackid));
                if (track == null) {
                    ws.WriteResponse (client, HttpStatusCode.BadRequest, "invalid track id");
                    return true;
                }

                try {
                    try {
                        if (TrackRequested != null)
                            TrackRequested (this, new TrackRequestedArgs (username,
                                                                        (client.RemoteEndPoint as IPEndPoint).Address,
                                                                        theDatabase, track));
                    } catch {}
                    
                    if (track.FileName != null) {
                        Console.WriteLine("Writing File now");
                        ws.WriteResponseFile (client, track.FileName, range);
                    } else if (theDatabase.Client != null) {
                        Console.WriteLine("Streaming file with theDatabase");
                        long trackLength = 0;
                        Stream trackStream = theDatabase.StreamTrack (track, out trackLength);
                        
                        try {
                            ws.WriteResponseStream (client, trackStream, trackLength);
                        } catch (IOException e) {
                        }
                    } else {
                        ws.WriteResponse (client, HttpStatusCode.InternalServerError, "no file");
                    }
                } finally {
                    client.Close ();
                }
            } 
            //Get a list of all playlists
            //TODO: Make sure this is actually functional
            else if (dbContainersRegex.IsMatch (path)) {
                int dbid = Int32.Parse (dbContainersRegex.Match (path).Groups[1].Value);

                ws.WriteResponse (client, theDatabase.ToPlaylistsNode ());
            } 
            //Get all the songs in a playlist
            else if (dbContainerItemsRegex.IsMatch (path)) {
                Match match = dbContainerItemsRegex.Match (path);
                int dbid = Int32.Parse (match.Groups[1].Value);
                int plid = Int32.Parse (match.Groups[2].Value);

                Playlist curpl = new Playlist(db.GetPlaylist(plid));
                if (curpl == null)
                {
                    ws.WriteResponse(client, HttpStatusCode.BadRequest, "invalid playlist id");
                    return true;
                }
                curpl.TrackMetaHandler = theDatabase.LookupTrackById;

                ArrayList deletedIds = db.GetDeletedIds(clientRev-delta, clientRev);
                    
                ws.WriteResponse (client, curpl.ToTracksNode ((int[]) deletedIds.ToArray (typeof (int))));
            } 
            //Get the current server version number or wait for the version number to change
            else if (path == "/update") {
                int retrev;
                
                // if they have the current revision, wait for a change
                retrev = db.WaitForUpdate(clientRev);
                
                if (!running) {
                    Console.WriteLine("Server has been stopped");
                    ws.WriteResponse (client, HttpStatusCode.NotFound, "server has been stopped");
                } else {
                    Console.WriteLine("Reporting version {0}", retrev);
                    ws.WriteResponse (client, GetUpdateNode (retrev));
                }
            }
            else if (path == "/xmlrpc")
            {
                Console.WriteLine("Processing XML-RPC Request");

                if (!running)
                {
                    ws.WriteResponse(client, HttpStatusCode.NotFound, "Server has been stopped");
                }
                
                string qryString = HttpUtility.UrlDecode(query["request"]);
                
                byte[] xmlByteData = Encoding.ASCII.GetBytes(qryString);
                MemoryStream xmlStream = new MemoryStream(xmlByteData);
                StreamReader xmlReader = new StreamReader(xmlStream);
                XmlRpcContent outputPacket = null;

                //put a lock here since there could potentially be a bunch of
                //threads running this function at once, all of them requesting from
                //the same xml-rpc object, which is not thread safe
                lock (xmlResponder)
                {
                    StringWriter response = xmlResponder.ProcessRequest(xmlReader);

                    outputPacket = new XmlRpcContent(response.ToString());
                }

                ws.WriteResponse(client, outputPacket.ToNode());

            }

            else
            {
                ws.WriteResponse(client, HttpStatusCode.Forbidden, "GO AWAY");
            }

            return true;
        }

        private ContentNode GetLoginNode (int id) {
            return new ContentNode ("dmap.loginresponse",
                                    new ContentNode ("dmap.status", 200),
                                    new ContentNode ("dmap.sessionid", id));
        }

        private ContentNode GetServerInfoNode () {
            return serverInfo.ToNode (1);
        }

        private ContentNode GetDatabasesNode () {
            ArrayList databaseNodes = new ArrayList ();

            /*
            List<Database> dbs = revmgr.GetRevision (revmgr.Current);
            if (dbs != null) {
                foreach (Database db in revmgr.GetRevision (revmgr.Current)) {
                    databaseNodes.Add (db.ToDatabaseNode ());
                }
            }*/
            databaseNodes.Add(theDatabase.ToDatabaseNode());

            ContentNode node = new ContentNode ("daap.serverdatabases",
                                                new ContentNode ("dmap.status", 200),
                                                new ContentNode ("dmap.updatetype", (byte) 0),
                                                new ContentNode ("dmap.specifiedtotalcount", 1),
                                                new ContentNode ("dmap.returnedcount", 1),
                                                new ContentNode ("dmap.listing", databaseNodes));

            return node;
        }

        private ContentNode GetUpdateNode (int revision) {
            return new ContentNode ("dmap.updateresponse",
                                    new ContentNode ("dmap.status", 200),
                                    new ContentNode ("dmap.serverrevision", revision));
        }
    }
}