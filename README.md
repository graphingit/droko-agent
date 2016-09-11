[droko-agent](https://graphing.it)

## Introduction

droko-agent is the custom agent responsible for collecting timeseries measurements, packaged in json and sends them off to (https://graphing.it) for storage and visualization. 
Written in Python (compatible with Python 2.7 and 3.x), it uses the sleekxmpp XMPP library to connect with graphing.it for its communication and transport layer. 

Using droko-agent requires an account with (http://graphing.it/sign-up), as the packaged results are stored against the subscribed account.

More developer documentation, for example how to write your own custom timeseries plugin, can be found at: (https://graphing.it/documentation)

![](https://graphing.it/images/slider_img1_optimized.png)

## License

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
