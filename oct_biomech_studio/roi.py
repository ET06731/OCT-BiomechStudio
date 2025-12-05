from dataclasses import dataclass
from typing import Tuple
from abc import ABC, abstractmethod
from math import sqrt


Vector3 = Tuple[float, float, float]


class ROI(ABC):
    @abstractmethod
    def contains(self, point: Vector3) -> bool: ...


@dataclass(frozen=True)
class BoxROI(ROI):
    center: Vector3
    size: Vector3

    def bounds(self) -> Tuple[Vector3, Vector3]:
        hx = self.size[0] / 2
        hy = self.size[1] / 2
        hz = self.size[2] / 2
        return (
            (self.center[0] - hx, self.center[1] - hy, self.center[2] - hz),
            (self.center[0] + hx, self.center[1] + hy, self.center[2] + hz),
        )

    def contains(self, point: Vector3) -> bool:
        mn, mx = self.bounds()
        return (
            mn[0] <= point[0] <= mx[0]
            and mn[1] <= point[1] <= mx[1]
            and mn[2] <= point[2] <= mx[2]
        )


@dataclass(frozen=True)
class SphereROI(ROI):
    center: Vector3
    radius: float

    def contains(self, point: Vector3) -> bool:
        dx = point[0] - self.center[0]
        dy = point[1] - self.center[1]
        dz = point[2] - self.center[2]
        return sqrt(dx * dx + dy * dy + dz * dz) <= self.radius
