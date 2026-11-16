import bpy

class RCS_ThrusterProperties(bpy.types.PropertyGroup):
  is_thruster: bool
  enabled: bool
  thrust_newtons: float
  bank: str
  stable_id: str

class Object(bpy.types.Object):
  rcs_thruster: RCS_ThrusterProperties