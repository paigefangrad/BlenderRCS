bl_info = {
  "name": "RCS Generator",
  "author": "RCS Generator",
  "version": (0, 1, 0),
  "blender": (5, 3, 0),
  "location": "View3D > Add > RCS Thruster",
  "description": "Create and manage spacecraft RCS thrusters",
  "category": "Object",
}

from . import properties
from . import utils
from . import thrusters
from . import add_menu
from . import ui
from . import allocation

_MODULES = (
  properties,
  utils,
  thrusters,
  add_menu,
  ui,
  allocation,
)

def register():
  for module in _MODULES:
    module.register()


def unregister():
  for module in reversed(_MODULES):
    module.unregister()