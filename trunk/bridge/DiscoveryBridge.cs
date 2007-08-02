using DAAP;
using System;
using System.Collections.Generic;
using System.Text;

namespace DMP {
	/// <summary>
	/// An extended version of the Bridge that supports ZeroConf discovery
	/// </summary>
	public class DiscoveryBridge : Bridge {
		/// <summary>
		/// Fires when a new server is found
		/// </summary>
		public event EventHandler<ServerStatusEventArgs> ServerAdded;

		/// <summary>
		/// Fires when a server is lost
		/// </summary>
		public event EventHandler<ServerStatusEventArgs> ServerRemoved;

		private bool myServiceLocatorStarted;

		/// <summary>
		/// Discovers servers
		/// </summary>
		private DAAP.ServiceLocator myServiceLocator;

		/// <summary>
		/// Initializes a new DiscoveryBridge using the defaults
		/// </summary>
		public DiscoveryBridge() {
			this.myServiceLocator = new ServiceLocator();
			lock (this.myServiceLocator) {
				this.myServiceLocator.ShowLocalServices = true;
				this.myServiceLocator.Found += ZeroConfServerFound;
				this.myServiceLocator.Removed += ZeroConfServerLost;
				this.myServiceLocatorStarted = false;
			}
		}

		/// <summary>
		/// Connects to the given server and eventually will get the songs from it
		/// </summary>
		/// <param name="zeroconfName">The Zeroconf name of the server to connect to</param>
		/// <returns>The library id, which is referred to in the db and the 
		/// bridge's dictionary of clients or -1 if the connect fails</returns>
		public int AddServerConnection(string zeroconfName) {
			bool containsKey;
			lock (this.serverNameToIdList) {
				containsKey = this.serverNameToIdList.ContainsKey(zeroconfName);
			}
			if (containsKey) { // Already connected
				return -1;
			}
			Dictionary<string, Service> serverList = this.getZeroconfServerList();
			if (serverList.ContainsKey(zeroconfName)) {
				Service theService = serverList[zeroconfName];
				int result = this.AddServerConnection(theService);
				return result;
			}
			else { // The UI is smoking crack
				return -1;
			}
		}

		/// <summary>
		/// Gets a list of servers that are discoverable at the time using Zeroconf
		/// </summary>
		/// <returns></returns>
		public Dictionary<String, Service> getZeroconfServerList() {
			System.Collections.IEnumerable serverListing;
			lock (this.myServiceLocator) {
				serverListing = this.myServiceLocator.Services;
			}
			Dictionary<String, Service> serverDict = new Dictionary<string, Service>();
			String key;
			String duplicateKey;
			int duplicateCount;
			Service server;
			Console.WriteLine("Listing servers...");
			foreach (System.Collections.DictionaryEntry entry in serverListing) {
				server = (Service)entry.Value;
				key = server.Name;
				Console.WriteLine("Found the server \"" + key + "\".");
				if (serverDict.ContainsKey(key)) {
					duplicateCount = 1;
					do {
						duplicateKey = String.Format("{0} ({1})", key, duplicateCount);
						duplicateCount++;
					}
					while (serverDict.ContainsKey(duplicateKey));
					serverDict.Add(duplicateKey, server);
				}
				else {
					serverDict.Add(key, server);
				}
			}
			Console.WriteLine("Done listing servers.");
			return serverDict;
		}

		/// <summary>
		/// Starts the service locator if it has not been started. Performs service locating
		/// to connect to new servers.
		/// </summary>
		public void StartZeroConf() {
			if (!this.myServiceLocatorStarted) {
				this.myServiceLocatorStarted = true;
				lock (this.myServiceLocator) {
					this.myServiceLocator.Start();
				}
			}
		}

		/// <summary>
		/// Runs when ZeroConf finds a new server.  Adds the server if it's been seen before
		/// </summary>
		/// <param name="o"></param>
		/// <param name="args"></param>
		private void ZeroConfServerFound(object o, DAAP.ServiceArgs args) {
			Service newServer = args.Service;
			Console.WriteLine("ZeroConf found " + newServer.Name);
			int libraryId;
			lock (this.database) {
				libraryId = this.database.getLibraryIdForName(newServer.Name);
			}
			Console.WriteLine("Library ID for " + newServer.Name + " is " + libraryId);
			if (this.ServerAdded != null) {
				Console.WriteLine("Calling the event for adding " + newServer.Name);
				this.ServerAdded(this, new ServerStatusEventArgs(newServer.Name, ServerStatusEventArgs.ServerStatusList.Disconnected));
			}
			if (libraryId > -1) { //Reconnect to this server
				int addResult = this.AddServerConnection(newServer);
			}
		}

		/// <summary>
		/// Runs when ZeroConf notices a server is gone.
		/// </summary>
		/// <param name="o"></param>
		/// <param name="args"></param>
		private void ZeroConfServerLost(object o, DAAP.ServiceArgs args) {
			Service oldServer = args.Service;
			bool containsKey;
			lock (this.serverNameToIdList) {
				containsKey = this.serverNameToIdList.ContainsKey(oldServer.Name);
			}
			if (containsKey) {
				// It was connected, drop it
				int libraryId;
				lock (this.serverNameToIdList) {
					libraryId = this.serverNameToIdList[oldServer.Name];
				}
				lock (this.clientList) {
					if (this.clientList.ContainsKey(libraryId)) {
						this.clientList.Remove(libraryId);
					}
				}
				lock (this.serverNameToIdList) {
					this.serverNameToIdList.Remove(oldServer.Name);
				}
				if (this.ServerRemoved != null) {
					this.ServerRemoved(this, new ServerStatusEventArgs(oldServer.Name, ServerStatusEventArgs.ServerStatusList.Connected));
				}
				LinkedList<Int64> oldSongs;
				lock (this.database) {
					oldSongs = this.database.getSongsFromServer(libraryId);
				}
				this.FireSongListChangedEvent(false, oldSongs);
			}
			else {
				if (this.ServerRemoved != null) {
					this.ServerRemoved(this, new ServerStatusEventArgs(oldServer.Name, ServerStatusEventArgs.ServerStatusList.Disconnected));
				}
			}
		}
	}
}
