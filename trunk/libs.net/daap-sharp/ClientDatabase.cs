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
using System.Net;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Threading;
using DMP.Data;
using DMP;

namespace DAAP {
/*
    public delegate void TrackHandler (object o, TrackArgs args);

    public class TrackArgs : EventArgs {
        private Track track;

        public Track Track {
            get { return track; }
        }
        
        public TrackArgs (Track track) {
            this.track = track;
        }
    }
        
    public delegate void PlaylistHandler (object o, PlaylistArgs args);

    public class PlaylistArgs : EventArgs {
        private Playlist pl;

        public Playlist Playlist {
            get { return pl; }
        }
        
        public PlaylistArgs (Playlist pl) {
            this.pl = pl;
        }
    }
*/
    public class ClientDatabase : ICloneable {

        private const int ChunkLength = 8192;
        private const string TrackQuery = "meta=dmap.itemid,dmap.itemname,dmap.itemkind,dmap.persistentid," +
                                         "daap.songalbum,daap.songgrouping,daap.songartist,daap.songbitrate," +
                                         "daap.songbeatsperminute,daap.songcomment,daap.songcodectype," +
                                         "daap.songcodecsubtype,daap.songcompilation,daap.songcomposer," +
                                         "daap.songdateadded,daap.songdatemodified,daap.songdisccount," +
                                         "daap.songdiscnumber,daap.songdisabled,daap.songeqpreset," +
                                         "daap.songformat,daap.songgenre,daap.songdescription," +
                                         "daap.songsamplerate,daap.songsize,daap.songstarttime," +
                                         "daap.songstoptime,daap.songtime,daap.songsongcount," +
                                         "daap.songsongnumber,daap.songuserrating,daap.songyear," +
                                         "daap.songdatakind,daap.songdataurl,com.apple.itunes.norm-volume," +
                                         "com.apple.itunes.itms-songid,com.apple.itunes.itms-artistid," +
                                         "com.apple.itunes.itms-playlistid,com.apple.itunes.itms-composerid," +
                                         "com.apple.itunes.itms-genreid";

        private static int nextid = 1;
        private Client client;
        private int id;
        private long persistentId;
        private string name;

        //private List<Track> tracks = new List<Track> ();
        //private List<Playlist> playlists = new List<Playlist> ();
        //private Playlist basePlaylist = new Playlist ();
        private int nextTrackId = 1;

        public event TrackHandler TrackAdded;
        public event TrackHandler TrackRemoved;
        public event PlaylistHandler PlaylistAdded;
        public event PlaylistHandler PlaylistRemoved;

        public int Id {
            get { return id; }
        }

        public string Name {
            get { return name; }
            set {
                name = value;
                //basePlaylist.Name = value;
            }
        }
        
        internal Client Client {
            get { return client; }
        }

        private ClientDatabase () {
            this.id = nextid++;
        }

        public ClientDatabase (string name) : this () {
            this.Name = name;
        }

        internal ClientDatabase (Client client, ContentNode dbNode) : this () {
            this.client = client;

            Parse (dbNode);
        }

        private void Parse (ContentNode dbNode) {
            foreach (ContentNode item in (ContentNode[]) dbNode.Value) {

                switch (item.Name) {
                case "dmap.itemid":
                    id = (int) item.Value;
                    break;
                case "dmap.persistentid":
                    persistentId = (long) item.Value;
                    break;
                case "dmap.itemname":
                    name = (string) item.Value;
                    break;
                default:
                    break;
                }
            }
        }

        private bool IsUpdateResponse (ContentNode node) {
            return node.Name == "dmap.updateresponse";
        }

        /// <summary>
        /// Re-retrieves playlists from the server
        /// </summary>
        /// <param name="revquery"></param>
        /// <param name="playlists">out param that contains the playlists</param>
        /// <returns>Error on failure, null on success</returns>
        private Error RefreshPlaylists(string revquery)
        {
            byte[] playlistsData;
            List<PlaylistBase> thePlaylists = new List<PlaylistBase>();
            BridgeDatabase theData = new BridgeDatabase();

            try {
                playlistsData = client.Fetcher.Fetch (String.Format ("/databases/{0}/containers", id, revquery));
            } catch (WebException e) {
                return new Error("An Exception occurred: " + e.Message); ;
            }
            
            ContentNode playlistsNode = ContentParser.Parse (client.Bag, playlistsData);

            if (IsUpdateResponse (playlistsNode))
                return null;

            // handle playlist additions/changes
            
            foreach (ContentNode playlistNode in (ContentNode[]) playlistsNode.GetChild ("dmap.listing").Value) {
                Playlist pl = Playlist.FromNode (playlistNode);

                if (pl != null) {
                    thePlaylists.Add(pl);
                }
            }

            theData.addPlaylists(thePlaylists);

            return null;
            /* Do this at a later time now --JMT
            // add/remove tracks in the playlists
            foreach (Playlist pl in playlists) {
                byte[] playlistTracksData = client.Fetcher.Fetch (String.Format ("/databases/{0}/containers/{1}/items",
                                                                                id, pl.Id), revquery);
                ContentNode playlistTracksNode = ContentParser.Parse (client.Bag, playlistTracksData);

                if (IsUpdateResponse (playlistTracksNode))
                    return;

                if ((byte) playlistTracksNode.GetChild ("dmap.updatetype").Value == 1) {

                    // handle playlist track deletions
                    ContentNode deleteList = playlistTracksNode.GetChild ("dmap.deletedidlisting");

                    if (deleteList != null) {
                        foreach (ContentNode deleted in (ContentNode[]) deleteList.Value) {
                            int index = pl.LookupIndexByContainerId ((int) deleted.Value);

                            if (index < 0)
                                continue;

                            pl.RemoveAt (index);
                        }
                    }
                }

                // add new tracks, or reorder existing ones

                int plindex = 0;
                foreach (ContentNode plTrackNode in (ContentNode[]) playlistTracksNode.GetChild ("dmap.listing").Value) {
                    Track pltrack = null;
                    int containerId = 0;
                    Track.FromPlaylistNode (this, plTrackNode, out pltrack, out containerId);

                    if (pl[plindex] != null && pl.GetContainerId (plindex) != containerId) {
                        pl.RemoveAt (plindex);
                        pl.InsertTrack (plindex, pltrack, containerId);
                    } else if (pl[plindex] == null) {
                        pl.InsertTrack (plindex, pltrack, containerId);
                    }

                    plindex++;
                }
            }*/
        }

        /// <summary>
        /// Requests the list of tracks from the server
        /// </summary>
        /// <param name="revquery"></param>
        /// <param name="deletedIds">out parameter that will contain all deleted tracks</param>
        /// <returns>Error on failure, null on success</returns>
        private Error RefreshTracks (string revquery) {
            BridgeDatabase theData = new BridgeDatabase();
            List<TrackBase> theTracks = new List<TrackBase>();
            List<int> deletedIds = new List<int>();

            byte[] tracksData = client.Fetcher.Fetch (String.Format ("/databases/{0}/items", id),
                                                     TrackQuery + "&" + revquery);
            ContentNode tracksNode = ContentParser.Parse (client.Bag, tracksData);
            
            if (IsUpdateResponse (tracksNode))
                return null;

            // handle track additions/changes
            foreach (ContentNode trackNode in (ContentNode[]) tracksNode.GetChild ("dmap.listing").Value) {
                Track track = Track.FromNode (trackNode);
                theTracks.Add(track);
            }

            theData.addSongs(theTracks,client.Id);

            //This flag shows that this update is has deleted tracks
            if ((byte) tracksNode.GetChild ("dmap.updatetype").Value == 1) {

                // handle track deletions
                ContentNode deleteList = tracksNode.GetChild ("dmap.deletedidlisting");

                if (deleteList != null) {
                    foreach (ContentNode deleted in (ContentNode[]) deleteList.Value) {
                        deletedIds.Add((int)deleted.Value);
                    }
                }
                theData.removeSongs(deletedIds);
            }

            return null;
        }

        /// <summary>
        /// Refreshes Client data from server
        /// </summary>
        /// <param name="newrev">The new revision to fetch</param>
        internal void Refresh(int newrev)
        {
            if (client == null)
                throw new InvalidOperationException ("cannot refresh server databases");

            string revquery = null;

            if (client.Revision != 0)
                revquery = String.Format("revision-number={0}&delta={1}", newrev, newrev - client.Revision);
            else
                revquery = String.Format("revision-number={0}", newrev);

            RefreshTracks (revquery);
            //RefreshPlaylists (revquery);
        }

        private HttpWebResponse FetchTrack (Track track, long offset) {
            return client.Fetcher.FetchFile (String.Format ("/databases/{0}/items/{1}.{2}", id, track.Id, track.Format),
                                             offset);
        }

        public UriBuilder StreamTrackURI(Track track)
        {
            return client.Fetcher.FetchResponseURI(
                String.Format("/databases/{0}/items/{1}.{2}", id, track.Id, track.Format), null);
        }

        public Stream StreamTrack (Track track, out long length) {
            return StreamTrack (track, -1, out length);
        }
        
        public Stream StreamTrack (Track track, long offset, out long length) {
            HttpWebResponse response = FetchTrack (track, offset);
            length = response.ContentLength;
            return response.GetResponseStream ();
        }

        public void DownloadTrack (Track track, string dest) {

            BinaryWriter writer = new BinaryWriter (File.Open (dest, FileMode.Create));

            try {
                long len;
                using (BinaryReader reader = new BinaryReader (StreamTrack (track, out len))) {
                    int count = 0;
                    byte[] buf = new byte[ChunkLength];
                    
                    do {
                        count = reader.Read (buf, 0, ChunkLength);
                        writer.Write (buf, 0, count);
                    } while (count != 0);
                }
            } finally {
                writer.Close ();
            }
        }

        /*
        public void AddTrack (Track track) {
            if (track.Id == 0)
                track.SetId (nextTrackId++);
            
            tracks.Add (track);
            basePlaylist.AddTrack (track);

            if (TrackAdded != null)
                TrackAdded (this, new TrackArgs (track));
        }

        public void RemoveTrack (Track track) {
            tracks.Remove (track);
            basePlaylist.RemoveTrack (track);

            foreach (Playlist pl in playlists) {
                pl.RemoveTrack (track);
            }

            if (TrackRemoved != null)
                TrackRemoved (this, new TrackArgs (track));
        }

        public void AddPlaylist (Playlist pl) {
            playlists.Add (pl);

            if (PlaylistAdded != null)
                PlaylistAdded (this, new PlaylistArgs (pl));
        }

        public void RemovePlaylist (Playlist pl) {
            playlists.Remove (pl);

            if (PlaylistRemoved != null)
                PlaylistRemoved (this, new PlaylistArgs (pl));
        }
        */

        public object Clone () {
            ClientDatabase db = new ClientDatabase (this.name);
            db.id = id;
            db.persistentId = persistentId;

            //db.basePlaylist = ClonePlaylist (db, basePlaylist);
            return db;
        }
    }
}
