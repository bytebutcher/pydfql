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
import logging
import os.path
import sqlite3
import sys
import traceback
from typing import List, Dict, Callable

from pydictdisplayfilter.display_filters import SQLDisplayFilter
from pydictdisplayfilter.evaluators import Evaluator
from pydictdisplayfilter.helpers import DisplayFilterShell, Table, TableError
from pydictdisplayfilter.slicers import BasicSlicer


class TableNotFoundError(TableError):

    def __init__(self):
        super().__init__('Table not found!')


class NoTableSelectedError(TableError):

    def __init__(self):
        super().__init__('No table selected!')


class SQLiteTable(Table):
    """ Data store with filter capabilities and pretty table printout. """

    def __init__(self,
                 database_file: str,
                 table_name: str = None,
                 column_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        self._database_file = database_file
        self._connection = sqlite3.connect(database_file)
        super().__init__(
            SQLDisplayFilter(
                connection=self._connection,
                table_name=table_name,
                column_names=column_names,
                functions=functions,
                slicers=slicers,
                evaluator=evaluator))

    def _table_exists(self, table_name: str) -> bool:
        """ Checks whether the specified table does exist. """
        cursor = self._connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    def use(self, table_name):
        """ Selects a table to work on. """
        if not self._table_exists(table_name):
            raise TableNotFoundError()
        self._display_filter.table_name = table_name

    def table(self) -> str:
        """ Returns the currently selected table. """
        if not self._display_filter.table_name:
            raise NoTableSelectedError()
        return self._display_filter.table_name

    def tables(self) -> List[str]:
        """ Lists all tables of the database. """
        cursor = self._connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        cursor.row_factory = lambda cursor, row: row[0]
        result = cursor.fetchall()
        cursor.close()
        return result

    def fields(self) -> List[str]:
        """ Returns the column names of the selected table. """
        if not self._display_filter.table_name:
            raise NoTableSelectedError()

        cursor = self._connection.cursor()
        cursor.row_factory = lambda cursor, row: row[1]
        cursor.execute(f'PRAGMA table_info({self._display_filter.table_name})')
        column_names = cursor.fetchall()
        cursor.close()
        return column_names

    def filter(self, display_filter: str) -> str:
        """
        Filters the rows in the table using the specified display filter and returns the result in a pretty
        table format.
        """
        if not self._display_filter.table_name:
            raise NoTableSelectedError()

        return super().filter(display_filter)


class SQLiteDisplayFilterShell(DisplayFilterShell):
    """ A little shell for querying a SQLite database using the display filter. """

    def __init__(self,
                 database_file: str,
                 table_name: str = None,
                 column_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """ Initializes the SQLiteDisplayFilterShell with a database file. """
        super().__init__(
            SQLiteTable(
                database_file=database_file,
                table_name=table_name,
                column_names=column_names,
                functions=functions,
                slicers=slicers,
                evaluator=evaluator))

    def do_tables(self, *args):
        """ Returns all tables which can be selected. """
        try:
            for table_name in self._table.tables():
                print(table_name)
        except Exception as err:
            self._logger.error(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()

    def do_table(self, *args):
        """ Shows the currently selected table. """
        try:
            print(self._table.table())
        except Exception as err:
            self._logger.error(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()

    def do_use(self, table_name: str):
        """ Selects the database table the display filter should be applied on. """
        try:
            if not table_name:
                self._logger.error('Usage: use <table_name>')
                return
            self._table.use(table_name)
            self._logger.info('Table changed')
        except Exception as err:
            self._logger.error(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()

    def do_fields(self, *args):
        """ Returns the fields the display filter can be applied on. """
        try:
            for key in self._table.fields():
                print(key)
        except Exception as err:
            self._logger.error(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='Display filter for sqlite database.')
    parser.add_argument('sqlite_db', action='store', metavar='FILE', help='SQLite-database to load')

    # Parse all arguments
    arguments = parser.parse_args()

    sqlite_db = arguments.sqlite_db
    if not os.path.isfile(sqlite_db):
        logger.error("{}: No such file".format(sqlite_db))
        sys.exit(1)

    try:
        SQLiteDisplayFilterShell(sqlite_db).cmdloop()
    except Exception as err:
        logger.error(err)
        traceback.print_exc()
        sys.exit(1)
