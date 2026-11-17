import bpy

from bpy.types import Context
from typing import Literal


class SelectParent(bpy.types.Operator):
  bl_idname = 'rcs.select_parent'
  bl_label = 'selects an objects parent'

  def execute(self, context: Context) -> set[Literal['RUNNING_MODAL'] | Literal['CANCELLED'] | Literal['FINISHED'] | Literal['PASS_THROUGH'] | Literal['INTERFACE']]:
    if context.object is not None and context.object.parent:
      bpy.ops.object.select_all(action='DESELECT')
      context.view_layer.objects.active = context.object.parent.select_set(True)
      return {'FINISHED'}
    else:
      return {'CANCELLED'}


_CLASSES = (
  SelectParent,
)

def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)


def unregister():
  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
