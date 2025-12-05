from typing import Callable
import pyvista as pv
from .roi import BoxROI, SphereROI


class ROIInteractor:
    def __init__(self, plotter: pv.Plotter, roi_created_cb: Callable):
        self.plotter = plotter
        self.roi_created_cb = roi_created_cb
        self.box_widget = None
        self.sphere_widget = None

    def enable_box_roi(self):
        self.plotter.enable_box_widget(callback=self._on_box_roi)

    def enable_sphere_roi(self):
        self.plotter.enable_sphere_widget(callback=self._on_sphere_roi)

    def disable_all(self):
        if self.plotter.box_widget is not None:
            self.plotter.disable_box_widget()
        if self.plotter.sphere_widget is not None:
            self.plotter.disable_sphere_widget()

    def _on_box_roi(self, bounds):
        x0, x1, y0, y1, z0, z1 = bounds
        center = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        size = (x1 - x0, y1 - y0, z1 - z0)
        roi = BoxROI(center=center, size=size)
        self.roi_created_cb(roi)

    def _on_sphere_roi(self, center, radius):
        roi = SphereROI(center=center, radius=radius)
        self.roi_created_cb(roi)
