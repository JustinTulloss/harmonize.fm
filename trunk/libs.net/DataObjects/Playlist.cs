using System;
using System.Collections.Generic;
using System.Collections;
using System.Text;
using DMP;

namespace DMP.Data
{

    //Delegates. These allow the playlist to operate between different
    //databases. The server has one way of filling in track data and
    //the client has a totally different way. So they both can register
    //their respective functions with this class so that a logical
    //operation (such as playlist[playlistindex]) will return a track
    public delegate TrackBase TrackDataHandler(int songid);
    //Function to write back all this data to the database itself
    public delegate Error PlaylistWriteBackHandler(int id, string name, ArrayList songs);
    //Don't know what this does yet
    public delegate void PlaylistTrackHandler(object o, int index, TrackBase track);

    public class PlaylistBase : ICloneable
    {
        //A dictionary where the key is just some playlist index that doesn't
        //matter and the values are the songids to be translated into actual tracks
        protected List<Int32> songs = new List<Int32>();

        //Something to keep track of our dictionary keys
        private static int nextPlIndex = 1;

        //Name of the playlist
        protected string name = String.Empty;
        protected Int32 id = -1;//ID of the playlist

        //private instances of the above delegates
        protected TrackDataHandler getTrackData;
        protected PlaylistWriteBackHandler writePlaylistBack;

        public event PlaylistTrackHandler TrackAdded;
        public event PlaylistTrackHandler TrackRemoved;
        public event EventHandler NameChanged;

        //Constructors
        public PlaylistBase(Int32 newId)
        {
            id = newId;
        }

        public PlaylistBase(Int32 newId, string newName)
        {
            id = newId;
            name = newName;
        }

        //Adds a song to the memory based playlist. You need to call
        //the Writeback delegate for it to go into the database.

        public void InsertTrack(int index, TrackBase track)
        {
            InsertTrack(index, track, songs.Count + 1);
        }

        internal void InsertTrack(int index, TrackBase track, int id)
        {
            songs[index]= track.Id;
            //containerIds.Insert(index, id);

            if (TrackAdded != null)
                TrackAdded(this, index, track);
        }

        public void RemoveSong(Int32 plIndex)
        {
            songs.Remove(songs[plIndex]);
        }

        public void Clear()
        {
            songs.Clear();
        }

        public void AddTrack(Int32 songid)
        {
            songs.Add(songid);

            //if (TrackAdded != null)
            //    TrackAdded(this, songs.Count - 1, track);
        }


        public void AddTrack(TrackBase track)
        {
            AddTrack(track, songs.Count + 1);
        }

        internal void AddTrack(TrackBase track, int id)
        {
            songs.Add(track.Id);

            if (TrackAdded != null)
                TrackAdded(this, songs.Count - 1, track);
        }

        public void RemoveAt(int index)
        {
            songs.RemoveAt(index);

            //if (TrackRemoved != null)
            //    TrackRemoved(this, index, track);
        }

        public bool RemoveTrack(TrackBase track)
        {
            int index;
            bool ret = false;

            while ((index = IndexOf(track)) >= 0)
            {
                ret = true;
                RemoveAt(index);
            }

            return ret;
        }

        public int IndexOf(TrackBase track)
        {
            return songs.IndexOf(track.Id);
        }

        virtual public TrackBase this[int plIndex]
        {
            get
            {
                Int32 songId = (Int32) songs[plIndex];
                if (getTrackData != null && songId != null)
                    return getTrackData(songId);
                else
                {
                    Exception noTrackHandler = new Exception("No track handling function defined");
                    throw noTrackHandler;
                }
            }
        }

        public Int32 Id
        {
            get
            {
                return id;
            }
            set
            {
                id = value;
            }
        }

        public string Name
        {
            get
            {
                return name;
            }
            set
            {
                name = value;
            }
        }

        public TrackDataHandler TrackMetaHandler
        {
            set
            {
                getTrackData = value;
            }
        }

        public List<Int32> Songs
        {
            get
            {
                return songs;
            }
        }

        public virtual object Clone()
        {
            PlaylistBase plClone = new PlaylistBase(this.id, this.name);
            plClone.songs = this.songs;

            return plClone;
        }
    }
}
