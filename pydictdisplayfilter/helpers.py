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
import cmd
import logging
import os
import time
import traceback
from collections import OrderedDict
from itertools import chain
from typing import List, Dict, Callable

from pydictdisplayfilter.display_filters import BaseDisplayFilter, DictDisplayFilter
from pydictdisplayfilter.evaluators import Evaluator
from pydictdisplayfilter.exceptions import ParserError, EvaluationError
from pydictdisplayfilter.slicers import BasicSlicer


class TableError(Exception):
    pass


class TableColumnSizeCalculator:

    @staticmethod
    def calculate(data_store: List[dict], fields: List) -> List[int]:
        """ Calculates and returns the necessary size of each column in the data store. """
        field_sizes = OrderedDict()
        for field in fields:
            field_sizes[field] = len(field)
        for item in data_store:
            for key in field_sizes.keys():
                if key in item:
                    field_sizes[key] = max(len(str(item[key])), field_sizes[key])
        return list(field_sizes.values())


class Table:
    """ Data store with filter capabilities and pretty table printout. """

    def __init__(self, display_filter: BaseDisplayFilter):
        self._display_filter = display_filter

    def _make_table(self, data_store: List[dict]) -> List[str]:
        """ Creates a table including header from the data store. """
        if not data_store:
            return []
        fields = self.fields()
        table = [fields]
        column_size = self._calculate_column_size(data_store, fields)
        format_str = ' | '.join(["{{:<{}}}".format(i) for i in column_size])
        for item in data_store:
            table.append([str(item[field]) if field in item else '' for field in fields])
        table.insert(1, ['-' * i for i in column_size]) # Separating line
        return [""] + [ format_str.format(*item) for item in table ]

    def _calculate_column_size(self, data_store: List[dict], fields: List) -> List[int]:
        """ Calculates and returns the necessary size of each column in the data store. """
        return TableColumnSizeCalculator.calculate(data_store, fields)

    def _make_footer(self, items: List[dict], duration: float) -> List[str]:
        """ Creates a footer for the table which prints some statistics. """
        item_count = len(items)
        result = [""]
        if item_count == 0:
            result.append("Empty set ({:.2f} secs)".format(duration))
        else:
            type_name = "row" if item_count == 1 else "rows"
            result.append("{} {} in set ({:.2f} secs)".format(item_count, type_name, duration))
        result.append("")
        return result

    def fields(self) -> List[str]:
        """ Returns the field names used in the data store. """
        return self._display_filter.field_names

    def filter(self, display_filter: str) -> str:
        """
        Filters the items in the data store using the specified display filter and returns the result in a table.
        """
        start = time.time()
        result = list(self._display_filter.filter(display_filter))
        end = time.time()
        duration = end - start
        return os.linesep.join(self._make_table(result) + self._make_footer(result, duration))


class DisplayFilterShell(cmd.Cmd):
    """ A little shell for the display filter. """

    intro = 'Type help or ? to list commands.\n'
    prompt = '> '

    def __init__(self, table: Table):
        """ Initializes the DisplayFilterShell with a data store. """
        super().__init__()
        self._logger = self._init_logger()
        self._table = table

    def _init_logger(self) -> logging.Logger:
        """ Setups the logger. Makes sure that info messages are actually printed. """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger

    def do_debug(self, *args):
        """ Toggles debug mode on/off. """
        if self._logger.level == logging.DEBUG:
            self._logger.level = logging.INFO
            self._logger.warning("Debug mode disabled")
        else:
            self._logger.level = logging.DEBUG
            self._logger.warning("Debug mode enabled")

    def do_fields(self, *args):
        """ Returns the fields the display filter can be applied on. """
        try:
            for key in self._table.fields():
                print(key)
        except Exception as err:
            self._logger.error('There was an error retrieving the fields!')
            self._logger.debug(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()

    def do_filter(self, *args):
        """ Applies the given display filter to the data and prints the result. """
        try:
            display_filter = ' '.join(args)
            if not display_filter:
                self._logger.error("No arguments supplied to filter function.")
                return
            print(self._table.filter(display_filter))
        except ParserError as err:
            self._logger.error('Invalid display filter!')
            self._logger.debug(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()
        except EvaluationError as err:
            self._logger.error('There was an unknown error evaluating the results!')
            self._logger.debug(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()
        except TableError as err:
            self._logger.error(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()
        except Exception as err:
            self._logger.error('There was an unknown error displaying the results!')
            self._logger.debug(err)
            if self._logger.level == logging.DEBUG:
                traceback.print_exc()

    def do_import(self, *args):
        """ Imports data from a given file. """
        self._logger.error("This function is currently not implemented!")
        return False

    def do_export(self, *args):
        """ Exports the data to a given file. Optional display filter for only exporting specific data. """
        self._logger.error("This function is currently not implemented!")
        return False

    def get_names(self):
        """ Override get_names() method of cmd.Cmd to remove functions from the help we do not want to show. """
        names = super().get_names()
        names.remove('do_EOF')
        return names

    def do_EOF(self, line):
        """ Exit application when pressing CTRL+D. """
        return True

    def do_exit(self, *args):
        """ Exit application. """
        return True


class DictTable(Table):
    """ Data store with filter capabilities and pretty table printout. """

    def __init__(self,
                 data_store: List[dict],
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """ Initializes the DictTable with a data store. """
        field_names = field_names or self._extract_field_names(data_store)
        super().__init__(DictDisplayFilter(data_store, field_names, functions, slicers, evaluator))

    def _extract_field_names(self, data_store: List[dict]) -> List[str]:
        """ Extracts the field names from the given data store. """
        return sorted(set(chain.from_iterable(row.keys() for row in data_store)))


class DictDisplayFilterShell(DisplayFilterShell):
    """ A little shell for querying a list of dictionaries using the display filter. """

    def __init__(self,
                 data_store: List[dict],
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """ Initializes the DictDisplayFilterShell with a data store. """
        super().__init__(DictTable(data_store, field_names, functions, slicers, evaluator))