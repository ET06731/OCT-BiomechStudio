import unittest
from oct_biomech_studio.roi import BoxROI, SphereROI


class TestROI(unittest.TestCase):
    def test_box_contains(self):
        roi = BoxROI(center=(0.0, 0.0, 0.0), size=(2.0, 2.0, 2.0))
        self.assertTrue(roi.contains((0.5, 0.5, 0.5)))
        self.assertFalse(roi.contains((2.0, 0.0, 0.0)))

    def test_sphere_contains(self):
        roi = SphereROI(center=(0.0, 0.0, 0.0), radius=1.0)
        self.assertTrue(roi.contains((0.5, 0.5, 0.5)))
        self.assertFalse(roi.contains((1.0, 1.0, 1.0)))


if __name__ == "__main__":
    unittest.main()
