from dataclasses import dataclass
from typing import Tuple, Optional, Any, Literal


Vector3 = Tuple[float, float, float]
Shape3D = Tuple[int, int, int]


@dataclass(frozen=True)
class VolumeMeta:
    origin: Vector3
    spacing: Vector3
    direction: Tuple[float, float, float, float, float, float, float, float, float]
    shape: Shape3D
    path: Optional[str] = None


@dataclass
class Volume:
    data: Any
    meta: VolumeMeta


@dataclass
class VolumePair:
    reference: Volume
    deformed: Volume


@dataclass
class Segmentation:
    labels: Any
    meta: VolumeMeta


@dataclass(frozen=True)
class DVCParameters:
    subset_size: Tuple[int, int, int]
    step_size: Tuple[int, int, int]
    algorithm: Literal["fft", "newton"]


@dataclass
class DisplacementField:
    u: Any
    v: Any
    w: Any
    meta: VolumeMeta


@dataclass
class StrainTensor:
    exx: Any
    eyy: Any
    ezz: Any
    exy: Any
    eyz: Any
    ezx: Any
    meta: VolumeMeta


@dataclass
class DVCResult:
    displacement: DisplacementField
    strain: StrainTensor
