from fobi.base import form_callback_registry
from .callbacks import (
    AutoFormDbStore
)
form_callback_registry.register(AutoFormDbStore)
