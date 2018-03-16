from __future__ import absolute_import

from fobi.base import form_element_plugin_registry

from .base import DragosRangeSelectInputPlugin

__title__ = 'dragos_range_select'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DragosRangeSelectInputPlugin',)


form_element_plugin_registry.register(DragosRangeSelectInputPlugin)
