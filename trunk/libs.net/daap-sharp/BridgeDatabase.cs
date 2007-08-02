/*
 * Lunardini with borrowed code from metadata.cs by Smith
 */

using DMP.Data;
using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using System.Data;
using System.Data.Common;
using System.Data.SQLite;

namespace DAAP
{
    public class BridgeDatabase
    {
        private SQLiteConnection databaseConnection;
        private static System.IO.StreamWriter logFile=null; //same logfile for every instance

        public BridgeDatabase()
        {
            if (logFile == null)
                logFile = System.IO.File.CreateText("dblog.txt");
            logFile.WriteLine("============================");
            logFile.Flush();
            initializeDB(System.IO.Directory.GetCurrentDirectory()+"/bridgeDB.db3");
            InitSQLCommands();
        }

        /*
         * Initializes the bridge database connection.
         * 
         * If database already exists, uses that one, else construct the database.
         */
        private bool initializeDB(string path)
        {
            path = System.IO.Path.GetFullPath(path);
            string directory = System.IO.Path.GetDirectoryName(path);
            if (!System.IO.Directory.Exists(directory))
                return false;
            
            this.databaseConnection = new SQLiteConnection("Data Source=" + path);
            if (this.databaseConnection == null)
            {
                logFile.WriteLine("Database connection failed");
                logFile.Flush();
                return false;
            }
            else
            {
                logFile.WriteLine("Database connection succeded");
                logFile.Flush();
            }

            if (System.IO.File.Exists(path))
            {
                logFile.WriteLine("Init queries");
                logFile.Flush();
                this.initializeQueries();
            }
            else
            {
                logFile.WriteLine("Setting up schema");
                logFile.Flush();
                this.setupSchema();
            }
            logFile.WriteLine("Done with DB init");
            logFile.Flush();
            return true;
        }

        private bool setupSchema()
        {
            if ( this.databaseConnection == null )
                return false;

            IDbCommand librariesTable = this.databaseConnection.CreateCommand();
            librariesTable.CommandText = @"CREATE TABLE libraries (
                id integer primary key autoincrement,
                address text,
                port integer,
                name text,
                username text,
                password text,
                lastSync integer,
                lastSeen integer )";

            IDbCommand songsTable = this.databaseConnection.CreateCommand();
            songsTable.CommandText = @"CREATE TABLE songs (
                id integer primary key autoincrement,
                libraryId integer,
                remoteSongId integer,
                artist text,
                album text,
                title text,
                year text,
                format text,
                duration text,
                genre text,
                tracknumber text,
                trackcount text,
                size integer,
                lastUpdated integer)";

            IDbCommand playlistsTable = this.databaseConnection.CreateCommand();
            playlistsTable.CommandText = @"CREATE TABLE playlistProperties (
                playlistId integer primary key autoincrement,
                playlistName text,
				modifiedTime int)";

			string playlistItemsText = @"CREATE TABLE playlistItems (
				playlistItemId integer primary key autoincrement,
				playlistId integer,
				songId integer,
				playlistOrder integer)";
			SQLiteCommand playlistItemsTable = new
				SQLiteCommand(playlistItemsText, this.databaseConnection);

            this.databaseConnection.Open();
            librariesTable.ExecuteNonQuery();
            songsTable.ExecuteNonQuery();
            playlistsTable.ExecuteNonQuery();
			playlistItemsTable.ExecuteNonQuery();
            this.databaseConnection.Close();

            return true;
        }

        private void initializeQueries()
        {
            // will do later
            /*insertSong = this.databaseConnection.CreateCommand();*/

        }

        /// <summary>
        /// Takes a client and puts the necessary information into db
        /// </summary>
        /// <param name="theClient">the client to add</param>
        /// <returns></returns>
        public void addLibrary( Client theClient )
        {
            logFile.WriteLine("adding " + theClient.Address + " to libraries"); logFile.Flush();
            IDbCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = @"INSERT INTO libraries 
                                  (address, port, name, username, password ) values (?, ?, ?, ?, ?);
                                  SELECT last_insert_rowid();";
            IDataParameter clientAddress = command.CreateParameter();
            command.Parameters.Add(clientAddress);
            IDataParameter clientPort = command.CreateParameter();
            command.Parameters.Add(clientPort);
            IDataParameter clientName = command.CreateParameter();
            command.Parameters.Add(clientName);
            IDataParameter clientUsername = command.CreateParameter();
            command.Parameters.Add(clientUsername);
            IDataParameter clientPassword = command.CreateParameter();
            command.Parameters.Add(clientPassword);

            clientName.Value = theClient.Name;
            clientUsername.Value = theClient.Username;
            clientPassword.Value = theClient.Password;
            clientAddress.Value = theClient.Address;
            clientPort.Value = theClient.Port;
            
            //IDbCommand command2 = this.databaseConnection.CreateCommand();
            //command2.CommandText = "select id from libraries where address=\"" + theClient.Address + 
            //                       "\" and port=\"" + theClient.Port + "\" and name=\"" + theClient.Name + "\"";
            this.databaseConnection.Open();
            int libId = Int32.Parse(command.ExecuteScalar().ToString());
            //int libId = Int16.Parse( command2.ExecuteScalar().ToString() );
            this.databaseConnection.Close();

            logFile.WriteLine("library will have id " + libId ); logFile.Flush();
            theClient.Id = libId;
            //return lib;
        }
		/// <summary>
		/// Adds songs from the given list into the Bridge's database
		/// </summary>
		/// <param name="songs">A list of songs</param>
		/// <param name="libraryID">The library ID to associate with these songs</param>
		public void addSongs(IList<TrackBase> songs, int libraryID) {
			
			this.databaseConnection.Open();
            IDbTransaction insertTrans = databaseConnection.BeginTransaction();

			//logFile.WriteLine("adding " + s.title + " to songs"); logFile.Flush();
			foreach (TrackBase song in songs)
            {
                if(SongExists(libraryID, song.Id)) {
                    updateSongLibraryId.Value = libraryID;
                    updateSongRemoteSongId.Value = song.Id;
                    updateSongArtist.Value = song.Artist;
                    updateSongAlbum.Value = song.Album;
                    updateSongTitle.Value = song.Title;
                    updateSongYear.Value = song.Year;
                    updateSongFormat.Value = song.Format;
                    updateSongDuration.Value = song.Duration.TotalMilliseconds;
                    updateSongGenre.Value = song.Genre;
                    updateSongTrackNumber.Value = song.TrackNumber;
                    updateSongTrackCount.Value = song.TrackCount;
                    updateSongSize.Value = song.Size;
                    updateSongLastUpdatedInfo.Value = song.DateModified;

                    updateSong.ExecuteNonQuery();
                }
                else {
                    insertSongLibraryId.Value = libraryID;
                    insertSongRemoteSongId.Value = song.Id;
                    insertSongArtist.Value = song.Artist;
                    insertSongAlbum.Value = song.Album;
                    insertSongTitle.Value = song.Title;
                    insertSongYear.Value = song.Year;
                    insertSongFormat.Value = song.Format;
                    insertSongDuration.Value = song.Duration.TotalMilliseconds;
                    insertSongGenre.Value = song.Genre;
                    insertSongTrackNumber.Value = song.TrackNumber;
                    insertSongTrackCount.Value = song.TrackCount;
                    insertSongSize.Value = song.Size;
                    insertSongLastUpdatedInfo.Value = song.DateModified;

				    insertSong.ExecuteNonQuery();
                }
			}

            insertTrans.Commit();
			this.databaseConnection.Close();
		}

		/// <summary>
		/// Gets the list of all the songs in the collection
		/// </summary>
		/// <param name="libraries">A list of the library id's to get the songs from</param>
		/// <returns>A DataTable with the following columns:
		/// id, libraryId, artist, album, title</returns>
		public DataTable getAvailableSongsInCollection(int[] libraries) {
			StringBuilder commandText = new StringBuilder("SELECT * FROM songs WHERE ");
			if (libraries.Length == 0) {
				commandText.Append("libraryId = -1");
			}
			else {
				commandText.AppendFormat("libraryId = {0}", libraries[0]);
				for (int i = 1; i < libraries.Length; i++) {
					commandText.AppendFormat(" OR libraryId = {0}", libraries[i]);
				}
			}
			SQLiteDataAdapter adapter = new SQLiteDataAdapter(commandText.ToString(), 
				this.databaseConnection);
			DataTable theTable = new DataTable();
			this.databaseConnection.Open();
			adapter.Fill(theTable);
			this.databaseConnection.Close();

			return theTable;
		}

		/// <summary>
		/// Finds the library ID matching the name, if one exists
		/// </summary>
		/// <param name="libName">The name of the server to find an ID for</param>
		/// <returns>The libary ID if it's in the database, -1 otherwise</returns>
		public int getLibraryIdForName(string libName) {
			string commandText = "SELECT id FROM libraries WHERE name = @name";
			SQLiteCommand command = new SQLiteCommand(commandText, this.databaseConnection);
			command.Parameters.Add("name", DbType.String).Value = libName;
			
			long longLibId = -1;

			databaseConnection.Open();
//			try{
				object scalar = command.ExecuteScalar();
				if (scalar != null) {
					longLibId = (long)scalar;
				}
			//} 
			//catch {}
			//finally {
			databaseConnection.Close();
			//}
			int libId = (int)longLibId;
			return libId;
		}

		/// <summary>
		/// Returns a list of distinct libraries that the bridge has connected to before
		/// </summary>
		/// <returns></returns>
		public DataTable getServersInCollection() {
			string commandText = "SELECT id, name FROM libraries";
			SQLiteDataAdapter adapter = new SQLiteDataAdapter(commandText, this.databaseConnection);
			DataTable theTable = new DataTable();
			this.databaseConnection.Open();
			adapter.Fill(theTable);
			this.databaseConnection.Close();

			return theTable;
		}

		/// <summary>
		/// Gets the list of all the songs in the collection
		/// </summary>
		/// <returns>A DataTable with the following columns:
		/// id, libraryId, artist, album, title</returns>
		public DataTable getSongsInCollection() {
			IDbCommand command = this.databaseConnection.CreateCommand();
			string commandText = "SELECT * FROM songs";
			SQLiteDataAdapter adapter = new SQLiteDataAdapter(commandText, this.databaseConnection);
			DataTable theTable = new DataTable();
			this.databaseConnection.Open();
			adapter.Fill(theTable);
			this.databaseConnection.Close();
			
			return theTable;
		}

		/// <summary>
		/// Gets a list of song ID's from the given server
		/// </summary>
		/// <param name="libraryId">The library ID for the server to get the songs from</param>
		/// <returns></returns>
		public LinkedList<Int64> getSongsFromServer(int libraryId) {
			String commandText = "SELECT id FROM songs WHERE libraryId = @libraryId";
			SQLiteCommand command = new SQLiteCommand(commandText, this.databaseConnection);
			command.Parameters.Add("libraryId", DbType.Int32).Value = libraryId;
			SQLiteDataAdapter adapter = new SQLiteDataAdapter(command);
			DataTable theTable = new DataTable();
			adapter.Fill(theTable);
			LinkedList<Int64> theSongs = new LinkedList<Int64>();
			Int64 songId;
			foreach (DataRow row in theTable.Rows) {
				songId = (Int64)(row[0]);
				theSongs.AddLast(songId);
			}
			return theSongs;
		}

        /// <summary>
        /// Retrieves the library ID from the database based on the global ID of a song
        /// </summary>
        /// <param name="id">The global ID of a song</param>
        /// <returns>The ID of the library the song is located in</returns>
        public int getRemoteLibraryId (int id)
        {
            SQLiteCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = "SELECT libraryId FROM Songs WHERE id=($1)";
            SQLiteParameter param = command.CreateParameter();
            param.ParameterName = "$1";
            param.Value = id.ToString();
            command.Parameters.Add(param);
            this.databaseConnection.Open();
            SQLiteDataReader result = command.ExecuteReader();
            result.Read();
            int ret = result.GetInt32(0);
            this.databaseConnection.Close();
            return ret;
        }

        /// <summary>
        /// Gets the id of a library based on its name
        /// </summary>
        /// <param name="name"></param>
        /// <returns>-1 if the server does not exist, the library name otherwise</returns>
        public int getRemoteLibraryId(string name)
        {
            databaseConnection.Open();
            IDbCommand command = databaseConnection.CreateCommand();
            command.CommandText = "SELECT COUNT(*) FROM libraries WHERE name=\"" + name + "\"";
            IDataReader reader = command.ExecuteReader();
            reader.Read();
            int count = reader.GetInt32(0);
            reader.Dispose();
            if (count == 0)
            {
                databaseConnection.Close();
                return -1;
            }

            command.CommandText = "SELECT id FROM libraries WHERE name=\"" + name + "\"";
            reader = command.ExecuteReader();
            reader.Read();
            int libid = reader.GetInt32(0);
            reader.Dispose();
            databaseConnection.Close();

            return libid;
        }


        /// <summary>
        /// Retrieves a Track class for a global id. The id contained within
        /// the track is a remote song id
        /// </summary>
        /// <param name="id">Global id</param>
        /// <returns>Track instance filled with tags</returns>
        public Track getRemoteTrack(int id)
        {
            Track retTrack = null;
            IDbCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = "SELECT * FROM songs WHERE id= " + id;

            databaseConnection.Open();
            IDataReader sqlResult = command.ExecuteReader();
            if (sqlResult.Read())
            {
                retTrack = new Track();

                //Fill everything in
                if (!sqlResult.IsDBNull(2))
                    retTrack.SetId(sqlResult.GetInt32(2));
                if (!sqlResult.IsDBNull(3))
                    retTrack.Artist = sqlResult.GetString(3);
                if (!sqlResult.IsDBNull(4))
                    retTrack.Album = sqlResult.GetString(3);
                if (!sqlResult.IsDBNull(5))
                    retTrack.Title = sqlResult.GetString(5);
                if (!sqlResult.IsDBNull(6))
                    retTrack.Year = Int32.Parse(sqlResult.GetString(6));
                if (!sqlResult.IsDBNull(7))
                    retTrack.Format = sqlResult.GetString(7);
                //if (!sqlResult.IsDBNull(8))
                    //retTrack.Duration = new TimeSpan(0, 0, 0, 0, Int32.Parse(sqlResult.GetString(8)));
                if (!sqlResult.IsDBNull(9))
                    retTrack.Genre = sqlResult.GetString(9);
                if (!sqlResult.IsDBNull(10))
                    retTrack.TrackNumber = Int32.Parse(sqlResult.GetString(10));
                if (!sqlResult.IsDBNull(11))
                    retTrack.TrackCount = Int32.Parse(sqlResult.GetString(11));
                if (!sqlResult.IsDBNull(12))
                    retTrack.Size = sqlResult.GetInt32(12);

            }

            //clean up
            sqlResult.Dispose();
            command.Dispose();
            databaseConnection.Close();

            return retTrack;
        }

        /// <summary>
        /// Retrieves the remote song ID from the database based on the global ID of a song
        /// </summary>
        /// <param name="id">The global ID of a song</param>
        /// <returns>The remote ID of the song</returns>
        public int getRemoteSongId(int id)
        {
            SQLiteCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = "SELECT remoteSongId FROM Songs WHERE id=($1)";
            SQLiteParameter param = command.CreateParameter();
            param.ParameterName = "$1";
            param.Value = id.ToString();
            command.Parameters.Add(param);
            this.databaseConnection.Open();
            SQLiteDataReader result = command.ExecuteReader();
            result.Read();
            int ret = result.GetInt32(0);
            this.databaseConnection.Close();
            return ret;
        }

        /// <summary>
        /// Retrieves te size of a song from the database based on the global ID of the song
        /// </summary>
        /// <param name="id">The global ID of a song</param>
        /// <returns>The size of the song</returns>
        public long getRemoteSongSize(int id)
        {
            SQLiteCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = "SELECT size FROM Songs WHERE id=($1)";
            SQLiteParameter param = command.CreateParameter();
            param.ParameterName = "$1";
            param.Value = id.ToString();
            command.Parameters.Add(param);
            this.databaseConnection.Open();
            SQLiteDataReader result = command.ExecuteReader();
            result.Read();
            //should we be storing this as a long?
            int ret = result.GetInt32(0);
            this.databaseConnection.Close();
            return ret;
        }

        public String getRemoteSongFormat(int id)
        {
            SQLiteCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = "SELECT format FROM Songs WHERE id=($1)";
            SQLiteParameter param = command.CreateParameter();
            param.ParameterName = "$1";
            param.Value = id.ToString();
            command.Parameters.Add(param);
            this.databaseConnection.Open();
            SQLiteDataReader result = command.ExecuteReader();
            result.Read();
            String ret = result.GetString(0);
            this.databaseConnection.Close();
            return ret;
        }

        public bool isDatabaseUp()
        {
            if (this.databaseConnection == null)
                return false;
            return true;
        }

		/// <summary>
		/// Removes the given server and all songs from it from the database.
		/// </summary>
		/// <param name="libraryId">The library ID of the server to remove</param>
		public void RemoveServer(int libraryId) {
			string songCommandString = "DELETE FROM songs WHERE libraryId = @libraryId";
			SQLiteCommand songCommand = new SQLiteCommand(songCommandString, this.databaseConnection);
			songCommand.Parameters.Add("libraryId", DbType.Int32).Value = libraryId;

			string libraryCommandString = "DELETE FROM libraries WHERE id = @id";
			SQLiteCommand libraryCommand = new SQLiteCommand(libraryCommandString, this.databaseConnection);
			libraryCommand.Parameters.Add("id", DbType.Int32).Value = libraryId;

			this.databaseConnection.Open();
			songCommand.ExecuteNonQuery();
			libraryCommand.ExecuteNonQuery();
			this.databaseConnection.Close();
		}

        public void removeSongs(List<int> deletedIds)
        {
            throw new Exception("The method or operation is not implemented.");
        }

        public void addPlaylists(List<PlaylistBase> thePlaylists)
        {
            List<IDbCommand> commandList = new List<IDbCommand>();
            foreach (PlaylistBase thePlaylist in thePlaylists)
            {
                foreach (Int32 Song in thePlaylist.Songs)
                {
                    IDbCommand command = this.databaseConnection.CreateCommand();
                    command.CommandText = @"INSERT INTO playlists 
                                      (songId, playlistId, playlistName) values (?, ?, ?);
                                      SELECT last_insert_rowid();";
                    IDataParameter songId = command.CreateParameter();
                    songId.Value = Song.ToString();
                    command.Parameters.Add(songId);
                    IDataParameter playlistId = command.CreateParameter();
                    playlistId.Value = thePlaylist.Id.ToString();
                    command.Parameters.Add(playlistId);
                    IDataParameter playlistName = command.CreateParameter();
                    playlistName.Value = thePlaylist.Name;
                    command.Parameters.Add(playlistName);
                    commandList.Add(command);
                }
            }
            this.databaseConnection.Open();
            foreach (IDbCommand command in commandList)
            {
                command.ExecuteNonQuery();
            }
            this.databaseConnection.Close();
        }

        public PlaylistBase loadPlaylist(int thePlaylistId)
        {
            PlaylistBase thePlaylist = new PlaylistBase(thePlaylistId);
            IDbCommand command = this.databaseConnection.CreateCommand();
            command.CommandText = @"SELECT songId FROM playlists WHERE playlistId=($1)";
            IDataParameter playlistId = command.CreateParameter();
            playlistId.ParameterName = "$1";
            playlistId.Value = thePlaylistId.ToString();
            command.Parameters.Add(playlistId);
            this.databaseConnection.Open();
            SQLiteDataReader result = (SQLiteDataReader)command.ExecuteReader();
            while(result.Read())
            {
                Int32 ret = result.GetInt32(0);
                thePlaylist.AddTrack(ret);
            }
            this.databaseConnection.Close();
            return thePlaylist;
        }

        public void addPlaylist(PlaylistBase thePlaylist)
        {
            List<PlaylistBase> theList = new List<PlaylistBase>();
            theList.Add(thePlaylist);
            addPlaylists(theList);
        }




        //DB Commands
        private IDbCommand insertSong;
        private IDbCommand updateSong;

        //Data parameters for insertSong and updateSong commands
        private IDataParameter insertSongLibraryId;
        private IDataParameter insertSongRemoteSongId;
        private IDataParameter insertSongArtist;
        private IDataParameter insertSongAlbum;
        private IDataParameter insertSongTitle;
        private IDataParameter insertSongYear;
        private IDataParameter insertSongFormat;
        private IDataParameter insertSongDuration;
        private IDataParameter insertSongGenre;
        private IDataParameter insertSongTrackNumber;
        private IDataParameter insertSongTrackCount;
        private IDataParameter insertSongSize;
        private IDataParameter insertSongLastUpdatedInfo;

        private IDataParameter updateSongLibraryId;
        private IDataParameter updateSongRemoteSongId;
        private IDataParameter updateSongArtist;
        private IDataParameter updateSongAlbum;
        private IDataParameter updateSongTitle;
        private IDataParameter updateSongYear;
        private IDataParameter updateSongFormat;
        private IDataParameter updateSongDuration;
        private IDataParameter updateSongGenre;
        private IDataParameter updateSongTrackNumber;
        private IDataParameter updateSongTrackCount;
        private IDataParameter updateSongSize;
        private IDataParameter updateSongLastUpdatedInfo;

        //Parameters to determine whether a song is already in the bridge db or not
        private IDbCommand songExists;
        private IDataParameter existsLibraryId;
        private IDataParameter existsSongId;

        private void InitSQLCommands()
        {
            insertSong = databaseConnection.CreateCommand();
            insertSong.CommandText = @"INSERT INTO songs(libraryId, remoteSongId, artist, album, title, year, format, duration,
                                        genre, tracknumber, trackcount, size, lastUpdated) 
                                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)";


            //Create and add parameters for inserting songs
            insertSongLibraryId = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongLibraryId);
            insertSongRemoteSongId = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongRemoteSongId);
            insertSongArtist = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongArtist);
            insertSongAlbum = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongAlbum);
            insertSongTitle = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongTitle);
            insertSongYear = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongYear);
            insertSongFormat = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongFormat);
            insertSongDuration = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongDuration);
            insertSongGenre = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongGenre);
            insertSongTrackNumber = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongTrackNumber);
            insertSongTrackCount = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongTrackCount);
            insertSongSize = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongSize);
            insertSongLastUpdatedInfo = insertSong.CreateParameter();
            insertSong.Parameters.Add(insertSongLastUpdatedInfo);

            updateSong = databaseConnection.CreateCommand();
            updateSong.CommandText = @"UPDATE songs SET artist=?, album=?, title=?, year=?, format=?, duration=?,
                                        genre=?, tracknumber=?, trackcount=?, size=?, lastUpdated=? 
                                        WHERE libraryId=? AND remoteSongId=?";


            //Create and add parameters for updating songs
            updateSongArtist = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongArtist);
            updateSongAlbum = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongAlbum);
            updateSongTitle = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongTitle);
            updateSongYear = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongYear);
            updateSongFormat = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongFormat);
            updateSongDuration = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongDuration);
            updateSongGenre = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongGenre);
            updateSongTrackNumber = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongTrackNumber);
            updateSongTrackCount = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongTrackCount);
            updateSongSize = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongSize);
            updateSongLastUpdatedInfo = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongLastUpdatedInfo);
            updateSongLibraryId = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongLibraryId);
            updateSongRemoteSongId = updateSong.CreateParameter();
            updateSong.Parameters.Add(updateSongRemoteSongId);

            //Song existance parameters
            songExists = databaseConnection.CreateCommand();
            songExists.CommandText = "SELECT COUNT(*) FROM songs WHERE libraryId=? AND remoteSongId=?";
            existsLibraryId = songExists.CreateParameter();
            songExists.Parameters.Add(existsLibraryId);
            existsSongId = songExists.CreateParameter();
            songExists.Parameters.Add(existsSongId);
        }

        /// <summary>
        /// Determines whether we need to insert a new song or update and existing record 
        /// </summary>
        private bool SongExists(int libraryId, int songId)
        {
            existsLibraryId.Value = libraryId;
            existsSongId.Value = songId;

            IDataReader reader = songExists.ExecuteReader();
            reader.Read();
            int count = reader.GetInt32(0);
            reader.Dispose();

            return (count == 1) ? true : false;
        }
    }
}
