using DAAP;
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.IO;
using System.Text;
using DMP.Data;

namespace DMP
{
    /// <summary>
	/// Represents the intermediary layer between the client (player) and the server.
	/// </summary>
	public class Bridge
	{
		/// <summary>
		/// Fires when a server is connected or disconnected
		/// </summary>
		public event EventHandler<ServerStatusEventArgs> ServerStatusChanged;

		/// <summary>
		/// Fires when the list of songs is changed
		/// </summary>
		public event EventHandler<SongListChangedEventArgs> SongListChanged;

		/// <summary>
		/// The dictionary of DAAP clients, since I believe each instance only connects to one server
		/// The int key corresponds to the library ID in the Bridge Database
		/// </summary>
		protected System.Collections.Generic.Dictionary<int, Client> clientList;

		/// <summary>
		/// This dictionary maps a server name to the library ID found in the Bridge Database
		/// </summary>
		protected System.Collections.Generic.Dictionary<string, int> serverNameToIdList;

        protected BridgeDatabase database;

		/// <summary>
		/// Initializes a new Bridge using the defaults
		/// </summary>
		public Bridge() {
            clientList = new Dictionary<int, Client>();
			this.serverNameToIdList = new Dictionary<string, int>();
            database = new BridgeDatabase();
		}

        public void addPlaylists(List<PlaylistBase> thePlaylists)
        {
            this.database.addPlaylists(thePlaylists);
        }

        public void addPlaylist(PlaylistBase thePlaylist)
        {
            this.database.addPlaylist(thePlaylist);
        }

        public PlaylistBase loadPlaylist(int thePlaylistId)
        {
            return this.database.loadPlaylist(thePlaylistId);
        }

		/// <summary>
		/// Connects to the given server and eventually will get the songs from it
		/// </summary>
		/// <param name="theHostName">The host name, in some form that can be resolved</param>
		/// <param name="thePort">The port number, the default is currently 3689</param>
		/// <returns>The library id, which is referred to in the db and the 
		/// bridge's dictionary of clients or -1 if the connect fails</returns>
        public int AddServerConnection(string theHostName, ushort thePort){
			try {
				Client newClient = new Client(theHostName, thePort);
				return this.LoginAndSaveToDatabase(newClient);
			}
			catch {
				return -1;
			}
		}
		/// <summary>
		/// Connects to the given server and eventually will get the songs from it
		/// </summary>
		/// <param name="theService">The serivce found with ZeroConf to connect to</param>
		/// <returns>The library id, which is referred to in the db and the 
		/// bridge's dictionary of clients or -1 if the connect fails</returns>
		public int AddServerConnection(Service theService) {
			bool containsKey;
			lock(this.serverNameToIdList){
				containsKey = this.serverNameToIdList.ContainsKey(theService.Name);
			}
			if (containsKey) { // Already connected
				return -1;
			}
			try {
				Client newClient = new Client(theService);
				return this.LoginAndSaveToDatabase(newClient);
			}
			catch {
				return -1;
			}
		}

		/// <summary>
		/// Used my subclasses to fire a SongListChanged event when it is needed
		/// </summary>
		protected void FireSongListChangedEvent(bool added, LinkedList<Int64> theDelta) {
			if (this.SongListChanged != null) {
				DataTable newSongs = this.getAvailableSongsInCollection();
				this.SongListChanged(this, new SongListChangedEventArgs(newSongs, 
					added, theDelta));
			}
		}

		/// <summary>
		/// Gets the list of all the songs in the collection that are on available servers
		/// </summary>
		/// <returns>A DataTable with the following columns:
		/// id, libraryId, artist, album, title</returns>
		public DataTable getAvailableSongsInCollection() {
			int[] libraries;
			lock (this.clientList) {
				libraries = new int[this.clientList.Count];
			}
			int libraryCount = 0;
			lock (this.clientList) {
				foreach (int key in this.clientList.Keys) {
					libraries[libraryCount] = key;
					libraryCount++;
				}
			}
			DataTable theTable;
			lock (this.database) {
				theTable = this.database.getAvailableSongsInCollection(libraries);
			}
			return theTable;
		}

		/// <summary>
		/// Gets the list of all the songs in the collection
		/// </summary>
		/// <returns>A DataTable with the following columns:
		/// id, libraryId, artist, album, title</returns>
		public DataTable getSongsInCollection()
		{
			DataTable theTable;
			lock (this.database) {
				theTable = this.database.getSongsInCollection();
			}
			return theTable;
		}

        /// <summary>
        /// Gets a stream of a requested song
        /// </summary>
        /// <param name="id">The id of the requested song</param>
        /// <returns>A stream of the requested song</returns>
        public Stream getSongStream(int id, out long length)
        {
			int libraryId;
			lock (this.database) {
				libraryId = this.database.getRemoteLibraryId(id);
			}
            //int remoteSongId = this.db.getRemoteSongId(id);
			long songSize;
			lock (this.database) {
				songSize = this.database.getRemoteSongSize(id);
			}

            //Track song = clientList[libraryId].Database.LookupTrackById(remoteSongId);
			Track song;
			lock (this.database) {
				song = database.getRemoteTrack(id);
			}
			Stream musicStream;
			lock (this.clientList) {
				lock (this.database) {
					musicStream = clientList[libraryId].Database.StreamTrack(song, out length);
				}
			}
			return musicStream;
            //return null;
        }

		/// <summary>
		/// Gets the track information for the specified track id.
		/// </summary>
		/// <param name="id">The id of the requested song.</param>
		/// <returns>the Track object containing the track information</returns>
		public Track getTrackInfo(int id)
		{
			Track theTrack;
			lock (this.database) {
				theTrack = database.getRemoteTrack(id);
			}
			return theTrack;
		}

        public String getSongURL(int id)
        {
            /*
            
            int remoteSongId = this.db.getRemoteSongId(id);
            String remoteSongFormat = this.db.getRemoteSongFormat(id);
             * */
			int libraryId;
			Track playTrack;
			lock (this.database) {
				libraryId = this.database.getRemoteLibraryId(id);
				playTrack = database.getRemoteTrack(id);
			}
			UriBuilder playbackUri;
			lock (this.clientList) {
					playbackUri = clientList[libraryId].Database.StreamTrackURI(playTrack);
			}
            return playbackUri.ToString();
        }


        /*
         * Eventually will include logic for time stamps. For new libraries, last seen 
         * and updated is 0 so the same function will work with all situations.
         */
		/*
        private void updateSongsForLibrary( Client client, BridgeDatabase.Library lib )
        {
            List<BridgeDatabase.Song> songs = new List<BridgeDatabase.Song>();
            foreach (Track track in client.Databases[0].Tracks)
            {
                BridgeDatabase.Song s = new BridgeDatabase.Song();
                s.artist = track.Artist;
                s.album = track.Album;
                s.title = track.Title;
                songs.Add(s);
            }

            this.db.addSongs(songs);
        }*/

        public bool isDatabaseUp()
        {
			bool theDatabaseIsUp;
			lock(this.database){
				theDatabaseIsUp = this.database.isDatabaseUp();
			}
            return theDatabaseIsUp ;
        }

		/// <summary>
		/// Attempts to log in and store the connection info in the database
		/// </summary>
		/// <param name="newClient">The client to log in to</param>
		/// <returns>-1 on failure, the library ID on success</returns>
		private int LoginAndSaveToDatabase(Client newClient) {
			try {
				lock (this.clientList) {
					if (!clientList.ContainsKey(newClient.Id)) {
						Console.WriteLine("Added libraryid to client list: " + newClient.Id);
						this.clientList.Add(newClient.Id, newClient);
						lock (this.serverNameToIdList) {
							this.serverNameToIdList.Add(newClient.Name, newClient.Id);
						}
					}
					else {
						Console.WriteLine("Following libraryId already in clientlist: " + newClient.Id);
					}
				}
				newClient.Login(); // Passwords are for wimps
				Console.WriteLine("Connected to " + newClient.Name);


				if (this.ServerStatusChanged != null) {
					this.ServerStatusChanged(this, new ServerStatusEventArgs(newClient.Name, ServerStatusEventArgs.ServerStatusList.Connected ));
				}

				if (this.SongListChanged != null) {
					LinkedList<Int64> newSongs;
					lock (this.database) {
						newSongs = this.database.getSongsFromServer(newClient.Id);
					}
					this.FireSongListChangedEvent(true, newSongs);
				}

				return newClient.Id;
			}
			catch (DAAP.LoginException ex) {
				Console.WriteLine("Bridge: " + ex.Message);
				return -1;
			}
		}

		/// <summary>
		/// Disconnects from the given server
		/// </summary>
		/// <param name="libraryId">The library ID to disconnect from</param>
		/// <returns></returns>
		private bool RemoveServerConnection(int libraryId) {
			bool containsKey;
			lock (this.clientList) {
				containsKey = (this.clientList.ContainsKey(libraryId));
			}
			if (containsKey) {
				Client oldClient;
				lock (this.clientList) {
					oldClient = this.clientList[libraryId];
				}
				oldClient.Logout();
				lock (this.clientList) {
					this.clientList.Remove(libraryId);
				}
				LinkedList<Int64> oldSongs;
				lock (this.database) {
					oldSongs = this.database.getSongsFromServer(libraryId);
					this.database.RemoveServer(libraryId);
				}
				if (this.ServerStatusChanged != null) {
					this.ServerStatusChanged(this, new ServerStatusEventArgs(oldClient.Name, ServerStatusEventArgs.ServerStatusList.Disconnected));
				}
				if (this.SongListChanged != null) {
					this.FireSongListChangedEvent(false, oldSongs);
				}
				return true;
			}
			else {
				return false;
			}
		}

		/// <summary>
		/// Disconnects from the given server
		/// </summary>
		/// <param name="zeroconfName">The serivce found with ZeroConf to disconnect from</param>
		/// <returns>True if it worked, false otherwise</returns>
		public bool RemoveServerConnection(string zeroconfName) {
			bool containsKey;
			lock(this.serverNameToIdList){
				containsKey = this.serverNameToIdList.ContainsKey(zeroconfName);
			}
			if (containsKey) {
				int libraryId;
				lock (this.serverNameToIdList) {
					libraryId = this.serverNameToIdList[zeroconfName];
					serverNameToIdList.Remove(zeroconfName);
				}
				bool result = this.RemoveServerConnection(libraryId);
				return result;
			}
			else {
				return false;
			}
		}

	}

}
