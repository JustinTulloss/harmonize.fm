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
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using DMP.Server;
using DMP.Data;

namespace DAAP {

    public class Playlist : PlaylistBase {
 
        //private List<Track> tracks = new List<Track> ();
        //private List<int> containerIds = new List<int> ();



        /*
        public Track this[int index] {
            get {
                if (tracks.Count > index)
                    return tracks[index];
                else
                    return null;
            }
            set { tracks[index] = value; }
        }*/
        
        public Playlist (Int32 id, string name) : base (id, name) {
        }

        public Playlist(Int32 id) : base(id) { }

        public Playlist(PlaylistBase copyList) : base(copyList.Id, copyList.Name)
        {
            songs = copyList.Songs;
        }

      
        /*
        internal int GetContainerId (int index) {
            return (int) containerIds[index];
        }*/

        /// <summary>
        /// Makes playlist into a ContentNode. Adds deleted ids as
        /// special nodes marked as deleted.
        /// </summary>
        /// <param name="deletedIds"></param>
        /// <returns></returns>
        internal ContentNode ToTracksNode (int[] deletedIds) {
            ArrayList trackNodes = new ArrayList ();

            for (int i = 0; i < songs.Count; i++) {
                TrackBase track = this[i] as TrackBase;
                trackNodes.Add (DAAP.Track.ToPlaylistNode (track, i));
            }

            ArrayList deletedNodes = null;
            if (deletedIds.Length > 0) {
                deletedNodes = new ArrayList ();

                foreach (int id in deletedIds) {
                    deletedNodes.Add (new ContentNode ("dmap.itemid", id));
                }
            }

            ArrayList children = new ArrayList ();
            children.Add (new ContentNode ("dmap.status", 200));
            children.Add (new ContentNode ("dmap.updatetype", deletedNodes == null ? (byte) 0 : (byte) 1));
            children.Add (new ContentNode ("dmap.specifiedtotalcount", songs.Count));
            children.Add (new ContentNode ("dmap.returnedcount", songs.Count));
            children.Add (new ContentNode ("dmap.listing", trackNodes));

            if (deletedNodes != null)
                children.Add (new ContentNode ("dmap.deletedidlisting", deletedNodes));
            
            
            return new ContentNode ("daap.playlistsongs", children);
        }

        internal ContentNode ToNode (bool basePlaylist) {

            ArrayList nodes = new ArrayList ();

            nodes.Add (new ContentNode ("dmap.itemid", id));
            nodes.Add (new ContentNode ("dmap.persistentid", (long) id));
            nodes.Add (new ContentNode ("dmap.itemname", name));
            nodes.Add (new ContentNode ("dmap.itemcount", songs.Count));
            if (basePlaylist)
                nodes.Add (new ContentNode ("daap.baseplaylist", (byte) 1));
            
            return new ContentNode ("dmap.listingitem", nodes);
        }

        internal static Playlist FromNode (ContentNode node) {

            Int32 tempId = 0;
            String tempName = "Unnamed Playlist";
            foreach (ContentNode child in (ContentNode[]) node.Value) {
                switch (child.Name) {
                case  "daap.baseplaylist":
                    return null;
                case "dmap.itemid":
                    tempId = (int) child.Value;
                    break;
                case "dmap.itemname":
                    tempName = (string) child.Value;
                    break;
                default:
                    break;
                }
            }

            return new Playlist(tempId, tempName);
        }

        internal void Update (Playlist pl) {
            if (pl.Name == name)
                return;

            Name = pl.Name;
        }

        internal int LookupIndexByContainerId (int id) {
            if (songs[id] != 0)
                return id;
            else
                return -1;
        }

        public IList<Track> Tracks
        {
            get
            {
                List<Track> tracks = new List<Track>();
                if (getTrackData != null)
                {
                    foreach (Int32 song in songs)
                        tracks.Add(new Track(getTrackData(song)));

                    return new ReadOnlyCollection<Track>(tracks);
                }
                else
                    return null;
            }
        }

        public override object Clone()
        {
            Playlist plClone = new Playlist(this.id, this.name);
            plClone.songs = this.songs;

            return plClone;
        }

    }

}
