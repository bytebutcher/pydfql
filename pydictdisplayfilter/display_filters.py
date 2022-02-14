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
import functools
from typing import List, Dict, Callable

from pydictdisplayfilter.evaluators import Evaluator, DefaultEvaluator
from pydictdisplayfilter.exceptions import EvaluationError
from pydictdisplayfilter.models import Expression
from pydictdisplayfilter.factories import SlicerFactory
from pydictdisplayfilter.parsers import DisplayFilterParser
from pydictdisplayfilter.slicers import BasicSlicer


class BaseDisplayFilter:
    """ Base class of a display filter. """

    def __init__(self,
                 data: List[dict],
                 field_names: List[str] = None,
                 functions: Dict[str, Callable] = None,
                 slicers: List[BasicSlicer] = None,
                 evaluator: Evaluator = None):
        """
        Initializes the BaseDisplayFilter.
        :param data: A list of dictionaries to filter on.
        :param field_names: A list of field names which are allowed in the display filter. If no field names are given
                            there are no restrictions regarding specifying field names.
        :param functions: A dictionary of functions whereby the key specifies the name. If no functions are supplied
                          "len", "lower" and "upper" are used as default ones.
        :param slicers: A list of slicers. If no slicers are supplied the BasicSlicer is used per default.
        :param evaluator: The evaluator used to evaluate the expressions. If no evaluator is specified the
                          DefaultEvaluator is used.
        """
        self._data = data
        functions = functions if functions else {
            "len": lambda value: len(value),
            "lower": lambda value: value.lower(),
            "upper": lambda value: value.upper()
        }
        self._slicer_factory = SlicerFactory(slicers)
        self._evaluator = evaluator if evaluator else DefaultEvaluator()
        self._display_filter_parser = DisplayFilterParser(field_names, functions)

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

    def filter(self, display_filter):
        raise NotImplementedError("This method should be implemented by the derived class!")


class DictDisplayFilter(BaseDisplayFilter):
    """ Allows to filter a dictionary based on a display filter. """

    def filter(self, display_filter):
        """ Filters the data based on a display filter. """
        expressions = self._display_filter_parser.parse(display_filter)
        for item in self._data:
            if self._evaluate_expressions(expressions, item):
                yield item


class ListDisplayFilter(DictDisplayFilter):
    """ Allows to filter a list of lists based on a display filter. """

    def __init__(self, data: List[List], field_names: List[str]):
        super().__init__([
            dict(zip(field_names, item)) for item in data
        ], field_names)

    def filter(self, display_filter):
        """ Filters the data based on a display filter. """
        for item in super().filter(display_filter):
            # Return each item as a list of values instead of a dictionary of key values.
            yield item.items()
