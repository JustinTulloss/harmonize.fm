namespace Nwc.XmlRpc
{
  using System;
  using System.Collections;
  using System.Diagnostics;
  using System.IO;
  using System.Net;
  using System.Net.Sockets;
  using System.Text;
  using System.Threading;
  using System.Xml;

public class XmlRpcServer : IEnumerable
  {
    private Hashtable _handlers;
    private XmlRpcSystemObject _system;
		
    //The constructor which make the TcpListener start listening on the
    //given port. It also calls a Thread on the method StartListen(). 
    public XmlRpcServer()
      {
	_handlers = new Hashtable();
	_system = new XmlRpcSystemObject(this);
      }

    public IEnumerator GetEnumerator()
      {
	return _handlers.GetEnumerator();
      }

    public Object this [String name]
      {
	get { return _handlers[name]; }
      }
  
    public StringWriter ProcessRequest(StreamReader req)
      {
	XmlRpcRequest rpc = XmlRpcRequestDeserializer.Parse(req);

	XmlRpcResponse resp = new XmlRpcResponse();
	Object target = _handlers[rpc.MethodNameObject];
	
	if (target == null)
	  {
	    resp.SetFault(-1, "Object " + rpc.MethodNameObject + " not registered.");
	  }
	else
	  {
	    try
	      {
		resp.Value = rpc.Invoke(target);
	      }
	    catch (XmlRpcException e)
	      {
		resp.SetFault(e.Code, e.Message);
	      }
	    catch (Exception e2)
	      {
		resp.SetFault(-1, e2.Message);
	      }
	  }

	Logger.WriteEntry(resp.ToString(), EventLogEntryType.Information);
    //TODO: Need to fix this up to actually return something rather than
    //try to use the no longer existent HTTP server.
    StringWriter xmlWriter = new StringWriter();
	XmlTextWriter xml = new XmlTextWriter(xmlWriter);
	XmlRpcResponseSerializer.Serialize(xml, resp);
    return xmlWriter;
      }

    ///<summary>
    ///Add an XML-RPC handler object by name.
    ///</summary>
    public void Add(String name, Object obj)
      {
	_handlers.Add(name,obj);
      }
  }
}
