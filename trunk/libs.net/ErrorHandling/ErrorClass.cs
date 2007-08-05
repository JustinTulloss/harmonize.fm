//Justin Tulloss
//01/10/2007
//
//A class library for returning errors to a calling function

using System;
using System.Collections;

namespace DMP
{
	/// <summary>
	/// This is the Error class. All user facing functions should return this
	/// object. If there was an error, a function should fill in the message.
	/// Otherwise, it should return null
	/// </summary>
	public class Error
	{
		/// <summary>
		/// The actual error message. This is private.
		/// </summary>
		private string message;

		/// <summary>
		/// The error code. Private.
		/// </summary>
		private int code;

		/// <summary>
		/// Constructor that sets default error message.
		/// </summary>
		public Error()
		{
			message = "An error occurred";
			code = 0;
		}

		/// <summary>
		/// Constructor allows setting the message and code.
		/// </summary>
		/// <param name="errMessage" type="string">The error message</param>
		/// <param name="errCode" type="string">The error code</param>
		public Error(string errMessage, int errCode)
		{
			message = errMessage;
			code = errCode;
		}

		/// <summary>
		/// Constructor allows setting the message.
		/// </summary>
		/// <param name="errMessage" type="string">The error message</param>
		public Error(string errMessage)
		{
			message = errMessage;
			code = 0;
		}

		/// <summary>
		/// Constructor allows setting the message and code through a
		/// hashtable that my have been returned via XML-RPC.
		/// </summary>
		/// <param name="errMessage" type="Hashtable">
		/// 	The error hashtable
		/// </param>
		public Error(Hashtable errStruct)
		{
			if (errStruct.ContainsKey("errorMessage"))
			{
				message = (string)errStruct["errorMessage"];
			}
			if (errStruct.ContainsKey("errorCode"))
			{
				code = (int)errStruct["errorCode"];
			}
		}

		/// <summary>
		/// A parameter that allows a user to read the error message
		/// </summary>
		/// <returns type="string">The error message </returns>
		public string Message
		{
			protected set
			{
				message=value;
			}
			get
			{
				return message;
			}
		}

		/// <summary>
		/// A parameter that allows a user to read the error code
		/// </summary>
		/// <returns type="string">The error code</returns>
		public int Code
		{
			protected set
			{
				code=value;
			}
			get
			{
				return code;
			}
		}

		/// <summary> 
		/// A property that returns a hashtable of the message
		/// and code. This can be sent across the wire via XML-RPC
		/// </summary>
		/// <returns type="Hashtable">The error code and message</returns>
        public Hashtable Structure
		{
			get
			{
                Hashtable thisError = new Hashtable();
                thisError.Add("errorMessage", message);
                thisError.Add("errorCode", code);

				return thisError;
			}
		}
	}

#if false
    public class ErrorStruct : Hashtable
    {
        internal ErrorStruct(string message, int code)
        {
            Add("errorMessage", message);
            Add("errorCode", code);
        }
    }
#endif
}
