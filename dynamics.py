from dataclasses import dataclass
from mathutils import Vector
from typing import cast

from .models import SpacecraftData
from .sampling import MotionSample

@dataclass(frozen=True)
class DynamicsResult:
  required_force: tuple[float, float, float]
  required_torque: tuple[float, float, float]
  desired_wrench: tuple[float, float, float, float, float, float]


def calculate_required_wrench(
    spacecraft: SpacecraftData,
    motion: MotionSample,
) -> DynamicsResult:
  """
  calculate force and torque require to reproduce sampled animation 
  quantities in spacecraft's local coords
  """

  mass = spacecraft.mass_kg

  acceleration = Vector(motion.linear_acceleration)
  angular_velocity = Vector(motion.angular_velocity)
  angular_acceleration = Vector(motion.angular_acceleration)

  inertia_x, inertia_y, inertia_z = spacecraft.inertia_diagonal

  # apply diagonal inertia tensor to a vector
  def apply_inertia(vector: Vector):
    return Vector((
      inertia_x * vector.x,
      inertia_y * vector.y,
      inertia_z * vector.z
    ))

  force = mass * acceleration

  angular_momentum = apply_inertia(angular_velocity)
  torque = (
    apply_inertia(angular_acceleration) + cast(Vector, angular_velocity.cross(angular_momentum))
  )

  return DynamicsResult(
    required_force=(force.x, force.y, force.z),
    required_torque=(torque.x, torque.y, torque.z),
    desired_wrench=(force.x, force.y, force.z, torque.x, torque.y, torque.z)
  )