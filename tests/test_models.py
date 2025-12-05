import unittest
from oct_biomech_studio.models import VolumeMeta, Volume, DVCParameters


class TestModels(unittest.TestCase):
    def test_volume_meta(self):
        meta = VolumeMeta(
            origin=(0.0, 0.0, 0.0),
            spacing=(1.0, 1.0, 1.0),
            direction=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
            shape=(10, 10, 10),
        )
        self.assertEqual(meta.shape, (10, 10, 10))

    def test_volume(self):
        meta = VolumeMeta(
            origin=(0.0, 0.0, 0.0),
            spacing=(1.0, 1.0, 1.0),
            direction=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
            shape=(10, 10, 10),
        )
        v = Volume(data=None, meta=meta)
        self.assertIsNone(v.data)

    def test_params(self):
        p = DVCParameters(
            subset_size=(32, 32, 32), step_size=(8, 8, 8), algorithm="fft"
        )
        self.assertEqual(p.algorithm, "fft")


if __name__ == "__main__":
    unittest.main()
