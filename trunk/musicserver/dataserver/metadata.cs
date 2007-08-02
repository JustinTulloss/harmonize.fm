using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Data.Common;

#if MONO
using Mono.Data.SqliteClient;
#else
using System.Data.SQLite;
#endif

using Nwc.XmlRpc;
using DMP;
using DMP.Data;
using Entagged;
using System.Threading;

namespace DMP.Server
{
	[XmlRpcExposed]
	public class Metadata
	{
		const int DEFAULT_PORT = 3689;
		private static string defaultName = System.Net.Dns.GetHostName();
		//All the queries we could ever want to define

		/****Settings queries*****/
		const string FIND_SERVER_NAME = 
			"SELECT value FROM settings WHERE key=\"servername\"";
		const string UPDATE_SERVER_NAME = 
			"UPDATE settings SET value=? WHERE key=\"servername\"";
		const string INSERT_SERVER_NAME =
			"INSERT INTO settings values(\"servername\",?)";
		const string FIND_SERVER_PORT =
			"SELECT value FROM settings WHERE key=\"serverport\"";
		const string UPDATE_SERVER_PORT =
			"UPDATE settings SET value=? WHERE key=\"serverport\"";
		const string INSERT_SERVER_PORT =
			"INSERT INTO settings values(\"serverport\",?)";
		/*****End settings queries *****/

		/*****Creation querie *****/
		const string CREATE_DB = @"CREATE TABLE songs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			path TEXT,
			artist TEXT,
			album TEXT,
			title TEXT,
			year INTEGER,
			format TEXT,
			duration TIME,
			genre TEXT,
			tracknumber INTEGER,
			trackcount INTEGER,
			size INTEGER,
			updated INTEGER,
			fileLastModified DATETIME,
			dbLastModified UNSIGNED INTEGER,
			deleted TINYINT
			); 
			CREATE INDEX rev_idx on songs(dbLastModified);
			CREATE TABLE playlists (
			id INTEGER,
			songid INTEGER);
			CREATE INDEX pl_idx ON playlists(id);
			CREATE TABLE directories (path TEXT);
			CREATE TABLE settings (key TEXT, value TEXT);";
		/*******End create db querie *******/

		/***** Informational queries *******/
		const string GET_SONG_COUNT = "SELECT COUNT(*) FROM songs";
		const string GET_SONG_PATHS = "SELECT path FROM songs";
		/**** End INformational queries *****/

		const string INSERT_DIRECTORY =
			"INSERT INTO directories('path') VALUES(?)";


		//Delegates for communicating with the GUI
		public delegate void UpdateProgressBar();
		public delegate void UpdateProgressTitle(string newTitle);
		public delegate void SetProgressMax(int max);
		public delegate void ResetProgressBar();

		//Instances of above delegates
		public static UpdateProgressTitle progressTitle;
		public static UpdateProgressBar progressUpdate;
		public static ResetProgressBar progressReset;
		public static SetProgressMax progressMax;

		//The almighty database connection
		private IDbConnection dbCon;

		//The current revision that the database is at
		private static int revision = 2;
		private static Object revLock = new Object();

		/// <summary>
		/// Default Constructor, creates db in current directory
		/// </summary>
		public Metadata() : this(System.IO.Directory.GetCurrentDirectory()+"/serverdb.db3")
		{ }

		//Default Constructor
		//TODO:
		// -Fail on bad path
		public Metadata(string path)
		{
			InitializeDb(path);

			//should probably lock. I think it's unnecessary, but it won't hurt
			lock (revLock)
			{
				revision = this.LatestRevision;
			}
		}

		/// <summary>
		/// Takes as an argument the SQLite database file to use for this server
		/// instance, checks whether it's there and creates it if not
		/// </summary>
		public bool InitializeDb(string path)
		{
			path = EscapePath(path);

			if (path == null)
				return false;

			string directory = System.IO.Path.GetDirectoryName(path);
			if (!System.IO.Directory.Exists(directory))
				return false;


#if MONO
			string connection = "URI=file:" + path;
			dbCon = (IDbConnection)new SqliteConnection(connection);
#else
			string connection = "Data Source=" + path;
			dbCon = (IDbConnection)new SQLiteConnection(connection);
#endif

			if (System.IO.File.Exists(path))
			{
				//TODO: Should validate database here, perhaps on a version number
				InitSQLCommands();
				return true;
			}

			return CreateDb();
		}

		/// <summary>
		/// This function creates a new database at the given path
		/// </summary>
		/// <returns>Success or failure</returns>
		private bool CreateDb()
		{
			if (dbCon == null)
				return false;

			IDbCommand dbcmd = dbCon.CreateCommand();
			dbcmd.CommandText = CREATE_DB;

			dbCon.Open();
			dbcmd.ExecuteNonQuery();


			//Insert Default Settings
			dbcmd.CommandText = INSERT_SERVER_PORT;
			IDbDataParameter valueParam = dbcmd.CreateParameter();
			dbcmd.Parameters.Add(valueParam);
			valueParam.Value = DEFAULT_PORT;
			dbcmd.ExecuteNonQuery();

			dbcmd.Parameters.Clear();

			dbcmd.CommandText = INSERT_SERVER_NAME;
			IDbDataParameter nameParam = dbcmd.CreateParameter();
			dbcmd.Parameters.Add(nameParam);
			nameParam.Value = defaultName;
			dbcmd.ExecuteNonQuery();

			dbCon.Close();

			InitSQLCommands();

			return true;
		}

		/// <summary>
		/// Returns true if directory successfully added or is already monitored,
		/// false if unable or directory doesn't exist
		/// </summary>
		/// <remarks>
		/// 070117::JMT - Altered this to return Error ErrorStruct (for RPC)
		/// </remarks>
		/// <param name="path">Directory to add</param>
		/// <returns>Success or failure</returns>
		public Error AddDirectory(string path)
		{
			if (dbCon == null)
			{
				Error noConn = new Error("Database Connection does not exist");
				return noConn;
			}

			path = EscapePath(path);

			if (path == null)
			{
				Error noPath = new Error("Must pass non-null file path");
				return noPath;
			}

			if (!System.IO.Directory.Exists(path))
			{
				Error badPath = new Error("Directory does not exist");
				return badPath;
			}

			dbCon.Open();
			IDbCommand dbCmd = dbCon.CreateCommand();

			dbCmd.CommandText = "SELECT COUNT(*) FROM directories WHERE path=?";
			IDataParameter pPath = dbCmd.CreateParameter();
			dbCmd.Parameters.Add(pPath);
			pPath.Value = path;

			IDataReader reader = dbCmd.ExecuteReader();
			reader.Read();

			int count = reader.GetInt32(0);
			reader.Close();

			if (count > 0)
			{
				dbCmd.Dispose();
				dbCon.Close();
				return null;
			}

			dbCmd.CommandText = INSERT_DIRECTORY;
			pPath = dbCmd.CreateParameter();
			dbCmd.Parameters.Add(pPath);
			pPath.Value = path;
			dbCmd.ExecuteNonQuery();

			//dbCmd.Dispose();
			dbCon.Close();

			return null;
		}

		/// <summary>
		/// Returns true if directory was successfully removed, false otherwise
		/// </summary>
		/// <remarks>
		/// 070117::JMT - Altered this to return Error ErrorStruct (for RPC)
		/// </remarks>
		/// <param name="path">Path of directory to remove</param>
		/// <returns>Success or failure errorstruct</returns>
		[XmlRpcExposed]
		public Hashtable RemoveDirectory(string path)
		{
			if (dbCon == null)
			{
				Error noDb = new Error("Database has not been initialized");
				return noDb.Structure;
			}
			path = EscapePath(path);

			if (path == null)
			{
				Error noPath = new Error("Must pass non-null file path");
				return noPath.Structure;
			}

			IDbCommand dbCmd = dbCon.CreateCommand();
			dbCmd.CommandText = "DELETE FROM directories WHERE path=?";
			IDataParameter pPath = dbCmd.CreateParameter();
			dbCmd.Parameters.Add(pPath);
			pPath.Value = path;

			dbCon.Open();
			int rowsAffected = dbCmd.ExecuteNonQuery();
			dbCon.Close();

			dbCmd.Dispose();

			if (rowsAffected != 0)
				return null;
			else
			{
				Error delFailed = new Error("Delete Failed");
				return delFailed.Structure;
			}
		}

		/// <summary>
		/// This returns a list of strings representing all monitored directories
		/// </summary>
		[XmlRpcExposed]
		public ArrayList ListDirectories()
		{
			if (dbCon == null)
				return null;

			IDbCommand dbCmd = dbCon.CreateCommand();

			dbCmd.CommandText = "SELECT COUNT(*) FROM directories";
			dbCon.Open();
			IDataReader reader = dbCmd.ExecuteReader();

			reader.Read();
			int count = reader.GetInt32(0);
			reader.Close();

			ArrayList returnVal = new ArrayList(count);

			dbCmd.CommandText = "SELECT path FROM directories";
			reader = dbCmd.ExecuteReader();

			for (int i = 0; i < count; i++)
			{
				reader.Read();
				returnVal.Add(reader.GetString(0));
			}

			dbCon.Close();
			reader.Close();
			//dbCmd.Dispose();

			return returnVal;
		}

		/// <summary>
		/// Takes each of the directories in the directories table and updates the
		/// songs in those directories
		/// </summary>
		/// <remarks>
		/// 070117::JMT - Altered this to return Error ErrorStruct (for RPC)
		/// </remarks>
		/// <returns></returns>
		public Error UpdateMusic()
		{
			if (dbCon == null)
			{
				Error noDb = new Error("Database has not been initialized");
				return noDb;
			}

			ArrayList directories = ListDirectories();

			dbCon.Open();
			IDbTransaction dbTrans = dbCon.BeginTransaction();

			IDbCommand markUpdated = dbCon.CreateCommand();
			markUpdated.CommandText = "UPDATE songs SET Updated=0; DELETE FROM playlists WHERE id=0;";
			markUpdated.ExecuteNonQuery();

			foreach (string path in directories)
			{

				System.IO.DirectoryInfo di = new System.IO.DirectoryInfo(path);

				//Should this return? It seems to me like it should silently
				//remove the directory from the DB if it's found to no longer
				//exist. Either that or just skip it.
				if (!di.Exists)
				{
					Error dirFailure = new Error("Directory " + path + " no longer exists");
					return dirFailure;
				}

				bool returnVal = UpdateDirectory(di);

				if (returnVal == false)
				{
					Error updateFailed = new Error("Updating " + path + " failed");
					return updateFailed;
				}
			}

			IDbCommand delNotUpdated = dbCon.CreateCommand();
			delNotUpdated.CommandText = "UPDATE songs SET deleted=1 WHERE Updated=0";
			delNotUpdated.ExecuteNonQuery();

			dbTrans.Commit();
			dbCon.Close();

			//Update Revision
			TimeSpan unixTime = (DateTime.UtcNow - new DateTime(1970, 1, 1));
			lock (revLock)
			{
				revision++;
				Monitor.PulseAll(revLock);
			}

			return null;
		}

		//Updates all the songs in the current directory and calls itself 
		//recursively on all subdirectories
		//TODO:
		// --Handle updating existing entries
		// --Find way of extracting tag info and inserting into db
		private bool UpdateDirectory(System.IO.DirectoryInfo currentDir)
		{
			bool returnVal = true; //Not sure what this will be used for...
			AudioFile song;

			System.IO.FileInfo[] files = currentDir.GetFiles();

			//Do progress bar reset
			if (progressTitle != null)
				progressTitle("Adding songs in "+currentDir.Name+"...");
			if (progressMax != null)
				progressMax(files.GetLength(0));
			if (progressReset != null)
				progressReset();

			foreach (System.IO.FileInfo fi in files)
			{
				//Update progress bar
				if (progressUpdate != null)
					progressUpdate();

				if (ValidMusicFile(fi))
				{
					try
					{
						song = new AudioFile(fi.FullName);
					}
					catch (Exception e)
					{
						Console.WriteLine("Problem with file {0} : {1}", fi.FullName, e);
						continue;
					}

					insertSongPath.Value = fi.FullName;
					insertSongArtist.Value = song.Artist;
					insertSongAlbum.Value = song.Album;
					insertSongTitle.Value = song.Title;
					insertSongYear.Value = song.Year;
					insertSongFormat.Value = fi.Extension.Substring(1);
					insertSongDuration.Value = song.Duration.TotalMilliseconds;
					insertSongGenre.Value = song.Genre;
					insertSongTrackNumber.Value = song.TrackNumber;
					insertSongTrackCount.Value = song.TrackCount;
					insertSongSize.Value = fi.Length;
					insertSongFileLastModified.Value = fi.LastWriteTimeUtc;
					insertSongDbLastModified.Value = revision;

					int updateId = 0;
					DateTime lastUpdated = new DateTime();

					getSongPath.Value = fi.FullName;
					IDataReader sqlTrack = getSongByPath.ExecuteReader();
					if (sqlTrack.Read())
					{
						updateId = sqlTrack.GetInt32(0);
						lastUpdated = sqlTrack.GetDateTime(1).ToUniversalTime();
					}

					sqlTrack.Dispose();

					//File was not already in database
					if (updateId == 0)
					{
						System.Console.WriteLine("Adding file {0} to database", fi.FullName);
						IDataReader lastID = insertSong.ExecuteReader();

						lastID.Read();
						insertSongInPlaylistId.Value = 0;
						insertSongInPlaylistSongId.Value = lastID.GetInt32(0);
						lastID.Dispose();

						insertSongInPlaylist.ExecuteNonQuery();
					}
					else
					{
						updateSongId.Value = updateId;

						//Put track back in the base playlist
						insertSongInPlaylistId.Value = 0;
						insertSongInPlaylistSongId.Value = updateId;

						insertSongInPlaylist.ExecuteNonQuery();

						if (!lastUpdated.Equals(fi.LastWriteTimeUtc))
						{
							System.Console.WriteLine("Updating file {0} in database", fi.FullName);
							updateSong.ExecuteNonQuery();
						}
						else
							hasUpdated.ExecuteNonQuery();
					}

				}
			}

			System.IO.DirectoryInfo[] directories = currentDir.GetDirectories();

			foreach (System.IO.DirectoryInfo di in directories)
				returnVal &= UpdateDirectory(di);

			return returnVal;
		}

		[XmlRpcExposed]
		public ArrayList ListSongs()
		{
			if (dbCon == null)
				return null;

			try
			{
				IDbCommand dbCmd = dbCon.CreateCommand();

				dbCmd.CommandText = GET_SONG_COUNT;

				dbCon.Open();

				IDataReader reader = dbCmd.ExecuteReader();
				reader.Read();
				int count = reader.GetInt32(0);
				reader.Close();

				ArrayList returnVal = new ArrayList(count);

				dbCmd.CommandText = GET_SONG_PATHS;
				reader = dbCmd.ExecuteReader();

				for (int i = 0; i < count; i++)
				{
					reader.Read();
					returnVal.Add(reader.GetString(0));
				}

				dbCon.Close();
				return returnVal;
			}
			catch (Exception e)
			{
				Console.WriteLine("Exception: {0}", e.Message);
				return null;
			}
		}

		public int SongCount
		{
			get
			{
				int count;                
				IDbCommand dbCmd = dbCon.CreateCommand();

				dbCon.Open();

				dbCmd.CommandText = GET_SONG_COUNT;

				IDataReader reader = dbCmd.ExecuteReader();
				if (reader.Read())
					count = reader.GetInt32(0);
				else
					return 0;
				reader.Dispose();

				dbCon.Close();

				return count;
			}
		}

		/// <summary>
		/// A list of every track in the database
		/// </summary>
		public List<TrackBase> TrackList
		{
			get
			{
				IDbCommand dbCmd = dbCon.CreateCommand();
				List<TrackBase> trackList;

				dbCon.Open();

				dbCmd.CommandText = "SELECT * FROM songs";
				IDataReader reader = dbCmd.ExecuteReader();

				trackList = (List<TrackBase>)SqlToTrack(reader);
				reader.Dispose();
				dbCon.Close();
				return trackList;  
			}
		}

		/// <summary>
		/// Checks to see if the file already exists in the database.
		/// </summary>
		/// <param name="fi">FileInfo object about the file in question</param>
		/// <returns>songid if file is in the database</returns>
		private int FileExistsInDb(System.IO.FileInfo fi)
		{
			getSongPath.Value = fi.FullName;
			int retTrack;

			IDataReader sqlTrack = getSongByPath.ExecuteReader();
			if (sqlTrack.Read())
			{
				retTrack = sqlTrack.GetInt32(0);
			}
			else
				retTrack = 0;

			sqlTrack.Dispose();

			return retTrack;
		}

		/// <summary>
		/// Gets song data from the database.
		/// </summary>
		/// <param name="songid">Id of the song to play</param>
		/// <returns></returns>
		public TrackBase GetSong(Int32 songid)
		{
			getSongId.Value = songid;
			dbCon.Open();
			IDataReader sqlTrack = getSong.ExecuteReader();
			List<TrackBase> retTrack = (List<TrackBase>) SqlToTrack(sqlTrack);
			sqlTrack.Dispose();
			dbCon.Close();

			return retTrack[0];
		}

		/// <summary>
		/// Retreives playlist from the database
		/// </summary>
		/// <param name="playlistid">Id of the playlist to get</param>
		/// <returns></returns>
		public PlaylistBase GetPlaylist(Int32 playlistid)
		{
			PlaylistBase retVal = new PlaylistBase(playlistid);

			dbCon.Open();
			getPlaylistId.Value = playlistid;
			IDataReader sqlPlaylist = getPlaylist.ExecuteReader();

			while(sqlPlaylist.Read())
			{
				retVal.AddTrack(sqlPlaylist.GetInt32(1));
			}

			sqlPlaylist.Dispose();
			dbCon.Close();
			return retVal;
		}

		//DB Commands
		private IDbCommand insertSong;
		private IDbCommand updateSong;
		private IDbCommand hasUpdated;
		private IDbCommand insertSongInPlaylist;
		private IDbCommand getSong;
		private IDbCommand getSongByPath;
		private IDbCommand getPlaylist;
		private IDbCommand getLatestRevision;

		//Data parameters for insertSong and updateSong commands
		private IDataParameter insertSongPath;
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
		private IDataParameter insertSongFileLastModified;
		private IDataParameter insertSongDbLastModified;

		//Song id to update
		private IDataParameter updateSongId;

		//Data parameters for insertSongInPlaylist command
		private IDataParameter insertSongInPlaylistSongId;
		private IDataParameter insertSongInPlaylistId;

		//parameters for getSong
		private IDataParameter getSongId;
		private IDataParameter getSongPath;

		//parameters for getPlaylist
		private IDataParameter getPlaylistId;

		/// <summary>
		/// initializes all the commands needed so they are only created once
		/// </summary>
		private void InitSQLCommands()
		{
			insertSong = dbCon.CreateCommand();
			updateSong = dbCon.CreateCommand();
			hasUpdated = dbCon.CreateCommand();
			insertSongInPlaylist = dbCon.CreateCommand();
			getSong = dbCon.CreateCommand();
			getSongByPath = dbCon.CreateCommand();
			getPlaylist = dbCon.CreateCommand();
			getLatestRevision = dbCon.CreateCommand();

			insertSong.CommandText = @"INSERT INTO songs(path, artist, album, title, year, format, duration,
										genre, tracknumber, trackcount, size, updated, fileLastModified, 
										dbLastModified, deleted) 
										VALUES(?,?,?,?,?,?,?,?,?,?,?,1,?,?,0);
										SELECT last_insert_rowid()";
			updateSong.CommandText = @"UPDATE songs SET path = ?, artist = ?, album = ?, title = ?, year =?,
											format = ?, duration = ?, genre = ?, tracknumber = ?, trackcount =?,
											size = ?, updated = 1, fileLastModified=?, 
											dbLastModified= ?
											WHERE id = ?";
			hasUpdated.CommandText = @"UPDATE songs SET updated = 1 WHERE id = ?";
			insertSongInPlaylist.CommandText = @"INSERT INTO playlists(id, songid) VALUES(?,?)";
			getSong.CommandText = @"SELECT * FROM songs WHERE id = ?";
			getSongByPath.CommandText = @"SELECT id, fileLastModified FROM songs WHERE path = ?";
			getPlaylist.CommandText = @"SELECT * FROM playlists WHERE id = ?";
			getLatestRevision.CommandText = @"SELECT MAX(dbLastModified) FROM songs";

			//Create and add parameters for inserting songs
			insertSongPath = insertSong.CreateParameter();
			insertSong.Parameters.Add(insertSongPath);
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
			insertSongFileLastModified = insertSong.CreateParameter();
			insertSong.Parameters.Add(insertSongFileLastModified);
			insertSongDbLastModified = insertSong.CreateParameter();
			insertSong.Parameters.Add(insertSongDbLastModified);

			//update song parameters
			updateSong.Parameters.Add(insertSongPath);
			updateSong.Parameters.Add(insertSongArtist);
			updateSong.Parameters.Add(insertSongAlbum);
			updateSong.Parameters.Add(insertSongTitle);
			updateSong.Parameters.Add(insertSongYear);
			updateSong.Parameters.Add(insertSongFormat);
			updateSong.Parameters.Add(insertSongDuration);
			updateSong.Parameters.Add(insertSongGenre);
			updateSong.Parameters.Add(insertSongTrackNumber);
			updateSong.Parameters.Add(insertSongTrackCount);
			updateSong.Parameters.Add(insertSongSize);
			updateSong.Parameters.Add(insertSongFileLastModified);
			updateSong.Parameters.Add(insertSongDbLastModified);

			//update song id only applies to updates
			updateSongId = updateSong.CreateParameter();
			updateSong.Parameters.Add(updateSongId);
			hasUpdated.Parameters.Add(updateSongId);

			insertSongInPlaylistId = insertSongInPlaylist.CreateParameter();
			insertSongInPlaylist.Parameters.Add(insertSongInPlaylistId);
			insertSongInPlaylistSongId = insertSongInPlaylist.CreateParameter();
			insertSongInPlaylist.Parameters.Add(insertSongInPlaylistSongId);

			getSongId = getSong.CreateParameter();
			getSong.Parameters.Add(getSongId);

			getSongPath = getSongByPath.CreateParameter();
			getSongByPath.Parameters.Add(getSongPath);

			getPlaylistId = getPlaylist.CreateParameter();
			getPlaylist.Parameters.Add(getPlaylistId);
		}


		/// <summary>
		/// This returns an escaped path so all directory entries are uniform
		/// </summary>
		/// <param name="path"></param>
		/// <returns></returns>
		private string EscapePath(string path)
		{
			try
			{
				path = System.IO.Path.GetFullPath(path);
			}
			catch (System.Exception e)
			{
				return null;
			}
			return path;
		}

		///<summary>
		///This checks whether a file is music
		///</summary>
		private bool ValidMusicFile(System.IO.FileInfo fi)
		{
			if (fi.Extension == ".mp3" || fi.Extension == ".m4a")
				return true;
			else
				return false;
		}

		/// <summary>
		/// Turns an sql data reader into a list of tracks
		/// </summary>
		/// <param name="sqlResult"></param>
		/// <returns></returns>
		private IList<TrackBase> SqlToTrack(IDataReader sqlResult)
		{
			List<TrackBase> trackList = new List<TrackBase>();
			while (sqlResult.Read())
			{
				TrackBase track = new TrackBase();

				track.SetId(sqlResult.GetInt32(0));
				if (!sqlResult.IsDBNull(1))
					track.FileName = sqlResult.GetString(1);
				if (!sqlResult.IsDBNull(2))
					track.Artist = sqlResult.GetString(2);
				if (!sqlResult.IsDBNull(3))
					track.Album = sqlResult.GetString(3);

				if (!sqlResult.IsDBNull(4))
					track.Title = sqlResult.GetString(4);
				if (!sqlResult.IsDBNull(5))
					track.Year = sqlResult.GetInt32(5);
				if (!sqlResult.IsDBNull(6))
					track.Format = sqlResult.GetString(6);
				if (!sqlResult.IsDBNull(7))
					//Store number of milliseconds in DB, so get TimeSpan like so:
					track.Duration = new TimeSpan(0,0,0,0,sqlResult.GetInt32(7));
				if (!sqlResult.IsDBNull(8))
					track.Genre = sqlResult.GetString(8);
				if (!sqlResult.IsDBNull(9))
					track.TrackNumber = sqlResult.GetInt32(9);
				if (!sqlResult.IsDBNull(10))
					track.TrackCount = sqlResult.GetInt32(10);
				if (!sqlResult.IsDBNull(11))
					track.Size = sqlResult.GetInt32(11);

				trackList.Add(track);                
			}
			return trackList;
		}

		/// <summary>
		/// Gets all the songs that have been deleted between the two requested revisions
		/// </summary>
		/// <param name="oldRev">The previous revision</param>
		/// <param name="currentRev">The revision being requested</param>
		/// <returns>ArrayList of songids</returns>
		public ArrayList GetDeletedIds(int oldRev, int currentRev)
		{
			dbCon.Open();
			IDbCommand getDeletedIds = dbCon.CreateCommand();
			getDeletedIds.CommandText = @"SELECT id FROM songs WHERE
					dbLastModified > " + oldRev + " AND dbLastModified <= " + currentRev +
					" AND deleted = 1";
			IDataReader deletedIds = getDeletedIds.ExecuteReader();

			ArrayList delIdArray = new ArrayList();

			while (deletedIds.Read())
			{
				delIdArray.Add(deletedIds.GetInt32(0));
			}

			deletedIds.Dispose();
			dbCon.Close();

			return delIdArray;
		}

		public int Revision
		{
			get
			{
				return revision;
			}
		}

		/// <summary>
		/// Allows a thread to wait indefinitely for a db update (blocks)
		/// </summary>
		/// <param name="oldRevision"></param>
		/// <returns>The newest revision number</returns>
		public int WaitForUpdate(int oldRevision)
		{
			Console.WriteLine("Old Revision: {0}", oldRevision);
			while (revision == oldRevision)
			{
				lock (revLock)
				{
					Console.WriteLine("Waiting for Update");
					Monitor.Wait(revLock);
					Console.WriteLine("Woke up, checking to see if update occurred...");
				}
			}
			Console.WriteLine("Found new revision: {0}", revision);
			return revision;
		}

		public List<TrackBase> GetTracks(int requestedRevision)
		{
			IDbCommand dbCmd = dbCon.CreateCommand();
			List<TrackBase> trackList;

			dbCon.Open();

			dbCmd.CommandText = "SELECT * FROM songs WHERE dbLastModified<= "+requestedRevision;
			IDataReader reader = dbCmd.ExecuteReader();

			trackList = (List<TrackBase>)SqlToTrack(reader);
			reader.Dispose();
			dbCon.Close();
			return trackList;  
		}

		private int LatestRevision
		{
			get
			{
				int latest = 2;
				dbCon.Open();
				IDataReader scalar = getLatestRevision.ExecuteReader();
				scalar.Read();
				if (!scalar.IsDBNull(0))
				{
					latest = scalar.GetInt32(0);
				}
				dbCon.Close();
				return latest;
			}
		}

		public string ServerName
		{
			get
			{
				dbCon.Open();
				IDbCommand sqlServer = dbCon.CreateCommand();

				sqlServer.CommandText = FIND_SERVER_NAME;
				string name = sqlServer.ExecuteScalar().ToString();

				sqlServer.Dispose();
				dbCon.Close();

				return name;
			}
			set
			{
				dbCon.Open();
				IDbCommand updateServer = dbCon.CreateCommand();

				updateServer.CommandText= UPDATE_SERVER_NAME;
				IDbDataParameter newName = updateServer.CreateParameter();
				updateServer.Parameters.Add(newName);

				newName.Value = value;

				updateServer.ExecuteNonQuery();
			}
		}

		public int ServerPort
		{
			get
			{
				dbCon.Open();
				IDbCommand sqlServer = dbCon.CreateCommand();

				sqlServer.CommandText = FIND_SERVER_PORT;
				int port = Int32.Parse(sqlServer.ExecuteScalar().ToString());

				sqlServer.Dispose();
				dbCon.Close();

				return port;
			}
			set
			{
				dbCon.Open();
				IDbCommand updateServer = dbCon.CreateCommand();

				updateServer.CommandText= UPDATE_SERVER_PORT;
				IDbDataParameter newName = updateServer.CreateParameter();
				updateServer.Parameters.Add(newName);

				newName.Value = value;

				updateServer.ExecuteNonQuery();
			}
		}

				
	}
}
