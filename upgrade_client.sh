#!/bin/bash

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

# Get the CONTACT value from the droko config file
CONTACT=$(cat /usr/share/droko-agent/droko_config.py | grep 'CONTACT =' | awk '{print $3}' | cut -d "'" -f 2 | cut -d '@' -f 1)

# Check that it is not empty
if [ -n "$CONTACT" ]
then
    # Upgrade the client
    /usr/bin/wget -q -O - https://graphing.it/install.sh | bash -s -- $CONTACT --upgrade & > /usr/share/droko-agent/logs/upgrade.stdout 2> /usr/share/droko-agent/logs//upgrade.error
fi
