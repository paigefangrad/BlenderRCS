from dataclasses import dataclass

from bpy.types import Object, Scene
from .models import SpacecraftData
from .sampling import MotionSample, sample_motion
from .allocation import AllocationMatrix, build_allocation_matrix
from .dynamics import DynamicsResult, calculate_required_wrench
from .solver import AllocationResult, solve_allocation


@dataclass(frozen=True)
class PipelineSample:
  motion: MotionSample
  Dynamics: DynamicsResult
  allocation: AllocationResult


def evaluate_sample(
    spacecraft: Object,
    scene: Scene,
    spacecraft_data: SpacecraftData,
    allocation_matrix: AllocationMatrix,
    frame: float,
    previous_activations: dict[str, float] | None = None,
    step_frames: float = 0.5
):
  motion = sample_motion(
    spacecraft,
    scene,
    frame,
    spacecraft_data.center_of_mass.position,
    step_frames=step_frames
  )

