//Justin Tulloss
//01/15/2007
//
//Implements a network layer for the DMP server

#define TESTINGRPC

#region Using Directives
using System;
using System.IO;
using System.Collections;
using System.Diagnostics;
using DMP.Server.Properties;
using DMP;
using DMP.Server;
using DMP.Data;
using DAAP;
#endregion

namespace DMP.Server
{
	public class ServerObject
	{
        //The actual DAAP server that does all the work
        private static DAAP.Server streamer;
        
		//Placeholder for when the port is not constant
		public static int Port	
		{
			get
			{
				Metadata database = new Metadata();
				return database.ServerPort;
			}
            set
            {
				if (value != streamer.Port)
				{
					Metadata database = new Metadata();
					database.ServerPort = value;
					streamer.Port = (ushort)value;

					//restart server on new port
					streamer.Stop();
					streamer.Start();
				}
            }
		}

        public static string Name
        {
            get
            {
				Metadata database = new Metadata();
				return database.ServerName;
            }
            set
            {
				Metadata database = new Metadata();
				database.ServerName = value;
				streamer.Name = value;
            }
        }

        public static ArrayList Directories
        {
            get
            {
                Metadata database = new Metadata();
                return database.ListDirectories();
            }
        }

		public ServerObject()
		{
			Metadata database = new Metadata();

            string serverName = database.ServerName;
            string databaseName = serverName;

            //Load preferences

            //Initialize DAAP
            streamer = new DAAP.Server(serverName);
            streamer.Port = (ushort)Port;
            Console.WriteLine("Starting Server '{0}' on Port {1}", streamer.Name, streamer.Port);
            streamer.Database.Name=databaseName;
            streamer.Commit();
		}
		/// <summary>Simple logging to Console.</summary>
		static public void WriteEntry(String msg, EventLogEntryType type)
		{
			if (type != EventLogEntryType.Information) // ignore debug msgs
			Console.WriteLine("{0}: {1}", type, msg);
		}

        public void StopServer()
        {
            streamer.Stop();
        }

        public void StartServer()
        {
            streamer.Start();
        }

        public static void SaveSettings()
        {
            Settings.Default.Save();
        }

        public static Error AddDirectory(string path)
        {
            Metadata theData = new Metadata();
            return theData.AddDirectory(path);
        }

        public static void UpdateMusic(object o)
        {
            Metadata theData = new Metadata();
            theData.UpdateMusic();
        }
    }
}

