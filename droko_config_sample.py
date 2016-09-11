# Copyright 2016 Graphing.it
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#
# Where the XMPP server is located. 
# Do not modify this value
HOST = ('xmpp.graphing.it','5222')

# 
# Location where Droko is installed by default
# It is generally not a good idea to change this location, as there are quite a few dependencies on this location
DROKO_INSTALL_DIR = '/usr/share/droko-agent'

#
# Username droko will connect to the server as. 
# This account is automatically created.
# Do not modify this value.
#
JID = '__JID__'

#
# Password droko will connect to the server as. 
# The password is automatically created.
# Do not modify this value.
#
JIDPASSWORD = '__JIDPASSWORD__'

#
# The unique System ID generated upon installation. 
# The systemid is automatically created.
# Do not modify this value.
#
SYSTEMID = '__SYSTEMID__'

#
# The JID of the server droko will talk to.
# Timeseries data will be sent to this address.
# Do not modify this value.
#
CONTACT = '__CONTACT__'

#
# Users (JIDs - like an email address) who are allowed to contact Droko and query it. 
# Usually this is just your user, CONTACT, but you may wish to add friends, team members,
# or other JIDs of yours.
# For example:
# AUTHORIZED_CONTACTS = [ CONTACT, 'friend@jabber.org', 'colleague@jabber.work.com' ]
#
AUTHORIZED_CONTACTS = [ CONTACT ]

#
# If you don't want to use the system's hostname, but want to override it with something else
# Default value: <empty>
HOSTNAME_OVERRIDE = ''

#
# Location on disk to spool results. This is a temporary space where we spool results of any/all checks until 
# the next SPOOL_TIME (see below) interval 
# Default value: /var/lib/droko/spool
SPOOL_LOCATION = '/var/lib/droko/spool'

#
# This is the amount of time we will cache results before we attempt to send timeseries results back to the server.
# Sending all results between intervals as one data packet is more resource friendly than doing many small transmits
# All check results will be written to an interval file, which is current_unix_epoch / SPOOL_TIME
# Default value: 60 (seconds)
SPOOL_TIME=60

#
# This is the maximum amount of time we will cache results on disk locally. Checks that have not been submitted to the server
# by this timeout will be discarded. This is to prevent the disk from filling up (although this happens very slowly).
# Depending on the number of checks and how often they run, disk usage is around 20 - 30 MiB a day
# Default value: 86400 (in seconds, which equals 1 day)
MAX_CACHE_TIME=86400

#
# This variable is unused currently. Please keep as is.
AUTHORIZED_COMMANDS = { }
