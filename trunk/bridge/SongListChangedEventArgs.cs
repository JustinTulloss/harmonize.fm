using System;
using System.Collections.Generic;
using System.Data;
using System.Text;

namespace DMP {
	/// <summary>
	/// The arguments for a SongListChange event
	/// </summary>
	public class SongListChangedEventArgs : EventArgs {
		/// <summary>
		/// The new data table
		/// </summary>
		public DataTable NewTable;

		/// <summary>
		/// True if the SongDelta contains songs to add,
		/// false if it contains songs to remove
		/// </summary>
		public bool SongsAdded;

		/// <summary>
		/// The list of songs that were either added or removed
		/// </summary>
		public LinkedList<Int64> SongDelta;

		/// <summary>
		/// Creates a new instance of the SongListChangeEventArgs
		/// </summary>
		/// <param name="theTable">The new DataTable</param>
		public SongListChangedEventArgs(DataTable theTable, 
			bool added, LinkedList<Int64> theDelta) {
			this.NewTable = theTable;
			this.SongsAdded = added;
			this.SongDelta = theDelta;
		}


	}
}
