import bpy

from typing import Literal
from . import thrusters

from bpy.types import Context

class VIEW3D_PT_rcs_panel(bpy.types.Panel):
  bl_label = "RCS Settings"
  bl_idname = "VIEW3D_PT_rcs_settings"

  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "RCS"

  @classmethod
  def poll(cls, context: Context) -> bool:
    obj = context.object

    return (
      obj is not None and (
        (hasattr(obj, "rcs_thruster") and obj.rcs_thruster.is_thruster)
        or
        (hasattr(obj, "spacecraft") and obj.spacecraft.is_spacecraft)
      )
    )


  def draw(self, context: Context) -> None:
    obj = context.object
    if obj.rcs_thruster.is_thruster is True:
      self.draw_rcs_ui(context)
    elif obj.spacecraft.is_spacecraft is True:
      self.draw_spacecraft_ui(context)


  def draw_rcs_ui(self, context: Context) -> None: 
    layout: bpy.types.UILayout | None
    layout = self.layout
    obj = context.object
    props = obj.rcs_thruster

    if layout is None or obj is None: 
      print("shit is missing")
      return

    layout.label(
      text=obj.name,
      icon='CON_CAMERASOLVER'
    )

    layout.prop(props, "enabled")
    layout.prop(props, "thrust_newtons")

    layout.separator()

    layout.label(text=obj.rcs_thruster.stable_id)

    layout.separator()

    if obj.parent:
      layout.label(
        text=f"Spacecraft: {obj.parent.name}",
        icon='OBJECT_DATA'
      )
      layout.operator(
        text="select spaceship",
        operator='rcs.select_parent',
        icon='ACTION'
      )
    else:
      layout.label(
        text="No spacecraft parent",
        icon='ERROR'
      )

  def draw_spacecraft_ui(self, context: Context) -> None:
    layout: bpy.types.UILayout | None
    layout = self.layout
    obj = context.object
    props = obj.spacecraft

    if layout is None or obj is None: 
      return

    layout.label(
      text=obj.name,
      icon='RESTRICT_SELECT_OFF'
    )

    layout.prop(props, "mass_kg")
    inertia_header, inertia_panel = layout.panel("inertia_moments", default_closed=True)
    inertia_header.label(text="inertia moments")

    if inertia_panel is not None:
      inertia_panel.prop(props, "inertia_x")
      inertia_panel.prop(props, "inertia_y")
      inertia_panel.prop(props, "inertia_z")

    layout.separator()

    layout.operator(
      thrusters.RCS_OT_check_ship.bl_idname,
      text="check ship"
    )


_CLASSES = (
  VIEW3D_PT_rcs_panel,
)

def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)


def unregister():
  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
