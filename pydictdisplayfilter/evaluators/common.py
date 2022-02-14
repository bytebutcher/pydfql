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
import ipaddress
import logging
from typing import Optional, Union, Callable, Any, List

import ipranger
import pyparsing
from dateutil.parser import parse as parse_date

from pydictdisplayfilter.exceptions import EvaluationError


class BasicEvaluator:
    """
    A basic evaluator which is ment to be used as base class for other evaluators and is quite useless on its own.
    """

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> Optional[Any]:
        """
        Converts a given value as defined in the expression to a more useful representation.
        :param value: a given value from the actual expression. Since we are kind of in control of the parsing process
                      we may expect an integer, string or None value here.
        :return: the transformed value.
        """
        return value  # Return untransformed value by default.

    def _convert_item_value(self, value: Optional[Any]) -> Optional[Any]:
        """
        Converts a given value from the datastore to a more useful representation.
        :param value: a given value from the datastore. Since we are not in control of the datastore the type of this
                      value is not known. Note that the value can also be None.
        :return: the transformed value.
        """
        return value  # Return untransformed by default.

    def _evaluate(self, expression_value: Any, item_value: Any) -> bool:
        """
        Evaluates the expression- and item-value.
        :param expression_value: a given transformed value from the expression.
        :param item_value: a given transformed value from the datastore.
        :return: True, when the item-value matches the expression.
        """
        return False  # Return False by default.

    def is_type(self, expression_value: Any, item_value: Any) -> bool:
        """
        Returns whether the evaluator is able to evaluate the expression- and item-value.
        :returns True, when expression- and item-value can be further processed, otherwise False.
        """
        try:
            self._convert_expression_value(expression_value)
            self._convert_item_value(item_value)
            return True
        except:
            return False

    def evaluate(self, expression_value: Optional[Union[int, str]], operator: str, item_value: Any) -> bool:
        """
        Evaluates the expression- and item-value.
        :param expression_value: a given untransformed value from the expression.
        :param item_value: a given untransformed value from the datastore.
        :return: True, when the item-value matches the expression.
        """
        try:
            evaluate = self._evaluate(
                self._convert_expression_value(expression_value),
                self._convert_item_value(item_value)
            )
            #print(self.__class__.__name__ + ": '{}' {} '{}' = {}".format(
            #    expression_value, operator, item_value, evaluate
            #))
            return evaluate
        except:
            #print(self.__class__.__name__ + ": '{}' {} '{}' = {}".format(
            #    expression_value, operator, item_value, False
            #))
            return False or operator == '!='


class CallbackEvaluator(BasicEvaluator):
    """ A basic evaluator which evaluates a callback with the given expression- and item-value. """

    def __init__(self, callback: Callable[[Any, Any], bool]):
        """
        Initializes the CallbackEvaluator with a callback.
        :param callback: a callback which expects two arguments and returns True or False.
        """
        self._callback = callback

    def _evaluate(self, expression_value: Any, item_value: Any) -> bool:
        """ Evaluates the expression- and item-value using the callback. """
        return self._callback(expression_value, item_value)


class FieldEvaluator(BasicEvaluator):
    """ A basic evaluator which tests that a given field exists in the datastore. """

    def _evaluate(self, expression_value: Any, item_value: Any) -> bool:
        """
        Tests whether the field exists in the given datastore. Note that there is no magic here and as long as the
        item value is not None, nor an empty string, list, or dictionary, this method will return True.
        """
        return item_value is not None and item_value != "" and item_value != [] and item_value != {}


class ListEvaluator(BasicEvaluator):
    """
    A basic evaluator which tests whether a given item can be found in the expression (e.g. "x in {'a', 'b', 'c'}").
    """

    def is_type(self, expression_value: Any, item_value: Any) -> bool:
        return isinstance(expression_value, List)

    def _evaluate(self, expression_value: List[Any], item_value: Any) -> bool:
        """
        Evaluates whether the given item value can be found in the given expression value list.
        :param expression_value: a list of items of any type.
        :param item_value: an item from a datastore of any type.
        :return: True, when item value is found in the given expression value list.
        """
        def _evaluate_list_item(ev, item_value):
            if isinstance(ev, List):
                if '..' in ev or '-' in ev:
                    l, _, r = ev
                    return float(l) <= float(item_value) <= float(r)
                else:
                    return any(_evaluate_list_item(v, item_value) for v in ev)
            else:
                try:
                    return float(item_value) == float(ev)
                except:
                    try:
                        return item_value == ev
                    except:
                        return False
        return any(_evaluate_list_item(ev, item_value) for ev in expression_value)


class StringEvaluator(CallbackEvaluator):
    """ Evaluates a callback where both arguments are strings. """

    def _convert_item_value(self, value: Any) -> str:
        return self._convert_expression_value(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> str:
        """
        Transform the expression value to a string.
        :param value: A given value from the expression. Since we are kind of in control of the parsing process
                      we may expect an integer, string or None value (but also other types as weill) here.
        :returns the transformed value.
        :raises Exception when value can not be converted.
        """
        # If value is None, return None instead of 'None'
        return str(value).encode('latin').decode('utf8') if value is not None else None


class DateEvaluator(CallbackEvaluator):

    def _convert_item_value(self, value: Any) -> str:
        """
        Transforms the item from the datastore to a date string.
        :param value: A given value from the expression. Since we are not in control of the datastore the type of the
                      value is not known.
        :returns the transformed value.
        :raises Exception when value can not be converted.
        """
        return parse_date(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> int:
        """
        Transform the expression value to a date string.
        :param value: A given value from the expression. Since we are kind of in control of the parsing process
                      we may expect an integer, string or None value here.
        :returns the transformed value.
        :raises Exception when value can not be converted.
        """
        if isinstance(value, str):
            if '.' in value:
                # The parse_date method accepts quite a lot of values which are then transformed to a dateformat.
                # For example, parse_date accepts -1, -1.0, 0, 0.0, 1.0, 1.
                # While we do not interfere with this parsing process for the item value we do not accept dots in the
                # expression value.
                return False
        return parse_date(value)


class NumberEvaluator(CallbackEvaluator):
    """ Evaluates a callback where both arguments are numbers. """

    def _convert_item_value(self, value: Any) -> float:
        """
        Transforms the item from the datastore to an integer.
        :param value: A given value from the expression. Since we are not in control of the datastore the type of the
                      value is not known. Note that octal, decimal or hexadecimal values are handled as well.
        :returns the transformed value.
        :raises Exception when value can not be converted.
        """
        return self._convert_expression_value(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]], ignore_strings: bool=False) -> float:
        """
        Transform the expression value to an integer. Handles octal, decimal and hexadecimal values as well.
        :param value: A given value from the expression. Since we are kind of in control of the parsing process
                      we may expect an integer, string or None value here.
        :returns the transformed value.
        :raises Exception when value can not be converted. Since we expect either an integer, string or None here
                it is rather unlikely that an exception is raised here.
        """
        if isinstance(value, bool):
            raise EvaluationError("Can not convert boolean value '{}' to float".format(value))
        if isinstance(value, List):
            return [self._convert_expression_value(v, ignore_strings=True) for v in value]
        if isinstance(value, str):
            if "." in value:
                # float
                return float(value)
            elif value.startswith("0x"):
                # hex
                return float(int(value, 16))
            elif value.startswith("0"):
                # octal
                return float(int(value, 8))
            elif value.isnumeric():
                # numeric
                return float(value)
            elif ignore_strings:
                return value
        return float(value)


class IntegerEvaluator(NumberEvaluator):
    """
    Evaluates integer expressions. This makes heavy use of the NumberEvaluator but transforms all results to integers.
    """

    def _convert_item_value(self, value: Any) -> int:
        """
        Transforms the item from the datastore to an integer.
        :param value: A given value from the expression. Since we are not in control of the datastore the type of the
                      value is not known. Note that octal, decimal or hexadecimal values are handled as well.
        :returns the transformed value.
        :raises Exception when value can not be converted.
        """
        return self._convert_expression_value(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> int:
        """
        Transform the expression value to an integer. Handles octal, decimal and hexadecimal values as well.
        :param value: A given value from the expression. Since we are kind of in control of the parsing process
                      we may expect an integer, string or None value here.
        :returns the transformed value.
        :raises Exception when value can not be converted. Since we expect either an integer, string or None here
                it is rather unlikely that an exception is raised here.
        """
        return not isinstance(value, bool) and int(super()._convert_expression_value(value))


class IPv4AddressEvaluator(CallbackEvaluator):
    """ Evaluates IPv4 addresses. """

    def _convert_item_value(self, value: Any) -> ipaddress.IPv4Address:
        return self._convert_expression_value(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> ipaddress.IPv4Address:
        """ Converts the expression value to an IPv4 address. """
        if isinstance(value, bool) or (isinstance(value, str) and '.' not in value) or isinstance(value, int):
            # Do not transform boolean values, strings without dots, or integers to IPv4 addresses.
            raise EvaluationError("Invalid value '{}'".format(value))
        return ipaddress.IPv4Address(value)


class IPv6AddressEvaluator(CallbackEvaluator):
    """ Evaluates IPv6 addresses. """

    def _convert_item_value(self, value: Any) -> ipaddress.IPv6Address:
        return self._convert_expression_value(value)

    def _convert_expression_value(self, value: Optional[Union[int, str]]) -> ipaddress.IPv6Address:
        """ Converts the expression value to an IPv6 address. """
        if isinstance(value, bool) or (isinstance(value, str) and ':' not in value) or isinstance(value, int):
            # Do not transform boolean values, strings without colons, or integers to IPv6 addresses.
            raise EvaluationError("Invalid value '{}'".format(value))
        return ipaddress.IPv6Address(value)


class IPv4RangeEvaluator(BasicEvaluator):
    """ Evaluates whether a given IPv4-address is within a list of IPv4-addresses. """

    def is_type(self, expression_value: Any, item_value: Any):
        """
        Checks whether the expression- and item-values are IPv4-addresses.
        :param expression_value: possibly a list of IPv4 Addresses.
        :param item_value: A given value from the expression. Since we are not in control of the datastore the type of the
                      value is not known.
        :return: True, when the expression- and item-values are IPv4-addresses.
        """
        try:
            return self._are_ipv4_addresses(expression_value) and self._is_ipv4_address(item_value)
        except:
            # If there is an error during type check it clearly indicates that this class is not meant to evaluate
            # the given expression- and item-value.
            return False

    def _are_ipv4_addresses(self, expression_value) -> bool:
        """ Checks whether the expression value evaluated as list of ipv4 addresses. """
        return all(isinstance(i, ipranger.ipranger.IPAddresses) for i in expression_value)

    def _is_ipv4_address(self, item_value) -> bool:
        """ Checks whether the item value is a valid ipv4 address. """
        try:
            pyparsing.common.ipv4_address.parseString(item_value, parse_all=True)
            return True
        except:
            return False

    def _evaluate(self, expression_value, item_value):
        """ Checks whether the item value is contained in the expression value. """
        # Split ipv4 address into parts.
        p1, p2, p3, p4 = map(int, item_value.split('.'))
        for part_1, part_2, part_3, part_4 in ipranger.IPAddressesResolver.resolve(expression_value):
            # Check whether each part of the item values ipv4 address can be found in the expression value.
            if p1 in part_1 and p2 in part_2 and p3 in part_3 and p4 in part_4:
                return True
        return False
