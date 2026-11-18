from dataclasses import dataclass


@dataclass(frozen=True)
class ThrusterData:
  id: str
  position: tuple[float, float, float]
  exhaust_direction: tuple[float, float, float]
  thrust_newtons: float
  enabled: bool


@dataclass(frozen=True)
class CenterOfMassData:
  id: str
  position: tuple[float, float, float]


@dataclass(frozen=True)
class SpacecraftData:
  id: str
  mass_kg: float
  inertia_diagonal: tuple[float, float, float]
  center_of_mass: CenterOfMassData | None
  thrusters: dict[str, ThrusterData]