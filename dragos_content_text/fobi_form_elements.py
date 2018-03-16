from __future__ import absolute_import

from fobi.base import form_element_plugin_registry

from .base import DragosContentTextPlugin

__title__ = 'dragos_content_text'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DragosContentTextPlugin',)


form_element_plugin_registry.register(DragosContentTextPlugin)
