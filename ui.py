import bpy
from bpy.types import Context

class VIEW3D_PT_rcs_thruster(bpy.types.Panel):
  bl_label = "RCS Thruster"
  bl_idname = "VIEW3D_PT_rcs_thruster"

  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "RCS"

  @classmethod
  def poll(cls, context: Context) -> bool:
    obj = context.object

    return (
      obj is not None
      and obj.rcs_thruster.is_thruster
    )


  def draw(self, context: Context) -> None:
    layout: bpy.types.UILayout | None
    layout = self.layout
    obj = context.object
    props = obj.rcs_thruster

    if layout is None or obj is None: 
      print("shit is missing")
      return

    layout.label(
      text=obj.name,
      icon='EMPTY_AXIS'
    )

    layout.prop(props, "enabled")
    layout.prop(props, "thrust_newtons")

    layout.separator()

    if obj.parent:
      layout.label(
        text=f"Spacecraft: {obj.parent.name}",
        icon='OBJECT_DATA'
      )
    else:
      layout.label(
        text="No spacecraft parent",
        icon='ERROR'
      )


_CLASSES = (
  VIEW3D_PT_rcs_thruster,
)

def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)


def unregister():
  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
