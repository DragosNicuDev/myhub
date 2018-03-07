from fobi.base import form_callback_registry
from fobi.contrib.plugins.form_handlers.db_store.callbacks import (
    AutoFormDbStore
)
form_callback_registry.register(AutoFormDbStore)
