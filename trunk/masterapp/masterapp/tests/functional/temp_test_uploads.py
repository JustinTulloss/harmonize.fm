#this is a test for file uploading, but is not integrated with the pylons
#test environment just yet
#The result will be a the mp3 file in the /tmp directory with its hash value
#as the new filename

import httplib
import hashlib

src_file = open("./02 Vacileo.mp3", "r")
src_data = src_file.read()

src_hash = hashlib.sha1(src_data).hexdigest()
upload_url = '/uploads/' + src_hash

rubicon_conn = httplib.HTTPConnection('localhost:2985')
rubicon_conn.request('POST', upload_url, src_data)
response = rubicon_conn.getresponse()
response.read() #this is '1' on success

#there should now be a file in the tmp directory with no diff from the source

