# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of ipranger.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import logging
import os.path
import sys
import traceback
from collections import defaultdict
from typing import List, Dict

from pydictdisplayfilter.helpers import DisplayFilterShell

try:
    from libnmap.objects import NmapHost
    from libnmap.parser import NmapParser
except:
    sys.stderr.write("Missing python3 package python-libnmap! ")
    sys.stderr.write("Please install python-libnmap using 'pip3 install python-libnmap==0.7.0" + os.linesep)
    sys.exit(1)


class NmapXMLParser:

    def _parse_host(self, host) -> List[List[dict]]:
        """ Parses the host and returns a list of lists of dictionaries. """
        data = []
        status_ports_map = self._parse_host_ports(host)
        for status, ports in status_ports_map.items():
            for port_spec in ports:
                port = str(port_spec[0])
                protocol = port_spec[1]
                if port and protocol:
                    service = host.get_service(int(port), protocol=protocol)
                    service_name = service.banner or service.service or ""
                    data.append([{
                        "host": host.address,
                        "port": port,
                        "protocol": protocol,
                        "status": status,
                        "service": service_name
                    }])

        return data

    def _parse_host_ports(self, host):
        """ Parses the host ports. """
        status_ports_map = defaultdict(list)
        for p in host.services:
            status_ports_map[p.state].append((p.port, p.protocol))
        return status_ports_map

    def parse(self, nmap_xml_file) -> List[dict]:
        """ Parses the nmap xml file and returns a list of dictionaries containing the data. """
        data = []
        nmap_data = NmapParser.parse_fromfile(nmap_xml_file)
        for host in nmap_data.hosts:
            for item in self._parse_host(host):
                data += item
        return data


if __name__ == '__main__':
    logger = logging.getLogger()
    parser = argparse.ArgumentParser(description='Display filter for nmap xml file.')
    parser.add_argument('nmap_xml_file', action='store', metavar='FILE', help='nmap xml-file to load')

    # Parse all arguments
    arguments = parser.parse_args()

    nmap_xml_file = arguments.nmap_xml_file
    if not os.path.isfile(nmap_xml_file):
        logger.error("{}: No such file".format(nmap_xml_file))
        sys.exit(1)

    try:
        data_store = NmapXMLParser().parse(nmap_xml_file)
        DisplayFilterShell(data_store).cmdloop()
    except Exception as err:
        logger.error(str(err))
        traceback.print_exc()
        sys.exit(1)
