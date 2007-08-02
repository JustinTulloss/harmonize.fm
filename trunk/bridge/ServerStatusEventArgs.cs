using System;
using System.Collections.Generic;
using System.Text;

namespace DMP {
	/// <summary>
	/// The arguments for a ServerAdded event or a ServerRemoved event
	/// </summary>
	public class ServerStatusEventArgs : EventArgs {
		public enum ServerStatusList {
			Connecting,
			Connected,
			Disconnecting,
			Disconnected
		}

		/// <summary>
		/// The name of the server
		/// </summary>
		private string myServerName;

		/// <summary>
		/// 
		/// </summary>
		private ServerStatusList myServerStatus;

		/// <summary>
		/// Creates a new instance of ServerAddedEventArgs
		/// </summary>
		/// <param name="theName">The name of the new server</param>
		/// <param name="isConnected">True if the server is connected, false otherwise</param>
		public ServerStatusEventArgs(String theName, ServerStatusList theServerStatus) {
			this.myServerName = theName;
			this.myServerStatus = theServerStatus;
		}

		/// <summary>
		/// True if the server is connected, false otherwise
		/// </summary>
		public ServerStatusList ServerStatus {
			get {
				return this.myServerStatus;
			}
		}

		/// <summary>
		/// The name of the server
		/// </summary>
		public string ServerName {
			get {
				return this.myServerName;
			}
		}
	}
}
