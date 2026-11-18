import bpy
import uuid

from typing import Literal
from mathutils import Vector
from .models import ThrusterData, CenterOfMassData, SpacecraftData
from .allocation import build_allocation_matrix

from bpy.types import Context, Operator, Object

class RCS_OT_check_ship(Operator):
  bl_idname="rcs.check_ship"
  bl_label="rcs.check_ship"
  bl_options={'INTERNAL', 'UNDO'}

  def execute(self, context: Context) -> set[Literal['RUNNING_MODAL'] | Literal['CANCELLED'] | Literal['FINISHED'] | Literal['PASS_THROUGH'] | Literal['INTERFACE']]:
    if context.object is None:
      self.report(
        {"ERROR"},
        message="no ship selected"
      )
      return {'CANCELLED'}

    try:
      config = collect_spacecraft(context.object)
      allocation = build_allocation_matrix(config)

    except SpacecraftConfigurationError as error:
      self.report({'ERROR'}, str(error))
      return {'CANCELLED'}


    # print("\n========== RCS ALLOCATION MATRIX ==========")
    # print(f"Spacecraft: {context.object.name}")
    # print(f"Mass: {config.mass_kg:.2f} kg")
    # print(f"Thrusters: {len(allocation.thruster_ids)}")

    # for thruster_id, column in zip(
    #     allocation.thruster_ids,
    #     allocation.columns,
    # ):
    #     fx, fy, fz, tx, ty, tz = column

    #     print(f"\nThruster: {thruster_id}")
    #     print(f"  Force:  ({fx:10.3f}, {fy:10.3f}, {fz:10.3f}) N")
    #     print(f"  Torque: ({tx:10.3f}, {ty:10.3f}, {tz:10.3f}) Nm")

    # print("\n===========================================\n")

    self.report({'INFO'}, "Allocation matrix printed to console")

    return {'FINISHED'}



    self.report(
      {'INFO'},
      message=f"check ship done"
    )

    return {'FINISHED'}


def collect_spacecraft(spacecraft: Object) -> SpacecraftData:

  errors = []

  if not spacecraft.spacecraft.is_spacecraft:
    raise SpacecraftConfigurationError(f"{spacecraft.name} is not an RCS spacecraft")

  spacecraft_id = spacecraft.spacecraft.stable_id
  mass_kg = spacecraft.spacecraft.mass_kg

  if not spacecraft_id:
    errors.append("Spacecraft missing ID")

  if not mass_kg:
    errors.append("Spacecraft missing mass")

  thrusters = {}
  center_of_mass = None

  try:
    for obj in get_decendants(spacecraft):
      # discover thruster
      if obj.rcs_thruster.is_thruster:
        props = obj.rcs_thruster
        thruster_id = props.stable_id

        if not thruster_id:
          errors.append(f"Thruster {obj.name} is missing ID")
          continue

        # duplicated thrusters share an ID, give them a new one if dupe is found
        if thruster_id in thrusters:
          props.stable_id = str(uuid.uuid4())
          thruster_id = props.stable_id

        position, exhaust_direction = get_local_transform(spacecraft, obj)

        if props.thrust_newtons <= 0:
          errors.append(f"thruster '{obj.name}' has no positive thrust value")
          continue

        thrusters[thruster_id] = ThrusterData(
          id=thruster_id,
          position=(position.x, position.y, position.z),
          exhaust_direction=(exhaust_direction.x, exhaust_direction.y, exhaust_direction.z),
          thrust_newtons=props.thrust_newtons,
          enabled=props.enabled,
        )

      # discover center of mass
      elif obj.com.is_com:
        if center_of_mass is not None:
          errors.append("Spaceship contains multiples centers of mass")
          continue

        com_id = obj.com.stable_id
        position, _exhaust_direction = get_local_transform(spacecraft, obj)
        center_of_mass = CenterOfMassData(
          id=com_id,
          position=(position.x, position.y, position.z)
        )
  except Exception as exc:
    import traceback

    traceback.print_exc()

    errors.append(
      f"Unexpected error while processing spacecraft: "
      f"{type(exc).__name__}: {exc}"
    )

  if center_of_mass is None:
    errors.append("No center of mass found")

  if not thrusters:
    errors.append("No thrusters found")

  if errors:
    raise SpacecraftConfigurationError(
      "Invalid spacecraft configuration: \n- "
      + "\n- ".join(errors)
    )

  data = SpacecraftData(
    id=spacecraft_id,
    mass_kg = mass_kg,
    inertia_diagonal=(
      spacecraft.spacecraft.inertia_x,
      spacecraft.spacecraft.inertia_y,
      spacecraft.spacecraft.inertia_z,
    ),
    center_of_mass=center_of_mass,
    thrusters=thrusters
  )

  return data



def get_decendants(root: Object):
  for child in root.children:
    if child.spacecraft.is_spacecraft:
      continue

    yield child

    yield from get_decendants(child)


def get_local_transform(spacecraft: Object, obj: Object) -> tuple[Vector, Vector]:

  relative_matrix = spacecraft.matrix_world.inverted() @ obj.matrix_world

  position, rotation, _scale = relative_matrix.decompose()
  # exhaust_direction = (rotation @ Vector((0.0, 0.0, -1.0))).normalized()
  exhaust_direction = rotation @ Vector((0.0, 0.0, -1.0))
  exhaust_direction = exhaust_direction.normalized()

  return position, exhaust_direction


class SpacecraftConfigurationError(Exception):
  """Raised when a spacecraft hierarchy is invalid."""


_CLASSES = (
  RCS_OT_check_ship,
)

def register():
  for cls in _CLASSES:
    bpy.utils.register_class(cls)


def unregister():
  for cls in reversed(_CLASSES):
    bpy.utils.unregister_class(cls)
