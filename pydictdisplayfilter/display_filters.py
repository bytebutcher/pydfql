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
import functools, re
from abc import ABC, abstractmethod
from sqlite3 import Connection
from typing import List, Dict, Callable, Union

from pydictdisplayfilter.evaluators import Evaluator, DefaultEvaluator
from pydictdisplayfilter.exceptions import EvaluationError
from pydictdisplayfilter.models import Expression
from pydictdisplayfilter.factories import SlicerFactory
from pydictdisplayfilter.parsers import DisplayFilterParser
from pydictdisplayfilter.slicers import BasicSlicer


class BaseDisplayFilter(ABC):
    """ Base class of a display filter. """

    def __init__(self,
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """
        Initializes the BaseDisplayFilter.
        :param field_names: A list of field names which are allowed in the display filter. If no field names are given
                            there are no restrictions regarding specifying field names.
        :param functions: A dictionary of functions whereby the key specifies the name. If no functions are supplied
                          "len", "lower" and "upper" are used as default ones.
        :param slicers: A list of slicers. If no slicers are supplied the BasicSlicer is used per default.
        :param evaluator: The evaluator used to evaluate the expressions. If no evaluator is specified the
                          DefaultEvaluator is used.
        """
        self._slicer_factory = SlicerFactory(slicers)
        self._evaluator = evaluator if evaluator else DefaultEvaluator()
        self._functions = functions if functions is not None else {
            "len": lambda value: len(value),
            "lower": lambda value: value.lower(),
            "upper": lambda value: value.upper()
        }
        self._field_names = field_names if field_names is not None else []
        self._display_filter_parser = DisplayFilterParser(field_names=self._field_names, functions=self._functions)

    def _get_item_value(self, expression, item) -> str:
        """
        Returns the value found at the specified key in the item. Key can be dot-notated for retrieving values
        inside nested dicts. Returns a transformed value if a function is specified.
        """
        keys = expression.field.split('.')
        value = functools.reduce(lambda d, key: d.get(key) if d else None, keys, item)
        sliced_value = self._slicer_factory.create(expression.slicer_specs, value).slice() if expression.slicer_specs else value
        return sliced_value if not expression.function else expression.function(sliced_value)

    def _evaluate_expressions(self, expressions, item) -> bool:
        """
        Evaluates a set of possibly nested expressions.
        :param expressions: List of expressions and logical operators.
        :param item: Item to test.
        :return: True, if expression matches item, otherwise False.
        """
        try:
            result = []
            for expression in expressions:
                if isinstance(expression, List):
                    # The expression is actually a list of expressions (e.g. '(x or y)').
                    # Evaluate list and convert boolean return value to a string.
                    result.append(str(self._evaluate_expressions(expression, item)))
                elif isinstance(expression, Expression):
                    # Evaluate the expression and convert boolean return value to a string (e.g. 'True' or 'False').
                    result.append(str(self._evaluator.evaluate(expression, self._get_item_value(expression, item))))
                elif isinstance(expression, str):
                    # The expression is actually an operator (e.g. 'and', 'or', etc.).
                    result.append(expression)
            # Join list of booleans and operators and evaluate this expression (e.g. 'True or False and True').
            return bool(eval(' '.join(result)))
        except Exception as err:
            raise EvaluationError(err)

    def _filter_data(self, data: List, expressions: List[Union[Expression, str]]) -> List:
        for item in data:
            if self._evaluate_expressions(expressions, item):
                yield item

    @property
    def field_names(self) -> List[str]:
        return self._field_names

    @field_names.setter
    def field_names(self, field_names: List[str] = None):
        self._field_names = field_names
        self._display_filter_parser = DisplayFilterParser(field_names=self._field_names, functions=self._functions)

    @property
    def functions(self) -> Dict[str, Callable]:
        return self._functions

    @functions.setter
    def functions(self, functions: Dict[str, Callable]):
        self._functions = functions
        self._display_filter_parser = DisplayFilterParser(field_names=self._field_names, functions=self._functions)

    @abstractmethod
    def filter(self, display_filter: str):
        raise NotImplementedError()


class DictDisplayFilter(BaseDisplayFilter):
    """ Allows to filter a dictionary using a display filter. """

    def __init__(self,
                 data: List[dict],
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """
        Initializes the DictDisplayFilter.
        :param data: A list of dictionaries to filter on.
        """
        super().__init__(field_names=field_names, functions=functions, slicers=slicers, evaluator=evaluator)
        self._data = data

    def filter(self, display_filter: str):
        """ Filters the data using the display filter. """
        expressions = self._display_filter_parser.parse(display_filter)
        yield from self._filter_data(self._data, expressions)


class ListDisplayFilter(DictDisplayFilter):
    """ Allows to filter a list of lists using a display filter. """

    def __init__(self,
                 data: List[List],
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """
        Initializes the ListDisplayFilter.
        :param data: A list of lists to filter on.
        """
        super().__init__(data=[
            dict(zip(field_names, item)) for item in data
        ], field_names=field_names, functions=functions, slicers=slicers, evaluator=evaluator)

    def filter(self, display_filter: str):
        """ Filters the data using the display filter. """
        for item in super().filter(display_filter):
            # Return each item as a list of values instead of a dictionary of key values.
            yield item.items()


class SQLDisplayFilter(BaseDisplayFilter):
    """
    Allows to filter a table of a SQL database using a display filter.

    This implementation is memory intensive since it queries all data from the database table and transforms it into a
    list of dictionaries before applying the actual display filter.
    """

    def __init__(self,
                 connection: Connection,
                 table_name: str = None,
                 column_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None
                 ):
        """
        Initializes the SQLDisplayFilter.
        :param connection:
        :param table_name: The name of the database table where the display filter will be applied.
        :param column_names: A list of column names which are allowed in the display filter. If no column names are
                             given there are no restrictions regarding specifying column names.
        """
        self._connection = connection
        self.table_name = table_name
        super().__init__(field_names=column_names, functions=functions, slicers=slicers, evaluator=evaluator)

    def _validate_table_name(self, table_name: str) -> bool:
        """ Checks whether the table name contains invalid characters or keywords"""
        pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
        if pattern.match(table_name) and not self._is_sql_keyword(table_name):
            return True
        else:
            return False

    def _is_sql_keyword(self, value: str) -> bool:
        """ Checks whether the given string is a reserved SQL keyword."""
        sql_keywords = [
            'select', 'from', 'where', 'join', 'order', 'group', 'having', 'union', 'intersect', 'except', 'limit',
            'offset'
        ]
        return value.lower() in sql_keywords

    def _get_column_names(self) -> List[str]:
        """ Retrieves the column names for the current table from the database. """
        cursor = self._connection.execute(f"SELECT * FROM {self._table_name} LIMIT(0)")
        return list(map(lambda x: x[0], cursor.description))

    def _get_table_data(self) -> List[dict]:
        """ Retrieves the table data from the database. """
        cursor = self._connection.execute(f"SELECT * FROM {self._table_name}")
        rows = cursor.fetchall()
        return [dict(zip(self.column_names, row)) for row in rows]

    @property
    def table_name(self) -> str:
        return self._table_name

    @table_name.setter
    def table_name(self, table_name: str):
        if table_name is not None and not self._validate_table_name(table_name):
            raise ValueError(f"'{table_name}' is not a valid table name.")
        self._table_name = table_name

    @property
    def column_names(self) -> List[str]:
        if not self.field_names:
            self.field_names = self._get_column_names()
        return self.field_names

    @column_names.setter
    def column_names(self, column_names: List[str]):
        self.field_names = column_names

    def filter(self, display_filter: str):
        """ Filters the data using the display filter. """
        expressions = self._display_filter_parser.parse(display_filter)
        table_data = self._get_table_data()
        yield from self._filter_data(table_data, expressions)
