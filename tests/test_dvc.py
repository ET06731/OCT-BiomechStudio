import unittest
from oct_biomech_studio.dvc import FFTBasedDVC, NewtonRaphsonDVC
from oct_biomech_studio.models import VolumeMeta, Volume, DVCParameters
from oct_biomech_studio.roi import BoxROI


class TestDVC(unittest.TestCase):
    def _volume(self):
        import numpy as np
        meta = VolumeMeta(
            origin=(0.0, 0.0, 0.0),
            spacing=(1.0, 1.0, 1.0),
            direction=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
            shape=(10, 10, 10),
        )
        return Volume(data=np.random.rand(10, 10, 10).astype(np.float32), meta=meta)

    def test_fft_stub(self):
        algo = FFTBasedDVC()
        result = algo.compute(
            self._volume(),
            self._volume(),
            BoxROI(center=(0, 0, 0), size=(2, 2, 2)),
            DVCParameters(subset_size=(32, 32, 32), step_size=(8, 8, 8), algorithm="fft"),
        )
        self.assertIsNotNone(result)

    def test_newton_stub(self):
        algo = NewtonRaphsonDVC()
        result = algo.compute(
            self._volume(),
            self._volume(),
            BoxROI(center=(0, 0, 0), size=(2, 2, 2)),
            DVCParameters(subset_size=(32, 32, 32), step_size=(8, 8, 8), algorithm="newton"),
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
