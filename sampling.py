import bpy

from bpy.types import Scene, Object
from mathutils import Vector, Quaternion
from dataclasses import dataclass


@dataclass(frozen=True)
class MotionSample:
  frame:float
  center_of_mass_world: tuple[float, float, float]
  linear_acceleration: tuple[float, float, float]
  angular_velocity: tuple[float, float, float]
  angular_acceleration: tuple[float, float, float]


def set_scene_time(scene: Scene, frame: float) -> None:
  """set blender's frame, including fractional"""
  whole_frame = int(frame // 1)
  subframe = frame - whole_frame
  scene.frame_set(whole_frame, subframe=subframe)


def sample_pose(spacecraft: Object, scene: Scene, frame: float, com_local) -> tuple[Vector, Quaternion]:
  """
  eval the spacecraft at a particular frame
  returns world-space CoM pos and world-space orientation
  """
  set_scene_time(scene, frame)

  depsgraph = bpy.context.evaluated_depsgraph_get()
  evaluated = spacecraft.evaluated_get(depsgraph)

  matrix = evaluated.matrix_world.copy()

  com_world = matrix @ Vector(com_local)
  orientation = matrix.to_quaternion().normalized()

  return com_world, orientation


def angular_velocity_world(q_start: Quaternion, q_end: Quaternion, duration: float):
  """
  calculate average world-space angular velocity between two orientations 
  """
  delta = (q_end @ q_start.conjugated().normalized())

  # use shortest equivalent quaternion rotation
  if delta.w < 0:
      delta = Quaternion((
        -delta.w,
        -delta.x,
        -delta.y,
        -delta.z,
      ))

  axis, angle = delta.to_axis_angle()

  return axis * (angle / duration)


def sample_motion(
    spacecraft: Object,
    scene: Scene,
    frame: float,
    com_local,
    step_frames: float = 0.5
):
  """
  calculate spacecraft's kinematics at a given frame 
  """
  if step_frames <= 0:
    raise ValueError("step_frames must be positive")

  fps = scene.render.fps / scene.render.fps_base
  dt = step_frames / fps

  original_frame = scene.frame_current
  original_subframe = scene.frame_subframe

  try:
    # 5 orientatinos needed for angular accel
    p_minus, q_minus = sample_pose(spacecraft, scene, frame - step_frames, com_local)
    p_center, q_center = sample_pose(spacecraft, scene, frame, com_local)
    p_plus, q_plus = sample_pose(spacecraft, scene, frame + step_frames, com_local)
    _p_minus2, q_minus2 = sample_pose(spacecraft, scene, frame - 2 * step_frames, com_local)
    _p_plus2, q_plus2 = sample_pose(spacecraft, scene, frame + 2 * step_frames, com_local)

    linear_acceleration_world = (
      p_plus - 2.0 * p_center + p_minus
    ) / (dt * dt)

    angular_velocity_world_center = angular_velocity_world(
      q_minus,
      q_plus,
      2.0 * dt,
    )

    angular_velocity_before = angular_velocity_world(
      q_minus2,
      q_center,
      2.0 * dt,
    )

    angular_velocity_after = angular_velocity_world(
      q_center,
      q_plus2,
      2.0 * dt,
    )

    angular_acceleration_world = (
      angular_velocity_after - angular_velocity_before
    ) / (2.0 * dt)

    # convert world-space into spacecraft local
    inverse_rotation = q_center.conjugated()

    linear_acceleration_local = inverse_rotation @ linear_acceleration_world
    angular_velocity_local = inverse_rotation @ angular_velocity_world_center
    angular_acceleration_local = inverse_rotation @ angular_acceleration_world

    return MotionSample(
      frame=frame,
      center_of_mass_world=(p_center.x, p_center.y, p_center.z),
      linear_acceleration=(linear_acceleration_local.x, linear_acceleration_local.y, linear_acceleration_local.z),
      angular_velocity=(angular_velocity_local.x, angular_velocity_local.y, angular_velocity_local.z),
      angular_acceleration=(angular_acceleration_local.x, angular_acceleration_local.y, angular_acceleration_local.z),
    )
  finally:
    # return to original frame
    scene.frame_set(
      original_frame, subframe=original_subframe
    )