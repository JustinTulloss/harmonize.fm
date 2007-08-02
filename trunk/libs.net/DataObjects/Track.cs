using System;
using System.Collections.Generic;
using System.Text;

namespace DMP.Data
{
    public class TrackBase : ICloneable 
    {

        protected string artist;
        protected string album;
        protected string title;
        protected int year;
        protected string format;
        protected TimeSpan duration;
        protected int id;
        protected int size;
        protected string genre;
        protected int trackNumber;
        protected int trackCount;
        protected string fileName;
        protected DateTime dateAdded = DateTime.Now;
        protected DateTime dateModified = DateTime.Now;
        protected short bitrate;

        public event EventHandler Updated;

        public TrackBase(TrackBase copyTrack)
        {
            artist = copyTrack.artist;
            album = copyTrack.album;
            title = copyTrack.title;
            year = copyTrack.year;
            format = copyTrack.format;
            duration = copyTrack.duration;
            id = copyTrack.id;
            size = copyTrack.size;
            genre = copyTrack.genre;
            trackNumber = copyTrack.trackNumber;
            trackCount = copyTrack.trackCount;
            fileName = copyTrack.fileName;
            dateAdded = copyTrack.dateAdded;
            dateModified = copyTrack.dateModified;
            bitrate = copyTrack.bitrate;
            Updated = copyTrack.Updated;
        }

        public TrackBase()
        { }

        public string Artist {
            get { return artist; }
            set {
                artist = value;
                EmitUpdated ();
            }
        }
        
        public string Album {
            get { return album; }
            set {
                album = value;
                EmitUpdated ();
            }
        }
        
        public string Title {
            get { return title; }
            set {
                title = value;
                EmitUpdated ();
            }
        }
        
        public int Year {
            get { return year; }
            set {
                year = value;
                EmitUpdated ();
            }
        }
        
        public string Format {
            get { return format; }
            set {
                format = value;
                EmitUpdated ();
            }
        }
        
        public TimeSpan Duration {
            get { return duration; }
            set {
                duration = value;
                EmitUpdated ();
            }
        }
        
        public int Id {
            get { return id; }
        }
        
        public int Size {
            get { return size; }
            set {
                size = value;
                EmitUpdated ();
            }
        }
        
        public string Genre {
            get { return genre; }
            set {
                genre = value;
                EmitUpdated ();
            }
        }
        
        public int TrackNumber {
            get { return trackNumber; }
            set {
                trackNumber = value;
                EmitUpdated ();
            }
        }
        
        public int TrackCount {
            get { return trackCount; }
            set {
                trackCount = value;
                EmitUpdated ();
            }
        }
        
        public string FileName {
            get { return fileName; }
            set {
                fileName = value;
                EmitUpdated ();
            }
        }
        
        public DateTime DateAdded {
            get { return dateAdded; }
            set {
                dateAdded = value;
                EmitUpdated ();
            }
        }
        
        public DateTime DateModified {
            get { return dateModified; }
            set {
                dateModified = value;
                EmitUpdated ();
            }
        }

        public short BitRate {
            get { return bitrate; }
            set { bitrate = value; }
        }

        public object Clone () {
            TrackBase track = new TrackBase ();
            track.artist = artist;
            track.album = album;
            track.title = title;
            track.year = year;
            track.format = format;
            track.duration = duration;
            track.id = id;
            track.size = size;
            track.genre = genre;
            track.trackNumber = trackNumber;
            track.trackCount = trackCount;
            track.fileName = fileName;
            track.dateAdded = dateAdded;
            track.dateModified = dateModified;
            track.bitrate = bitrate;

            return track;
        }

        public override string ToString () {
            return String.Format ("{0} - {1}.{2} ({3}): {4}", artist, title, format, duration, id);
        }

        public void SetId (int id) {
            this.id = id;
        }

        private bool Equals(TrackBase track)
        {
            return artist == track.Artist &&
                album == track.Album &&
                title == track.Title &&
                year == track.Year &&
                format == track.Format &&
                duration == track.Duration &&
                size == track.Size &&
                genre == track.Genre &&
                trackNumber == track.TrackNumber &&
                trackCount == track.TrackCount &&
                dateAdded == track.DateAdded &&
                dateModified == track.DateModified &&
                bitrate == track.BitRate;
        }

        public void Update(TrackBase track)
        {
            if (Equals(track))
                return;

            artist = track.Artist;
            album = track.Album;
            title = track.Title;
            year = track.Year;
            format = track.Format;
            duration = track.Duration;
            size = track.Size;
            genre = track.Genre;
            trackNumber = track.TrackNumber;
            trackCount = track.TrackCount;
            dateAdded = track.DateAdded;
            dateModified = track.DateModified;
            bitrate = track.BitRate;

            EmitUpdated();
        }

        private void EmitUpdated()
        {
            if (Updated != null)
                Updated(this, new EventArgs());
        }
    }
}
