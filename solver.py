from .models import SpacecraftData
from .allocation import AllocationMatrix
from mathutils import Vector
from math import isfinite
from dataclasses import dataclass


@dataclass(frozen=True)
class AllocationResult:
  activations: dict[str, float]
  achieved_wrench: tuple[float, ...]
  residual: tuple[float, ...]
  iterations: int
  converged: bool


def solve_allocation(
    allocation: AllocationMatrix,
    desired_wrench: tuple[float, ...],
    previous_activations: dict[str, float] | None = None,
    force_scale: float = 100.0,
    torque_scale: float = 100.0,
    regularization: float = 0.01,
    smoothness: float = 0.1,
    max_iterations: int = 2000,
    tolerance: float = 1e-7,
) -> AllocationResult:
  """
  find bounded thruster activations that approximate desired wrench
  regularization penalizes total activation
  smoothness penalizes changes from the previous sample 
  """

  if len(desired_wrench) != 6:
    raise ValueError("desired wrench must be 6D")

  if force_scale <= 0 or torque_scale <= 0:
    raise ValueError("Force and torque scales must be positive")

  if regularization < 0 or smoothness < 0:
    raise ValueError("Penalties cannot be negative")

  if max_iterations < 1 or tolerance <= 0:
    raise ValueError("Invalid iteration settings")

  if not all(isfinite(v) for v in desired_wrench):
    raise ValueError("Desired wrench contains non-finite values")

  ids = allocation.thruster_ids
  columns = allocation.columns
  count = len(ids)

  if len(columns) != count or any(len(c) != 6 for c in columns):
    raise ValueError("Invalid allocation matrix dimensions")

  if any(not all(isfinite(v) for v in c) for c in columns):
    raise ValueError("Allocation matrix contains non-finite values")

  if count == 0:
      return AllocationResult(
        activations={},
        achieved_wrench=(0.0,) * 6,
        residual=tuple(-v for v in desired_wrench),
        iterations=0,
        converged=True
      )

  previous_activations = previous_activations or {}
  previous = [
    min(1.0, max(0.0, previous_activations.get(tid, 0.0)))
    for tid in ids
  ]

  # normalize force and torque for comparisson
  scales = (
    1.0 / force_scale,
    1.0 / force_scale,
    1.0 / force_scale,
    1.0 / torque_scale,
    1.0 / torque_scale,
    1.0 / torque_scale,
  )

  # convert col to matrix rows
  matrix = [
    [columns[j][i] * scales[i] for j in range(count)]
    for i in range(6)
  ]

  target = [
    desired_wrench[i] * scales[i]
    for i in range(6)
  ]

  # Build the quadratic objective:
  #
  # ||A*u - target||²
  # + regularization*||u||²
  # + smoothness*||u - previous||²
  hessian = [[0.0] * count for _ in range(count)]
  gradient_target = [0.0] * count

  for i in range(count):
    for row in range(6):
      gradient_target[i] += matrix[row][i] * target[row]

    gradient_target[i] += smoothness * previous[i]

    for j in range(count):
      hessian[i][j] = sum(
        matrix[row][i] * matrix[row][j]
        for row in range(6)
      )

      if i == j:
        hessian[i][j] += regularization + smoothness

  # upper bound on largest eigenvalue of the hessian
  lipschitz = max(
    sum(abs(value) for value in row)
    for row in hessian
  )

  if lipschitz <= 0:
    lipschitz = 1.0

  #start at previous sample
  x = previous[:]
  y = x[:]
  momentum = 1.0

  converged = False

  for iteration in range(1, max_iterations + 1):
    # Gradient of quadratic objective
    gradient = [
      sum(hessian[i][j] * y[j] for j in range(count))
      - gradient_target[i]
      for i in range(count)
    ]

    # gradient step followed by projection onto [0, 1]
    next_x = [
      min(1.0, max(0.0, y[i] - gradient[i] / lipschitz))
      for i in range(count)
    ]

    change = max(
      abs(next_x[i] - x[i])
      for i in range(count)
    )

    if change < tolerance:
      x = next_x
      converged = True
      break

    next_momentum = (
      1.0 + (1.0 + 4.0 * momentum * momentum) ** 0.5
    ) / 2.0

    factor = (momentum - 1.0) / next_momentum

    y = [
      next_x[i] + factor * (next_x[i] - x[i])
      for i in range(count)
    ]

    x = next_x
    momentum = next_momentum

  #calculate actual wrench produced by solution
  achieved = tuple(
    sum(columns[j][i] * x[j] for j in range(count))
    for i in range(6)
  )

  residual = tuple(
    desired_wrench[i] - achieved[i]
    for i in range(6)
  )

  return AllocationResult(
    activations={
      tid: x[i]
      for i, tid in enumerate(ids)
    },
    achieved_wrench=achieved,
    residual=residual,
    iterations=iteration, # type: ignore
    converged=converged
  )