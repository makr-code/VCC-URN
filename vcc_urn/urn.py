import importlib as _importlib
import vcc_urn.services.urn as _urn_impl
_importlib.reload(_urn_impl)
from vcc_urn.services.urn import *  # re-export URN and URNComponents