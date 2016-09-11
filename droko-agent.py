#!/usr/bin/env __PYTHONVER__
"""
Copyright 2016 Graphing.it

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import logging
import logging.config
import logging.handlers
import os
from os import listdir
from os.path import isfile, join
import sys
import time
import traceback
import socket
import subprocess
import datetime
import csv
import base64
import zlib
import hashlib
import json
import threading
import platform 

requests_module_loaded = True
try: 
    import requests
except ImportError:
    requests_module_loaded = False

import sleekxmpp
import ssl
from sleekxmpp.xmlstream import cert

from droko_config import *

import signal
import sys

from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read

droko_agent_version = '20160905'

_hostname = ''
xmpp = None
connected = False
sent_messages = {}
threads = []
mainthread = ''

platform_kernel_version = ''
platform_python_version = ''
platform_arch = ''
platform_os_string = ''
platform_ipaddr = ''
agent_uptime = ''

# Signal handler for Ctrl+C
def signal_handler(signal, frame):
        logger.debug('Ctrl+c pressed! Stopping agent...')
        global xmpp
        global threads
        try:
            logger.debug('Disconnecting from XMPP')
            xmpp.disconnect()
            logger.debug('Stopping sub-threads')
            p = subprocess.Popen(DROKO_INSTALL_DIR + '/' + 'kill_threads.sh', shell=True)
            #for t in threads:
            #    t.stopTheThread()
            #    t.join()             

            sys.stdout.flush()
            logger.debug('Stopping droko-agent, bye bye...')
            os.system('kill %d' % os.getpid())
        except Exception:
            pass
signal.signal(signal.SIGINT, signal_handler)

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')

# This thread is responsible for upgrading the local droko agent when called upon
class upgradeThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        logger.debug('Calling: /usr/share/droko-agent/upgrade_client.sh')
        subprocess.call(['/usr/share/droko-agent/upgrade_client.sh'], shell=True)


# XMPP class implementing the necessary callbacks to process various stages of the connection
class DrokoClient(sleekxmpp.ClientXMPP):
    """
    Droko-client bot responsible for collecting metrics and sending them to the server at graphing.it
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

        self.add_event_handler("ssl_invalid_cert", self.invalid_cert)

    def invalid_cert(self, pem_cert):
        der_cert = ssl.PEM_cert_to_DER_cert(pem_cert)
        try:
            #cert.verify('localhost', der_cert)
            pass
        except cert.CertificateError as err:
            logger.error('Problem with the SSL certificate: ', exc_info=True)
            pass

    def handle_disconnect(self, event):
        global sent_messages
        global connected
        logger.debug('Disconnecting from XMPP')

        # Clear sent_messages, so that all cached messages are re-processed when we reconnect
        try:
            sent_messages.clear()
        except:
            pass

        # Set our global variable to False
        try:
            connected = False
        except:
            pass

    def start(self, event):
        global connected
        global sent_messages
        connected = True

        logger.debug('Connected to XMPP!')
 
        # Reset any sent messages (we we reconnected from a disconnection). This will force the agent to reprocess any files and send again
        try:
            sent_messages.clear()
        except Exception:
            pass
        logger.debug('Current state of sent_messages: ' + str(sent_messages))

        try:
            self.send_presence()
            self.get_roster()
        except:
            logger.error('Restarting droko-agent due to roster error: ', exc_info=True)
            os.execl(DROKO_INSTALL_DIR + '/' + 'droko-agent.py', '')


    # Callback every time we receive a message
    def message(self, msg):
        sender = msg['from']
        message_type = msg['type']
        global sent_messages
        global xmpp


#        if any([sender.bareMatch(x) for x in jids]):
#        if 1 == 1:
        # Double check that the sender of the message is from our authorized xmpp account at Graphing.it
        if str(sender)[:64] == CONTACT[:64]:
           incoming_message = str(msg['body'])
               
           # Check if the incoming message is to upgrade our local client
           if incoming_message == 'upgrade_client_version' and str(sender)[:64] == CONTACT[:64]:
               logger.debug('Receving instrunction to upgrade droko-client: ' + incoming_message)
               # Start the background thread that will upgrade the droko-agent               
               upgradethread = upgradeThread()
               upgradethread.start()
           elif incoming_message == 'droko_ping' and str(sender)[:64] == CONTACT[:64]:
                logger.debug('Responding to ping_pong message')
                xmpp.send_message(mto=CONTACT, mbody="droko_pong", mtype='chat')
           elif incoming_message and incoming_message != 'None':
               # Alternatively, we might have received a SHA256 from the server
               # This means we need to look in our global sent_messages for a matching SHA256, and delete the file associated with it (confirming that message was sent successfully)
               if incoming_message in sent_messages:
                   file_to_remove = sent_messages[incoming_message]
                   logger.debug('Receving confirmation hash: ' + incoming_message)
                   logger.debug('Cached file to remove from disk: ' + file_to_remove)
                   # Remove the processed file from spool directory, and the hash from sent_messages
                   if file_to_remove:
                       # Remove hash from dictionary
                       del sent_messages[incoming_message]
                       # Remove the file
                       try:
                           if os.path.isfile(SPOOL_LOCATION + '/' + file_to_remove):
                               os.remove(SPOOL_LOCATION + '/' + file_to_remove)
                       except Exception:
                           logger.error('Error removing cached file on disk: ', exc_info=True)
                           pass

# checksThread is responsible to start a background script (Bash, Python, PHP, Perl, etc) and collects the STDOUT timeseries data
# One thread per check in checks.d
class checksThread(threading.Thread):
    def __init__(self, execmd):
        threading.Thread.__init__(self)
        logger.debug('Starting new checks thread: ' + execmd)
        self.execmd = execmd
        self.data = ''
        self.popen = ''
        self.signal = True
        self.threadname = execmd
 
    def run(self):
        # Start the check in a subprocess, and continously collect the output 
        self.popen = subprocess.Popen([DROKO_INSTALL_DIR + self.execmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True, universal_newlines=True, bufsize=1)
        flags = fcntl(self.popen.stdout, F_GETFL)             # get current self.popen.stdout flags
        fcntl(self.popen.stdout, F_SETFL, flags | O_NONBLOCK) # Set the non-blocking IO
        time.sleep(2)
        while self.signal:
            time.sleep(0.1)
            try:
                # Continously collect the output
                for line in iter(self.popen.stdout.readline, b''):
                    time.sleep(0.05)
                    if line:
                        self.data += line

            except Exception:
                pass
                
        # Time to go bye bye thread
        try:
            logger.debug('Terminating thread: ' + self.threadname)
            self.popen.terminate()
        except Exception:
            pass

        time.sleep(0.5)
        self.popen.poll()

    # Return all the metrics we've collected to far, and clear our local buffer for the next cycle
    def printdata(self):
        try:
            self.popen.poll()
            self.x = self.data
            logger.debug('Number of rows collected for ' + self.execmd + ': ' + str(len(self.data.split('\n'))))
            self.data = ''
            return self.x
        except: 
            return ''
    
    def stopTheThread(self):
        logger.debug('stopTheThread called on ' + self.execmd)
        self.signal = False


# This thread collects all the metrics from the mini-threads (checksThread), combines them all together into a final XMPP message and sends it off
# Also creates a cached file, incase something goes wrong with transmission so that we can reprocess and retransmit later
class mainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.now = int(time.time())
        logger.debug('Starting mainThread, current Unix time: ' + str(int(time.time())))

    def run(self):
        global threads

        time.sleep(1)
        while True:
            # Check if we were asleep for more than SPOOL_TIME seconds. If so, restart self
            # This is a protecctive measure against VM's or laptops that was put into Hibernation state, or something like that
            self.current_epoch = int(time.time())
            if (self.current_epoch - self.now) > (SPOOL_TIME + 5):
                logger.debug('mainThread was asleep for more than ' + str(SPOOL_TIME) + ' seconds, restarting droko-agent...')
                ## Shutdown any checks threads
                #for t in threads:
                #    t.stopTheThread()
                #    t.join()
                p = subprocess.Popen(DROKO_INSTALL_DIR + '/' + 'kill_threads.sh', shell=True)
                
                logger.debug('All threads stopped, sleeping for 5 seconds...')
                time.sleep(5)

                logger.debug('Self-restarting droko-agent')
                sys.stdout.flush()
                os.execl(DROKO_INSTALL_DIR + '/' + 'droko-agent.py', '')


            # Check if SPOOL_TIME has passed, and if so, collect all metrics and send to server, otherwise sleep for 1 second
            if (self.current_epoch - self.now) > (SPOOL_TIME - 1):
                self.now = self.current_epoch
                self.process()
            else: # No SPOOL_TIME has passed, sleeping
                # Sleep for 1 second
                time.sleep(1)
 

    def process(self):
        logger.debug(' ======================== Collecting data =======================')
        logger.debug(str(SPOOL_TIME) + ' seconds has passed, collecting all timeseries data from threads')
        global sent_messages
        global xmpp
        global connected
        global threads

        self.data = ''
        for t in threads:
            self.data += t.printdata()
        logger.debug('Number of rows collected in total: ' + str(len(self.data.split('\n'))))

        # Cache the results to disk before we send it off
        now = str(int(time.time() / SPOOL_TIME))
        logger.debug('Caching the collected data to disk, filename: ' + SPOOL_LOCATION + '/' + now)
        try:
            _f = open(SPOOL_LOCATION + '/' + now, 'a')
            _f.write(str(self.data))
        except IOError:
            # We should probably log here that we can't write to SPOOL_LOCATION        
            logger.error('Unable to write cached data to: ' + SPOOL_LOCATION + '/' + now, exc_info=True)
        else:
            _f.flush()
            _f.close()

        # Let's give the OS a chance to flush to disk
        # This works around some race-condition/bug where if we don't sleep, then we can't really read all the data from disk as it is still "flushing"
        time.sleep(5)

        logger.debug('Processing cached results and sending to graphing.it')
        onlyfiles = [ f for f in listdir(SPOOL_LOCATION) if isfile(join(SPOOL_LOCATION,f)) ]
        logger.debug('Files in ' + SPOOL_LOCATION + ': ' + str(sorted(onlyfiles)))

        # Get the system hostname. We do this every time, as to keep up with hostname changes while the system is running
        try:
            if socket.gethostname():
                _hostname=socket.gethostname()
            else:       
                _hostname=socket.gethostbyaddr(socket.gethostname())[0]
        except Exception:
            _hostname='unknown-hostname-please-correct'
            logger.error('Unable to determine system hostname, using default of "unknown-hostname-please-correct"', exc_info=True)

        # Override the hostname if it is set
        if HOSTNAME_OVERRIDE:
            _hostname = HOSTNAME_OVERRIDE

        # Loop through each file in the spool directory, package it and send it off to the server
        for filename in sorted(onlyfiles):
            # Only process the file if we have not processed it before and stored it in sent_messages
            if not filename in sent_messages.values():
                logger.debug('Currently processing file: ' + filename)
                # Add a header to the dictionary with other info
                d = {}
                d['header'] = {}
                d['header']['systemid'] = {}
                d['header']['systemid'] = SYSTEMID
                d['header']['hostname'] = {}
                d['header']['hostname'] = _hostname
                d['header']['message_type'] = {}
                d['header']['message_type'] = 'scheduled_results'
                d['header']['platform_kernel_version'] = {}
                d['header']['platform_kernel_version'] = platform_kernel_version
                d['header']['platform_python_version'] = {}
                d['header']['platform_python_version'] = platform_python_version
                d['header']['platform_arch'] = {}
                d['header']['platform_arch'] = platform_arch
                d['header']['platform_os_string'] = {}
                d['header']['platform_os_string'] = platform_os_string
                d['header']['platform_ipaddr'] = {}
                d['header']['platform_ipaddr'] = platform_ipaddr
                d['header']['droko_agent_version'] = {}
                d['header']['droko_agent_version'] = droko_agent_version
                d['header']['droko_agent_uptime'] = {}
                d['header']['droko_agent_uptime'] = agent_uptime
                d['header']['metadata'] = {}
 
                # Try and get system uptime in seconds 
                try:
                    with open('/proc/uptime', 'r') as f:
                        uptime_seconds = round(int(float(f.readline().split()[0])),4)
                        d['header']['platform_uptime_seconds'] = {}
                        d['header']['platform_uptime_seconds'] = uptime_seconds
                except:
                    d['header']['platform_uptime_seconds'] = {}
                    d['header']['platform_uptime_seconds'] = ''
                  
                # Add a sub-dictionary, which will hold metric values
                d['values'] = []
                json_body = {}
                  
                # Open up the file, and parse through it building an "internal" json like dictionary + array 
                with open(SPOOL_LOCATION + '/' + filename) as csvfile:
                    # Read our file as CSV file, and use the following column names as identifiers
                    reader = csv.DictReader(csvfile, ['epoch','checkname','checkresult','metadata'])
                    # Try reading a row from the file. If we get an exception (because say the line is corrupt)
                    # then we ignore the error (and the line), and continue with the next line
                    try: 
                        for r in reader:
                            row = {}
                            row['epoch']       = r['epoch']
                            row['checkname']   = r['checkname']
                            row['checkresult'] = r['checkresult']
                            row['metadata']    = r['metadata']
     
                            # Seems in Python we need to create empty subkeys if they don't exist
                            checkname = row['checkname']
                            try:
                                testval = json_body[checkname]
                            except KeyError:
                                json_body[checkname] = {}
                            try:
                                testval = json_body[checkname]['columns']
                            except KeyError:
                                json_body[checkname]['columns'] = {}
                            try:
                                testval = json_body[checkname]['name']
                            except KeyError:
                                json_body[checkname]['name'] = {}
                            try:
                                testval = json_body[checkname]['points']
                            except KeyError:
                                json_body[checkname]['points'] = []

                            # Add the metadata
                            try:
                                d['header']['metadata'][SYSTEMID + '.' + row['checkname']] = {'metadata':row['metadata'], 'lastval':str(float(row['checkresult']))}
                            except:
                                pass
     
     
                            # Try and save the metrics to our internal json structre. If we can't, then ignore this row
                            try:
                                json_body[checkname]['name'] = SYSTEMID + "." + checkname 
                                json_body[checkname]['columns'] = ["time", "value"]
                                # Try and convert the checkresult value to a float, if it can't, then save it as a string
                                if row['checkresult'] == '':
                                    dummyval = 1
                                else:
                                    try:
                                        datapointvalue = float(row['checkresult']) * 1
                                    except:
                                        datapointvalue = str(row['checkresult'])
     
    
                                    # If the metric isn't an empty value, then add to the json structure 
                                    if str(datapointvalue).strip() != '':
                                        try:
                                            json_body[checkname]['points'].append([int(row['epoch']), datapointvalue])
                                        except:
                                            pass # Ignore and continue
                                    else:
                                        # empty datapointvalue
                                        pass
     
                            except:
                                pass
     
                    # Handle exception thrown if the csv line is corrupt
                    except Exception as e: 
                        logger.error('Unable to process CSV line: ', exc_info=True)
                        pass
     
                # Once we are done converting the file to an internal json structure, we can now add it properly to d
                for key, value in json_body.items():
                    d['values'].append(value)
     
                # Convert the dictionary to JSON
                jsn = json.dumps(d)
     
                # Compress the dictionary, and give a base64 encoded string that is safe to transmit over the messaging layer
                if sys.version_info[:2] == (2, 7):    # python 2.7
                    result_string = base64.standard_b64encode(zlib.compress(jsn.decode()))
                if sys.version_info[:1] == (3,):      # python 3.x
                    result_string = base64.standard_b64encode(zlib.compress(bytes(jsn, 'UTF-8')))
     
                # SHA256 the message
                hash_object = hashlib.sha256(result_string)
                hex_digest = hash_object.hexdigest()
     
                # Send it to the server, if we are connected
                # If we are not connected, we'll just keep spooling until it reaches MAX_CACHE_TIME
                logger.debug('Are we connected to XMPP: ' + str(connected))
                if connected:
                    # Only send the results to the server if we have not sent it before and still waiting for a server response
                    if not hex_digest in sent_messages and not filename in sent_messages.values():
                        xmpp.send_message(mto=CONTACT,
                                          mbody=bytes.decode(result_string),
                                          mtype='chat')
 
     
                        # Put the SHA256 generated above in the list
                        # If we get the same response (same SHA256) back later, we can remove the file from disk
                        # If we don't get the response back, we must process the file again and resend
                        sent_messages[hex_digest] = {}
                        sent_messages[hex_digest] = filename
                
                        logger.debug('Bytes of base64 string: ' + str(len(result_string)) + ', SHA256: ' + str(hex_digest))
                else:
                    # If we are not connected, make sure our tracking list is empty, so that when we reconnect later, 
                    # we can re-process all cached results
                    logger.debug('Not connected to XMPP, delaying sending messages')
                    try:
                        sent_messages.clear()
                    except Exception:
                        pass
            
                # Lastly if this input file is more than MAX_CACHE_TIME old, we can delete it and not have to process it again
                try:
                    if time.time() - os.path.getmtime(SPOOL_LOCATION + '/' + filename) > MAX_CACHE_TIME:
                        logger.debug('Filename: ' + filename + ', expired beyond MAX_CACHE_TIME (' + str(MAX_CACHE_TIME) + ', deleting from disk')
                        os.remove(SPOOL_LOCATION + '/' + filename)
                        # Also remove from the sent_messages dictionary, we don't care anymore if the server got the message or not
                        if hex_digest in sent_messages:
                            try:
                                del sent_messages[hex_digest]     
                            except Exception:
                                pass
                except:
                    pass 
    

if __name__ == "__main__":
    # Setup logging
    if os.path.exists(DROKO_INSTALL_DIR + '/logging.json'):
        with open(DROKO_INSTALL_DIR + '/logging.json', 'rt') as f:
            logging.config.dictConfig(json.load(f))

    #logging.config.fileConfig(DROKO_INSTALL_DIR + '/logging.ini')
    logger = logging.getLogger('droko-agent')
    logger.info('Starting droko-agent, version ' + droko_agent_version + ' using Python ' + str(sys.version_info[:3]))

    # Get information about our runtime environment
    platform_kernel_version = platform.release()
    platform_python_version = platform.python_version()
    platform_arch = platform.machine()
    platform_os_string = platform.dist()[0] + ' ' + platform.dist()[1] + ' ' + platform.dist()[2]
    agent_uptime = str(int(time.time()))
    logger.debug('Platform Python version: ' + platform.python_version())
    logger.debug('Platform release: ' + platform.release())
    logger.debug('Platform arch: ' + platform.machine())
    logger.debug('Platform OS String: ' + str(platform.dist()))
   
    CLIENT_JID = JID
    CLIENT_PASSWORD = JIDPASSWORD
    AUTHORIZED_JIDS = [ CONTACT ]

    # Add scheduled jobs from checks.d, each into its own thread
    for subdir, dirs, files in os.walk(DROKO_INSTALL_DIR + '/checks.d/', followlinks=True):
        logger.debug('Files in checks.d: ' + str(files))
        for file in files:
            if os.access(DROKO_INSTALL_DIR + '/checks.d/' + file, os.X_OK):
                logger.debug('Loading job for: ' + file)
                thread = checksThread('/checks.d/' + file)
                threads += [thread]
                thread.start()

    # Load the mainThread that will periodically collect from the checkTreads
    mainthread = mainThread()
    mainthread.start()
    logger.debug('mainthread.start() called')

    # Setup the droko agent and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    logger.debug('Calling DrokoClient xmpp class with username: ' + CLIENT_JID)
    logger.debug('Authorized XMPP Contact: ' + CONTACT)
    xmpp = DrokoClient(CLIENT_JID, CLIENT_PASSWORD)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping


    # Loop until the program is terminated.
    # In case of connection problems and/or exceptions, the client is
    # run again after a delay.
    while True:
        # Find out what our Internet live IP is. This is to show on the dashboard
        try:
            if requests_module_loaded:
                ipinfo = requests.get('http://ipinfo.io')
                platform_ipaddr = ipinfo.json()['ip']
        except:
            platform_ipaddr = ''
            pass

        logger.debug('Trying to connect to graphing.it on the xmpp protocol')

        try:
            if xmpp.connect(HOST, reattempt=True):
                xmpp.add_event_handler("disconnected", xmpp.handle_disconnect)
                xmpp.process(block=True)
            else:
                logger.debug('Unable to connect to graphing.it on XMPP, sleeping for 30 seconds')
        except Exception:
            logger.error('Exception connecting to graphing.it on XMPP: ', exc_info=True)
            pass

        logger.debug('Unable to connect to graphing.it on XMPP, sleeping for 30 seconds')
        connected = False
        time.sleep(30)
