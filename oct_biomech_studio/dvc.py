from dataclasses import dataclass
from typing import Protocol
from .models import Volume, DVCParameters, DVCResult
from .roi import ROI


class DVCAlgorithm(Protocol):
    def compute(
        self, reference: Volume, deformed: Volume, roi: ROI, params: DVCParameters
    ) -> DVCResult: ...


@dataclass
class FFTBasedDVC:
    def compute(self, reference: Volume, deformed: Volume, roi: ROI, params: DVCParameters) -> DVCResult:
        import numpy as np
        from .models import DisplacementField, StrainTensor
        ref = reference.data
        if ref is None:
            raise ValueError("reference data is None")
        shape = ref.shape
        u = np.zeros(shape, dtype=np.float32)
        v = np.zeros(shape, dtype=np.float32)
        w = np.zeros(shape, dtype=np.float32)
        disp = DisplacementField(u=u, v=v, w=w, meta=reference.meta)
        exx = eyy = ezz = exy = eyz = ezx = np.zeros(shape, dtype=np.float32)
        strain = StrainTensor(exx=exx, eyy=eyy, ezz=ezz, exy=exy, eyz=eyz, ezx=ezx, meta=reference.meta)
        return DVCResult(displacement=disp, strain=strain)


@dataclass
class NewtonRaphsonDVC:
    def compute(self, reference: Volume, deformed: Volume, roi: ROI, params: DVCParameters) -> DVCResult:
        import numpy as np
        from .models import DisplacementField, StrainTensor
        ref = reference.data
        if ref is None:
            raise ValueError("reference data is None")
        shape = ref.shape
        u = np.zeros(shape, dtype=np.float32)
        v = np.zeros(shape, dtype=np.float32)
        w = np.zeros(shape, dtype=np.float32)
        disp = DisplacementField(u=u, v=v, w=w, meta=reference.meta)
        exx = eyy = ezz = exy = eyz = ezx = np.zeros(shape, dtype=np.float32)
        strain = StrainTensor(exx=exx, eyy=eyy, ezz=ezz, exy=exy, eyz=eyz, ezx=ezx, meta=reference.meta)
        return DVCResult(displacement=disp, strain=strain)

def test_dvc():
    import numpy as np
    from .models import Volume, ROI, DVCParameters
    ref = np.zeros((100, 100, 100), dtype=np.float32)
    def = np.zeros((100, 100, 100), dtype=np.float32)
    roi = ROI(x=0, y=0, z=0, width=100, height=100, depth=100)
    params = DVCParameters()