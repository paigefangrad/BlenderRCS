import bpy

from bpy.props import (
  BoolProperty,
  FloatProperty,
  StringProperty,
  PointerProperty,
)

class RCSThrusterProperties(bpy.types.PropertyGroup):
  is_thruster: BoolProperty(
    name="Is RCS Thruster",
    description="Identifies this obect as an RCS thruster",
    default=False,
    options={'HIDDEN'},
  )

  enabled: BoolProperty(
    name="Enabled",
    description="Allows the solver to use this thruster" ,
    default=True
  )

  thrust_newtons: FloatProperty(
    name="Thrust",
    description="Maximum thrust produced in newtons",
    default=250.0,
    min=0.0,
    soft_max=100000.0,
    precision=2,
  )

  stable_id: StringProperty(
    name="Stable ID",
    description="Internal ID independent of object name",
    default="",
    options={'HIDDEN'}
  )


_CLASSES = (
  RCSThrusterProperties,
)


def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.Object.rcs_thruster = PointerProperty(
    type=RCSThrusterProperties
  )


def unregister():
  del bpy.types.Object.rcs_thruster  # type: ignore[attr-defined]

  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)