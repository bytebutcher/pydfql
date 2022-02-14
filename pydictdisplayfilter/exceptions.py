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


class ParserError(Exception):
    """
    This error indicates that there was an error during parsing the display filter which usually happens when the
    user input (aka the display filter) is not correctly specified.
    """
    pass


class EvaluationError(Exception):
    """
    This error indicates that there was an error during evaluating an expression which usually happens when some
    illegal operations are performed (e.g. 'lower(int)' -> only works with strings).
    """
    pass


class ProgrammingError(Exception):
    """
    This error indicates an internal error likely due to some programming error.
    If this error is thrown please open a ticket.
    """
    pass
