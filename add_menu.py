import bpy
import uuid

from mathutils import Matrix
from typing import TYPE_CHECKING, Literal, cast
from . import properties

from bpy.types import Context

if TYPE_CHECKING:
  import bpy.stub_internal.rna_enums as rna_enums


# addon submenu / folder
class VIEW3D_MT_rcs_submenu(bpy.types.Menu):
  bl_label = "RCS Tools"
  bl_idname = "VIEW3D_MT_rcs_submenu"

  def draw(self, context: Context | None) -> None:
    layout = self.layout
    if layout is None: return
    layout.operator(OBJECT_OT_add_rcs_thruster.bl_idname, icon="CON_CAMERASOLVER")
    layout.operator(OBJECT_OT_add_spacecraft.bl_idname, icon="RESTRICT_SELECT_OFF")
    layout.operator(OBJECT_OT_add_com.bl_idname, icon="MATERIAL")

def draw_rcs_submenu(self, context: Context) -> None:
  self.layout.menu(
    VIEW3D_MT_rcs_submenu.bl_idname, 
    text="RCS Tools",
    icon='ORIENTATION_GIMBAL',
  )


def get_target_spacecraft(context: Context):
  active = context.active_object

  if active is None:
    return None

  if active.rcs_thruster.is_thruster:
    return active.parent

  return active


# create spacecraft
class OBJECT_OT_add_spacecraft(bpy.types.Operator):
  bl_idname = "object.add_spacecraft"
  bl_label = "Spacecraft"
  bl_description = "Add a spacecraft container. should be the parent of all RCS components."
  bl_options = {'REGISTER', 'UNDO'}

  @classmethod
  def poll(cls, context: Context):
    return True


  def execute(self, context: Context) -> set["rna_enums.OperatorReturnItems"]:
    cursor_world = context.scene.cursor.location.copy() 

    spacecraft = bpy.data.objects.new("Spacecraft", None)
    context.collection.objects.link(spacecraft)

    spacecraft.empty_display_type = 'PLAIN_AXES'
    spacecraft.empty_display_size = 0.75
    spacecraft.show_in_front = True
    # thruster.color = (0.015, 0.75, 1.0, 1.0)

    # spacecraft.matrix_parent_inverse = Matrix.Identity(4)

    spacecraft.location = cursor_world
    spacecraft.rotation_euler = (0.0, 0.0, 0.0)
    spacecraft.scale = (1.0, 1.0, 1.0)

    props = cast(properties.SpacecraftProperties, spacecraft.spacecraft)  # type: ignore[attr-defined]

    props.is_spacecraft = True
    # props.mass = 
    # props.stable_id = str(uuid.uuid4())

    bpy.ops.object.select_all(action='DESELECT')

    spacecraft.select_set(True)
    context.view_layer.objects.active = spacecraft

    self.report(
      {'INFO'},
      f"Created {spacecraft.name}"
    )

    return {'FINISHED'}


 

# create thruster
class OBJECT_OT_add_rcs_thruster(bpy.types.Operator):
  bl_idname = "object.add_rcs_thruster"
  bl_label = "RCS Thruster"
  bl_description = "Add an RCS thruster to a spacecraft."
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


class OBJECT_OT_add_com(bpy.types.Operator):
  bl_idname = "object.add_com"
  bl_label = "Center of Mass"
  bl_description = "Adds a Center of Mass object to a spacecraft."
  bl_options = {'REGISTER', 'UNDO'}

  @classmethod
  def poll(cls, context: Context) -> bool:
    return True

  def execute(self, context: Context) -> set["rna_enums.OperatorReturnItems"]:
    spacecraft = get_target_spacecraft(context)

    if spacecraft is None:
      self.report(
        {'ERROR'},
        "Select a spacecraft"
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

    com = bpy.data.objects.new("CoM", None)
    context.collection.objects.link(com)

    com.empty_display_type = 'SPHERE' 
    com.empty_display_size = 0.5
    com.show_in_front = True

    com.parent = spacecraft
    com.matrix_parent_inverse = Matrix.Identity(4)

    com.location = cursor_local
    com.rotation_euler = (0.0, 0.0, 0.0)
    com.scale = (1.0, 1.0, 1.0)

    props = cast(properties.COMProperties, com.com)  # type: ignore[attr-defined]
    # props = thruster.rcs_thruster

    props.is_CoM = True
    # props.stable_id = str(uuid.uuid4())

    bpy.ops.object.select_all(action='DESELECT')

    com.select_set(True)
    context.view_layer.objects.active = com

    self.report(
      {'INFO'},
      f"Created {com.name} on {spacecraft.name}"
    )

    return {'FINISHED'}


_CLASSES = (
    VIEW3D_MT_rcs_submenu,
    OBJECT_OT_add_rcs_thruster,
    OBJECT_OT_add_spacecraft,
    OBJECT_OT_add_com,
)


def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.VIEW3D_MT_add.append(draw_rcs_submenu) # type: ignore[arg-type]


def unregister():
  bpy.types.VIEW3D_MT_add.remove(draw_rcs_submenu) # type: ignore[arg-type]

  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
