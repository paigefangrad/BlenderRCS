from dataclasses import dataclass
from mathutils import Vector
from .models import SpacecraftData

@dataclass(frozen=True)
class AllocationMatrix:
  thruster_ids: tuple[str, ...]
  columns: tuple[tuple[float, ...], ...]


def build_allocation_matrix(spacecraft: SpacecraftData) -> AllocationMatrix:
  """
  6D control allocation matrix generation
  Each column repressents a thruster's max force and torque contribution
  """
  columns = []
  thruster_ids = []

  com_position = Vector(spacecraft.center_of_mass.position)

  for thruster_id, thruster in spacecraft.thrusters.items():
    if not thruster.enabled:
      continue

    position = Vector(thruster.position)
    exhaust_direction = Vector(thruster.exhaust_direction)

    force = -exhaust_direction * thruster.thrust_newtons

    lever_arm = position - com_position

    lever_arm: Vector
    force: Vector


    # torque: Vector = lever_arm.cross(force)
    torque = Vector((
      lever_arm.y * force.z - lever_arm.z * force.y,
      lever_arm.z * force.x - lever_arm.x * force.z,
      lever_arm.x * force.y - lever_arm.y * force.x,
    ))

    columns.append((
      force.x,
      force.y,
      force.z,
      torque.x,
      torque.y,
      torque.z,
    )) 

    thruster_ids.append(thruster_id)

  return AllocationMatrix(
    thruster_ids=tuple(thruster_ids),
    columns=tuple(columns)
  )

def register():
  pass

def unregister():
  pass