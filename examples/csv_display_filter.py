# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of pydfql.
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
import csv
import logging
import os.path
import sys
import traceback

from pydfql.helpers import DictDisplayFilterShell


def read_csv_file(csv_file):
    try:
        with open(csv_file, mode='r') as infile:
            reader = list(csv.reader(infile))
            field_names = reader.pop(0)
            return [dict(zip(field_names, item)) for item in reader]
    except Exception as err:
        logger.debug(err)
        raise Exception("{}: Error reading file".format(csv_file))


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='Display filter for csv file.')
    parser.add_argument('csv_file', action='store', metavar='FILE', help='CSV-file to load')

    # Parse all arguments
    arguments = parser.parse_args()

    csv_file = arguments.csv_file
    if not os.path.isfile(csv_file):
        logger.error("{}: No such file".format(csv_file))
        sys.exit(1)

    try:
        data_store = read_csv_file(csv_file)
        if not data_store or len(data_store) == 0:
            field_names = list()
        else:
            # Extract field names from header.
            field_names = list(data_store[0].keys())
        DictDisplayFilterShell(data_store, field_names=field_names).cmdloop()
    except Exception as err:
        logger.error(str(err))
        traceback.print_exc()
        sys.exit(1)
