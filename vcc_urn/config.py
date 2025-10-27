import importlib as _importlib
import vcc_urn.core.config as _core_config
_importlib.reload(_core_config)
from vcc_urn.core.config import *  # re-export settings and types