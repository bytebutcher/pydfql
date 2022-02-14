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
from typing import List

from pydictdisplayfilter.slicers import MacSlicer, BasicSlicer, IPv4Slicer, IPv6Slicer


class SlicerFactory:
    """
    Creates a slicer object used for extended slicing.
    """

    def __init__(self, slicers: List[BasicSlicer] = None):
        self._classes = slicers if slicers else [MacSlicer, IPv4Slicer, IPv6Slicer]

    def create(self, slicer_spec, value: str) -> BasicSlicer:
        """ Returns the sliced value. """
        for cls in self._classes:
            if cls.is_type(value):
                return cls(slicer_spec, value)
        return BasicSlicer(slicer_spec, value)
