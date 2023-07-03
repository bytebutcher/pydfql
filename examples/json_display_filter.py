# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of python-dict-display-filter.
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
import json
import logging
import os.path
import sys
import traceback
from typing import List, Set

from pydictdisplayfilter import DictDisplayFilter
from pydictdisplayfilter.helpers import Table, DisplayFilterShell


def read_json_file(json_file):
    try:
        with open(json_file, mode='r') as infile:
            return json.load(infile)
    except Exception as err:
        logger.debug(err)
        raise Exception("{}: Error reading file".format(json_file))


class JSONTable(Table):
    """ Data store with filter capabilities and pretty table printout. """

    def __init__(self, data_store: List[dict]):
        """ Initializes the DictTable with a data store. """
        self._data_store = data_store
        super().__init__(DictDisplayFilter(data_store))

    def _make_table(self, data_store: List[dict]) -> List[str]:
        """ Creates a view for nested data items. """
        return [json.dumps(data) for data in data_store]

    def _extract_keys(self, data_store: List[dict]) -> List[str]:
        """ Extracts the keys from a nested data store. """
        def extract_keys(data: dict, parent_key: str='') -> Set[str]:
            keys = set()
            if isinstance(data, dict):
                for k, v in data.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    keys |= extract_keys(v, new_key)
            else:
                keys.add(parent_key)
            return keys

        all_keys = set()
        for data in data_store:
            all_keys |= extract_keys(data)
        return list(all_keys)

    def fields(self, thorough: bool = True) -> List[str]:
        """ Returns the field names used in the data store. """
        if not self._data_store:
            # No items in data store, so there are no fields to query either.
            return list()
        return self._extract_keys(self._data_store)


class JSONDisplayFilterShell(DisplayFilterShell):
    """ A little shell for querying a list of dictionaries using the display filter. """

    def __init__(self, data_store: List[dict]):
        """ Initializes the DictDisplayFilterShell with a data store. """
        super().__init__(JSONTable(data_store))


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='Display filter for json file.')
    parser.add_argument('json_file', action='store', metavar='FILE', help='JSON-file to load')

    # Parse all arguments
    arguments = parser.parse_args()

    json_file = arguments.json_file
    if not os.path.isfile(json_file):
        logger.error("{}: No such file".format(json_file))
        sys.exit(1)

    try:
        data_store = read_json_file(json_file)
        JSONDisplayFilterShell(data_store).cmdloop()
    except Exception as err:
        logger.error(str(err))
        traceback.print_exc()
        sys.exit(1)
