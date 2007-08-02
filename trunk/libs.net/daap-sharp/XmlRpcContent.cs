using System;
using System.Collections.Generic;
using System.Text;
using Nwc.XmlRpc;

namespace DAAP
{
    internal class XmlRpcContent
    {
        string responseMessage;

        internal XmlRpcContent()
        {}

        internal XmlRpcContent(string message)
        {
            responseMessage = message;
        }

        internal XmlRpcContent(ContentNode node) 
        {
            //Get message
        }

        internal string Message
        {
            get
            {
                return responseMessage;
            }
            set
            {
                responseMessage = value;
            }
        }

        internal ContentNode ToNode () {
            //Send an xmlrpc response node of the message
            return new ContentNode ("dmp.xmlrpcresponse",
                                    new ContentNode ("dmp.xmlrpcmessage", responseMessage));
        }
    }
}
