import bpy
import uuid

from mathutils import Matrix
from typing import TYPE_CHECKING, cast
from . import properties

from bpy.types import Context

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

def get_target_spacecraft(context):
  active = context.active_object

  if active is None:
    return None

  if active.rcs_thruster.is_thruster:
    return active.parent

  return active


# create thruster
class OBJECT_OT_add_rcs_thruster(bpy.types.Operator):
  bl_idname = "object.add_rcs_thruster"
  bl_label = "RCS Thruster"
  bl_options = {'REGISTER', 'UNDO'}


  @classmethod
  def poll(cls, context: Context):
    spacecraft = get_target_spacecraft(context)
    return (
      spacecraft is not None
      and not spacecraft.rcs_thruster.is_thruster
    )


  def execute(self, context: Context) -> set["rna_enums.OperatorReturnItems"]:
    spacecraft = get_target_spacecraft(context)

    if spacecraft is None:
      self.report(
        {'ERROR'},
        "Select a spacecraft or one of its thrusters"
      )
      return {'CANCELLED'}

    cursor_world = context.scene.cursor.location.copy()

    try:
      cursor_local = (
        spacecraft.matrix_world.inverted() @ cursor_world
      )
    except(ValueError, ZeroDivisionError):
      self.report(
        {'ERROR'},
        "Spacecraft has non-invertable transform"
      )
      return {'CANCELLED'}

    thruster = bpy.data.objects.new("RCS_Thruster", None)
    context.collection.objects.link(thruster)

    thruster.empty_display_type = 'SINGLE_ARROW'
    thruster.empty_display_size = 0.75
    thruster.show_in_front = True
    # thruster.color = (0.015, 0.75, 1.0, 1.0)

    thruster.parent = spacecraft
    thruster.matrix_parent_inverse = Matrix.Identity(4)

    thruster.location = cursor_local
    thruster.rotation_euler = (0.0, 0.0, 0.0)
    thruster.scale = (1.0, 1.0, 1.0)

    props = cast(properties.RCSThrusterProperties, thruster.rcs_thruster)  # type: ignore[attr-defined]
    # props = thruster.rcs_thruster

    props.is_thruster = True
    props.enabled = True
    props.thrust_newtons = 250.0
    props.stable_id = str(uuid.uuid4())

    bpy.ops.object.select_all(action='DESELECT')

    thruster.select_set(True)
    context.view_layer.objects.active = thruster

    self.report(
      {'INFO'},
      f"Created {thruster.name} on {spacecraft.name}"
    )

    return {'FINISHED'}


def menu_func(self, context: Context):
  self.layout.operator(
    OBJECT_OT_add_rcs_thruster.bl_idname,
    text="RCS Thruster",
    icon='EMPTY_AXIS',
  )

_CLASSES = (
    OBJECT_OT_add_rcs_thruster,
)


def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.VIEW3D_MT_add.append(menu_func) # type: ignore[arg-type]


def unregister():
  bpy.types.VIEW3D_MT_add.remove(menu_func) # type: ignore[arg-type]

  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
