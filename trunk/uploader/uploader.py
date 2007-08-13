import os
from urllib2 import Request, urlopen
import mimetools, mimetypes

import sys
sys.path.insert(0,'../libs.py/')
import guid

DEFAULT_URL = "http://localhost:2985/postfile"
DEFAULT_HOST = "localhost:2985"
DEFAULT_FILE = "test.mp3"

SUCCESS = "Great work kiddos!"
HTTP_OK = 200

class uploader:

    def __init__(self, user, url=DEFAULT_URL, filename=DEFAULT_FILE ):
        self.user = user
        self.url = url
        self._fd = None
        self._set_fname(filename)

    def upload(self):
        if not (self.url and self.fname):
            raise Exception("You must set the url and file to upload first")

        req = self.build_request({"user":self.user}, (("file", self.fname, self._fd.read()),))
        resp = urlopen(req)

        msg = resp.read()
        resp.close()
        if msg != SUCCESS:
            raise Exception(msg)
    #
    #
    # build_request/encode_multipart_formdata code is from 
    # www.voidspace.org.uk/atlantibots/pythonutils.html
    #
    # --Modified to use guid instead of mimetools.choose_boundary 
    #   since that did not properly handle exceptions (JMT)
    #
    def build_request(self, fields, files, txheaders=None):
        """
        Given the fields to set and the files to encode it returns a fully 
        formed urllib2.Request object.  You can optionally pass in additional 
        headers to encode into the opject. (Content-type and Content-length 
        will be overridden if they are set). 

        fields is a sequence of (name, value) elements for regular 
        form fields - or a dictionary.

        files is a sequence of (name, filename, value) elements for data 
        to be uploaded as files.    
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        if not txheaders: txheaders = {}
        txheaders['Content-type'] = content_type
        txheaders['Content-length'] = str(len(body))

        return Request(self.url, body, txheaders)     

    def encode_multipart_formdata(self,fields, files,
        BOUNDARY = '-----'+guid.generate()+'-----'):
        """ Encodes fields and files for uploading.
        fields is a sequence of (name, value) elements for regular form fields
        - or a dictionary.

        files is a sequence of (name, filename, value) elements for data to 
        be uploaded as files.

        Return (content_type, body) ready for urllib2.Request instance
        You can optionally pass in a boundary string to use or 
        we'll let mimetools provide one.
        """    
        CRLF = '\r\n'
        L = []
        if isinstance(fields, dict):
            fields = fields.items()
        for (key, value) in fields:   
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                % (key, filename))
            L.append('Content-Type: %s' % filetype)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        
        # XXX what if no files are encoded
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def _get_fname(self):
        return self._fname

    def _set_fname(self, fname):
        self._fname = fname

        if self._fd != None:
            self._fd.close()

        self._fd = open(fname,'rb')

    fname = property(_get_fname, _set_fname)

if __name__ == "__main__":
    u = uploader("0000")
    u.upload()
    print "Success!"
