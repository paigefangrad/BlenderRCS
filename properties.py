import bpy

from bpy.props import (
  BoolProperty,
  FloatProperty,
  StringProperty,
  PointerProperty,
)

class SpacecraftProperties(bpy.types.PropertyGroup):
  is_spacecraft: BoolProperty(
    name="Is Spacecraft",
    description="Identifies this object as a spacecraft",
    default=False,
    options={'HIDDEN'},
  )

  stable_id: StringProperty(
    name="Stable ID",
    description="Internal ID independent of object name",
    default="",
    options={'HIDDEN'}
  )

  mass_kg: FloatProperty(
    name="Mass kg",
    description="Mass of the craft in kg",
    default=100.0,
    min=0.1,
    soft_max=1000000.0,
    precision=2,
  )

  inertia_x: FloatProperty(
      name="Inertia X",
      description="Moment of inertia around the spacecraft's local X axis (kg·m²)",
      default=1000.0,
      min=0.001,
      precision=2,
  )

  inertia_y: FloatProperty(
      name="Inertia Y",
      description="Moment of inertia around the spacecraft's local Y axis (kg·m²)",
      default=1000.0,
      min=0.001,
      precision=2,
  )

  inertia_z: FloatProperty(
      name="Inertia Z",
      description="Moment of inertia around the spacecraft's local Z axis (kg·m²)",
      default=1000.0,
      min=0.001,
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


class COMProperties(bpy.types.PropertyGroup):
  is_com: BoolProperty(
    name="is_CoM",
    description="is Center of Mass",
    default=False,
    options={'HIDDEN'}
  )

  stable_id: StringProperty(
    name="Stable ID",
    description="Internal ID independent of object name",
    default="",
    options={'HIDDEN'}
  )


_CLASSES = (
  RCSThrusterProperties,
  SpacecraftProperties,
  COMProperties,
)


def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.Object.rcs_thruster = PointerProperty(
    type=RCSThrusterProperties
  )
  bpy.types.Object.spacecraft = PointerProperty(
    type=SpacecraftProperties
  )
  bpy.types.Object.com = PointerProperty(
    type=COMProperties
  )


def unregister():
  del bpy.types.Object.rcs_thruster  # type: ignore[attr-defined]
  del bpy.types.Object.spacecraft  # type: ignore[attr-defined]
  del bpy.types.Object.com  # type: ignore[attr-defined]

  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)