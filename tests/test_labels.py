import unittest
from oct_biomech_studio.labels import Label, LABEL_COLORS


class TestLabels(unittest.TestCase):
    def test_enum_values(self):
        self.assertEqual(Label.Background.value, 0)
        self.assertEqual(Label.ILM.value, 1)
        self.assertEqual(Label.OPL_Henles.value, 2)
        self.assertEqual(Label.IS_OS.value, 3)
        self.assertEqual(Label.IBRPE.value, 4)
        self.assertEqual(Label.OBRPE.value, 5)

    def test_color_mapping(self):
        self.assertEqual(len(LABEL_COLORS), 6)
        self.assertIn(Label.OBRPE, LABEL_COLORS)


if __name__ == "__main__":
    unittest.main()
