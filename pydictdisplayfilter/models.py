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
from dataclasses import dataclass
from typing import Optional, Callable, Union, List


@dataclass
class Expression:
    """ Object representation of an expression (e.g. 'name == Neo', 'lower(name) == neo', ...) """
    field: str
    operator: Optional[str]
    value: Optional[Union[str, int]]
    function: Optional[Callable]
    slicer_specs: Optional[List]

    def __init__(self,
                 field: str,
                 operator: Optional[str] = None,
                 value: Optional[str] = None,
                 function: Optional[Callable] = None,
                 slicer_spec: Optional[str] = None):
        self.field = field
        self.operator = operator
        self.value = value
        self.function = function
        self.slicer_specs = slicer_spec if slicer_spec else None
