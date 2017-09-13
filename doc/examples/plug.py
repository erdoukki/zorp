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
# Demonstrates the usage of the built-in plug proxy. It listens on
# 127.0.0.1:1999 and connects to 127.0.0.1:25

from Zorp.Core import *
from Zorp.Plug import PlugProxy

InetZone('site-net', '192.168.1.0/24',
         inbound_services=["*"],
         outbound_services=["*"])

InetZone('local', '127.0.0.0/8',
         inbound_services=["*"],
         outbound_services=["*"])

InetZone('internet', '0.0.0.0/0',
         inbound_services=["*"],
         outbound_services=["*"])

def zorp():

    Service("plug", PlugProxy,
            router=DirectedRouter(SockAddrInet('127.0.0.1', 25)))
    Listener(SockAddrInet("0.0.0.0", 1999), "plug")
