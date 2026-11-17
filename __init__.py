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
from . import add_menu
from . import ui

_MODULES = (
  properties,
  utils,
  add_menu,
  ui
)

def register():
  for module in _MODULES:
    module.register()


def unregister():
  for module in reversed(_MODULES):
    module.unregister()