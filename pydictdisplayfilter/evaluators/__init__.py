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
import re
from typing import List, Dict
from pydictdisplayfilter.evaluators.common import FieldEvaluator, IPv4RangeEvaluator, ListEvaluator, NumberEvaluator, \
    IntegerEvaluator, StringEvaluator, DateEvaluator, IPv4AddressEvaluator, IPv6AddressEvaluator, BasicEvaluator


class Evaluator:
    """ Evaluates an expression and item value. """

    # Dictionary of evaluators. Key is the operator. There can be more than one evaluator for a given operator.
    evaluators = {
        # eq
        '==': [],
        # neq
        '!=': [],
        # matches
        '~': [],
        # contains
        '~=': [],
        # ge
        '>=': [],
        # gt
        '>': [],
        # le
        '<=': [],
        # lt
        '<': [],
        # (no alternative symbol)
        '&': [],
        # (no alternative symbol)
        'in': []
    }

    def __init__(self, evaluators: Dict[str, List[BasicEvaluator]]):
        """
        Initializes the Evaluator.
        :param evaluators: A dictionary of evaluators whereby each key stands for a operator.
        """
        self.evaluators = evaluators

    def _get_evaluators(self, expression, item_value):
        """ Returns the matching evaluators for a given expression and item value. """
        # Since there can be more than one evaluator for a given operator they are tried in order.
        for evaluator in self.evaluators.get(expression.operator):
            if evaluator.is_type(expression.value, item_value):
                yield evaluator

    #test = {'value': ['1', '2', '3']}
    # value == 1 -- any(i = v for i in val)     == True
    # value != 1 -- not any                     == False

    # value != 1
    # value == 1
    # not (operator == '!=' and any(value))      value == 1     ==>  false       true
    # not (operator == '!=' and any(value))      value != 1     ==>  true
    #
    # 1         0       1
    # 0        1        0

    def _evaluate(self, evaluator, expression, item_value) -> bool:
        """ Returns True, if the value matches the expression using the given evaluator. """
        if isinstance(item_value, List) and item_value != []:
            # Check whether any item value in the list matches the expression.
            if expression.operator != '!=':
                # The list of items_matching_expression contains True for any item value corresponding to the
                # expression. We return True, if any item value with matching expression was found, otherwise
                # False.
                return any(
                    evaluator.evaluate(expression.value, expression.operator, item_value) for item_value in item_value
                )
            else:
                # In case of the '!='-operator we are testing whether the value was NOT found in the list.
                # The list of items matching the expression contains True for any item value not corresponding to the
                # expression. We return True, if all item values did not match the expression, otherwise False.
                return all(
                    evaluator.evaluate(expression.value, expression.operator, item_value) for item_value in item_value
                )
        else:
            # Returns True, if the value matches the expression using the given evaluator, otherwise False.
            return evaluator.evaluate(expression.value, expression.operator, item_value)

    def evaluate(self, expression, item_value) -> bool:
        """ Returns whether the value matches the expression. """
        if not expression.operator:
            # When no operator is given only the existence of the field/key in the given item is tested.
            return FieldEvaluator().evaluate(expression, expression.operator, item_value)
        # Returns True, when any fitting evaluator evaluates to True, otherwise False.
        for evaluator in self._get_evaluators(expression, item_value):
            result = self._evaluate(evaluator, expression, item_value)
            if result or expression.operator == '!=':
                # Returns either the first False result for the '!=' operator or the first True result for any other
                # operator.
                return result
        return False


class DefaultEvaluator(Evaluator):
    """ The default implementation of an evaluator supporting all kind of types. """

    def __init__(self):
        super().__init__({
            # eq
            '==': [
                NumberEvaluator(lambda expression_value, item_value: expression_value == item_value),
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value == expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value == expression_value),
                StringEvaluator(lambda expression_value, item_value: expression_value == item_value)
            ],
            # neq
            '!=': [
                NumberEvaluator(lambda expression_value, item_value: expression_value != item_value),
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value != expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value != expression_value),
                StringEvaluator(lambda expression_value, item_value: expression_value != item_value)
            ],
            # matches
            '~': [StringEvaluator(lambda expression_value, item_value: bool(re.search(expression_value, item_value)))],
            # contains
            '~=': [StringEvaluator(lambda expression_value, item_value: expression_value in item_value)],
            # ge
            '>=': [
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value >= expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value >= expression_value),
                DateEvaluator(lambda expression_value, item_value: item_value >= expression_value),
                NumberEvaluator(lambda expression_value, item_value: item_value >= expression_value)
            ],
            # gt
            '>': [
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value > expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value > expression_value),
                DateEvaluator(lambda expression_value, item_value: item_value > expression_value),
                NumberEvaluator(lambda expression_value, item_value: item_value > expression_value)
            ],
            # le
            '<=': [
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value <= expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value <= expression_value),
                DateEvaluator(lambda expression_value, item_value: item_value <= expression_value),
                NumberEvaluator(lambda expression_value, item_value: item_value <= expression_value)
            ],
            # lt
            '<': [
                IPv4AddressEvaluator(lambda expression_value, item_value: item_value < expression_value),
                IPv6AddressEvaluator(lambda expression_value, item_value: item_value < expression_value),
                DateEvaluator(lambda expression_value, item_value: item_value < expression_value),
                NumberEvaluator(lambda expression_value, item_value: item_value < expression_value)
            ],
            # (no alternative symbol)
            '&': [IntegerEvaluator(lambda expression_value, item_value: (item_value & expression_value) > 0)],
            # (no alternative symbol)
            'in': [IPv4RangeEvaluator(), ListEvaluator()]
        })
