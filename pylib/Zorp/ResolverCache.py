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

"""
<module maturity="stable">
  <summary>
    Module defining a cached DNS resolver.
  </summary>
  <description>
  <para>
    FIXME
  </para>
  </description>
</module>
"""

from Zorp import *
import dns.resolver
import dns.rdatatype
import dns.name
import time
import operator
import socket

class AbstractResolver(object):
    """<class internal="yes"/>"""
    def __init__(self, timeout):
        self.timeout = timeout

    def resolve(self, name):
        raise NotImplementedError


class DNSResolver(AbstractResolver):
    """<class internal="yes"/>"""
    def __init__(self, server=None, timeout=2):
        super(DNSResolver, self).__init__(timeout)

        self.resolver = dns.resolver.Resolver()
        self.resolver.lifetime = timeout
        if server:
            self.resolver.nameservers = [server]

    def resolve(self, host, resolved_cnames=None):
        if type(host) is str:
            host = dns.name.from_text(host)

        if resolved_cnames == None:
            resolved_cnames = set([host])

        ipv4_addresses = set()
        ipv6_addresses = set()
        ttl = None

        for record_type in (dns.rdatatype.A, dns.rdatatype.AAAA, dns.rdatatype.CNAME):
            try:
                log(None, CORE_DEBUG, 6, "Resolving host; host='%s', record_type='%s'" % (host, dns.rdatatype.to_text(record_type)))
                answer = self.resolver.query(host, record_type)
            except dns.resolver.NoAnswer:
                log(None, CORE_DEBUG, 6, "No records; host='%s', record_type='%s'" % (host, dns.rdatatype.to_text(record_type)))
            except (dns.resolver.Timeout, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN, dns.resolver.NoNameservers) as e:
                log(None, CORE_ERROR, 4, "Error while resolving host; host='%s', record_type='%s', error='%s'" % (host, dns.rdatatype.to_text(record_type), type(e)))
                raise KeyError
            else:
                ttl = min(ttl, answer.ttl) if ttl else answer.ttl
                if record_type == dns.rdatatype.A:
                    ipv4_addresses.update({record.address for record in answer})
                elif record_type == dns.rdatatype.AAAA:
                    ipv6_addresses.update({record.address for record in answer})
                elif record_type == dns.rdatatype.CNAME:
                    for record in answer:
                        if record.target in resolved_cnames:
                            log(None, CORE_DEBUG, 6, "CNAME already resolved, skipping; host='%s', cname='%s'" % (host, record.target))
                            continue
                        resolved_cnames.add(record.target)
                        log(None, CORE_DEBUG, 6, "Resolving CNAME for host; host='%s', cname='%s'" % (host, record.target))
                        cname_ttl, cname_ipv4_addresses, cname_ipv6_addresses = self.resolve(record.target, resolved_cnames)
                        ipv4_addresses.update(cname_ipv4_addresses)
                        ipv6_addresses.update(cname_ipv6_addresses)
                        ttl = min(ttl, cname_ttl)

        log(None, CORE_DEBUG, 6, "Host resolved; host='%s', ttl='%d', addresses='%s'" % (host, ttl, list(ipv4_addresses) + list(ipv6_addresses)))
        return ttl or AbstractHostnameCache.default_cache_timeout, list(ipv4_addresses), list(ipv6_addresses)


class AbstractHostnameCache(object):
    default_cache_timeout = 60

    def __init__(self, hosts=(), server=None):
        raise NotImplementedError

    def addHost(self, name):
        raise NotImplementedError

    def removeHost(self, name):
        raise NotImplementedError

    def updateHost(self, name):
        raise NotImplementedError

    def getNextExpiration(self):
        raise NotImplementedError

    def shouldUpdate(self):
        raise NotImplementedError

    def lookupAddress(self, address):
        """<method internal="yes"/>
        """
        raise NotImplementedError

    def lookupHostname(self, name):
        """<method internal="yes"/>
        """
        raise NotImplementedError

    def lookupTTL(self, name):
        """<method internal="yes"/>
        """
        raise NotImplementedError


class ResolverCache(AbstractHostnameCache):
    """
    <class maturity="stable">
      <summary>
        DNS cache
      </summary>
      <description>
        <para>
          ResolverCache retrieves the IP addresses of domain names. This can be used in domain name based
          policy decisions, for example to allow encrypted connections only to trusted e-banking sites.
        </para>
        <para>
          ResolverCache operates as follows: it resolves the IP addresses stored in the list of domain names using the specified Domain Name Server,
          and compares the results to the IP address of the connection (i.e., the IP address of the server or the client).
        </para>
        <example>
        <title>ResolverCache example</title>
        <para>
        The following ResolverCache class uses the <parameter>dns.example.com</parameter> name server to
        resolve the <parameter>example2.com</parameter> and <parameter>example3.com</parameter> domain names.
        </para>
        <synopsis>ResolverCache(server="dns.example.com", hosts=("example2.com", "example3.com"))</synopsis>
        </example>
      </description>
      <metainfo>
        <attributes/>
      </metainfo>
    </class>
    """

    def __init__(self, resolver):
        """
        <method maturity="stable">
          <summary>
            Constructor to initialize an instance of the ResolverCache class.
          </summary>
          <description>
            <para>
              This constructor initializes an instance of the ResolverCache class.
            </para>
          </description>
          <metainfo>
            <arguments>
              <argument maturity="stable">
                <name>hosts</name>
                <type>
                  <list>
                    <string/>
                  </list>
                </type>
                <description>Hostnames to resolve.</description>
              </argument>
              <argument maturity="stable">
                <name>server</name>
                <type>
                  <string/>
                </type>
                <default>None</default>
                <description>IP address of the DNS server to query. Defaults to the servers set in
                the <filename>resolv.conf</filename> file.</description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """
        self.resolver = resolver
        self.hosts = set()

        # address -> set of names
        self.cache_address_to_names = {}
        # name -> set of addresses
        self.cache_name_to_addresses = {}
        # hostname -> expiry timestamp
        self.expires = {}

    def __addHostToCache(self, host, ipv4_addresses, ipv6_addresses, ttl):
        """<method internal="yes">
        </method>
        """
        self.cache_name_to_addresses[host] = (set(ipv4_addresses), set(ipv6_addresses))

        for address in ipv4_addresses + ipv6_addresses:
            self.cache_address_to_names.setdefault(address, set()).add(host)

        now = time.time()
        self.expires[host] = now + ttl

    def __dropHostFromCache(self, host):
        """<method internal="yes">
        </method>
        """
        if host not in self.cache_name_to_addresses:
            return

        ipv4_addresses, ipv6_addresses = self.cache_name_to_addresses[host]
        for address in ipv4_addresses | ipv6_addresses:
            names = self.cache_address_to_names[address]
            names.remove(host)
            if len(names) == 0:
                del self.cache_address_to_names[address]

        del self.cache_name_to_addresses[host]

    def __updateHost(self, host):
        """<method internal="yes">
        </method>
        """
        self.__dropHostFromCache(host)

        try:
            ttl, ipv4_addresses, ipv6_addresses = self.resolver.resolve(host)
            self.__addHostToCache(host, ipv4_addresses, ipv6_addresses, ttl)
        except KeyError:
            self.__addHostToCache(host, [], [], AbstractHostnameCache.default_cache_timeout)
            log(None, CORE_INFO, 3, "Could not resolve host name trying again after default timeout; host='%s', timeout='%d'" % (host, AbstractHostnameCache.default_cache_timeout))

    def updateHost(self, host):
        """<method internal="yes">
        </method>
        """
        self.__updateHost(host)

    def update(self, now=None):
        """<method internal="yes">
        </method>
        """
        now = time.time()
        for host in self.hosts:
            expiration_time = self.expires.get(host, 0)
            if now < expiration_time:
                log(None, CORE_DEBUG, 6, "Host already in DNS cache and within TTL; host='%s', ttl='%f'" % (host, (expiration_time - now)))
            else:
                log(None, CORE_INFO, 5, "Host not in DNS cache or has expired, doing lookup; host='%s'" % host)
		try:
                    self.__updateHost(host)
                except ValueError:
                    raise KeyError

    def getNextExpiration(self):
        """<method internal="yes">
        </method>
        """
        return min(self.expires.items(), key=operator.itemgetter(1))

    def shouldUpdate(self):
        """<method internal="yes">
        </method>
        """
        try:
            now = time.time()
            expired_host, expiration_time = self.getNextExpiration()
            if now >= expiration_time:
                log(None, CORE_DEBUG, 6, "Found expired host in DNS cache; host='%s'" % expired_host)
                return True
        except ValueError:
            pass

        log(None, CORE_DEBUG, 6, "Not found expired host n DNS cache")
        return False

    def addHost(self, name):
        """<method internal="yes">
        </method>
        """
        self.hosts.add(name)
        self.__updateHost(name)

    def removeHost(self, name):
        """<method internal="yes">
        </method>
        """
        self.hosts.discard(name)
        self.__dropHostFromCache(name)

    def lookupAddress(self, address):
        """<method internal="yes"/>
        """
        self.update()

        return self.cache_address_to_names.get(address)

    def lookupHostname(self, name):
        """<method internal="yes"/>
        """
        self.update()

        return self.cache_name_to_addresses[name]

    def lookupTTL(self, name):

        """<method internal="yes"/>
        """
        return self.expires.get(name, None)
