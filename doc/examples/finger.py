############################################################################
##
## Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2015-2017 BalaSys IT Ltd, Budapest, Hungary
##
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##
############################################################################
# Demonstrates the usage of the built in Finger proxy. Forwards
# finger connections from 127.0.0.1:7979 to 127.0.0.1:79
#


from Zorp.Zorp import *
from Zorp.Finger import *

Zorp.firewall_name = 'fw@site-net'

InetZone('site-net', '192.168.1.0/24',
         inbound_services=["*"],
         outbound_services=["*"])

InetZone('local', '127.0.0.0/8',
         inbound_services=["*"],
         outbound_services=["*"])

InetZone('internet', '0.0.0.0/0',
         inbound_services=["*"],
         outbound_services=["*"])

class MyFinger(FingerProxy):
    def config(self):
        self.max_username_length = 32
        self.response_header = "Finger header generated by Zorp\r\n" + '-'*80 + "\r\n"
        self.response_footer = "\r\n" + '-' * 80 + "\r\nThis request was supervised and logged by Zorp"

    def fingerRequest(self, dir):
        self.username = 'bazsi'
        return ZV_ACCEPT

def zorp():

    Service("finger", MyFinger,
            router=DirectedRouter(SockAddrInet('127.0.0.1', 79)))
    Listener(SockAddrInet("0.0.0.0", 7979), "finger")
