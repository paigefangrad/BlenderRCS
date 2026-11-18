import bpy
import uuid

from typing import Literal
from mathutils import Vector
from .models import ThrusterData, CenterOfMassData, SpacecraftData
from .allocation import build_allocation_matrix
from .solver import solve_allocation
from .sampling import sample_motion
from .dynamics import calculate_required_wrench

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

    sample = sample_motion(
      context.object,
      context.scene,
      context.scene.frame_current,
      config.center_of_mass.position,
    )

    # print("\n========== MOTION SAMPLE ==========")
    # print(f"Frame: {sample.frame}")
    # print(f"CoM world: {sample.center_of_mass_world}")
    # print(f"Linear acceleration: {sample.linear_acceleration}")
    # print(f"Angular velocity: {sample.angular_velocity}")
    # print(f"Angular acceleration: {sample.angular_acceleration}")
    # print("===================================\n")

    dynamics = calculate_required_wrench(config, sample)

    print("\n========== REQUIRED WRENCH ==========")
    print(f"Required force:  {dynamics.required_force}")
    print(f"Required torque: {dynamics.required_torque}")
    print(f"Desired wrench:  {dynamics.desired_wrench}")
    print("=====================================\n")

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
