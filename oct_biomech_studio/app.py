from PySide6.QtWidgets import (

    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import  QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCT Biomech Studio")
        self.resize(1200, 800)

        # Menu bar
        menubar = self.menuBar()
        file_menu = QMenu("File", self)
        load_ref_act = QAction("Load Reference", self)
        load_def_act = QAction("Load Deformed", self)
        load_pair_act = QAction("Load Volume Pair", self)
        file_menu.addAction(load_ref_act)
        file_menu.addAction(load_def_act)
        file_menu.addAction(load_pair_act)
        menubar.addMenu(file_menu)

        load_ref_act.triggered.connect(self._load_reference)
        load_def_act.triggered.connect(self._load_deformed)
        load_pair_act.triggered.connect(self._load_volume_pair)

        # Central splitter
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left panel
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.btn_segment = QPushButton("Segment")
        self.btn_compute = QPushButton("Compute DVC")
        self.btn_export = QPushButton("Export Report")

        # Layer control
        from PySide6.QtWidgets import QCheckBox

        self.layer_checks = {}
        for label in ["ILM", "OPL_Henles", "IS_OS", "IBRPE", "OBRPE"]:
            chk = QCheckBox(label)
            chk.setChecked(True)
            chk.stateChanged.connect(self._toggle_layer)
            self.layer_checks[label] = chk
            left_layout.addWidget(chk)

        self.btn_roi_box = QPushButton("ROI Box")
        self.btn_roi_sphere = QPushButton("ROI Sphere")
        left_layout.addWidget(self.btn_roi_box)
        left_layout.addWidget(self.btn_roi_sphere)
        left_layout.addWidget(self.btn_segment)
        left_layout.addWidget(self.btn_compute)
        left_layout.addWidget(self.btn_export)
        left_layout.addStretch()

        self.roi_interactor = None
        self.btn_roi_box.clicked.connect(self._enable_box_roi)
        self.btn_roi_sphere.clicked.connect(self._enable_sphere_roi)

        # Right 3D view
        try:
            from pyvistaqt import QtInteractor

            self.plotter = QtInteractor()
            right = self.plotter
        except Exception:
            right = QLabel("PyVista/pyvistaqt not available")

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def _load_reference(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Reference Volume", "", "Volumes (*.npy *.nii *.nii.gz *.dcm)"
        )
        if path:
            try:
                from .io import load_volume

                self.ref_vol = load_volume(path)
                QMessageBox.information(self, "Loaded", f"Reference loaded: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _load_deformed(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Deformed Volume", "", "Volumes (*.npy *.nii *.nii.gz *.dcm)"
        )
        if path:
            try:
                from .io import load_volume

                self.def_vol = load_volume(path)
                QMessageBox.information(self, "Loaded", f"Deformed loaded: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _load_volume_pair(self):
        ref_path, _ = QFileDialog.getOpenFileName(
            self, "Load Reference Volume", "", "Volumes (*.npy *.nii *.nii.gz *.dcm)"
        )
        if not ref_path:
            return
        def_path, _ = QFileDialog.getOpenFileName(
            self, "Load Deformed Volume", "", "Volumes (*.npy *.nii *.nii.gz *.dcm)"
        )
        if not def_path:
            return
        try:
            from .io import load_volume_pair

            self.volume_pair = load_volume_pair(ref_path, def_path)
            QMessageBox.information(
                self, "Loaded", f"Pair loaded: {ref_path} & {def_path}"
            )
            self._show_volume_pair()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _show_volume_pair(self):
        if not hasattr(self, "volume_pair"):
            return
        try:
            import pyvista as pv

            arr = self.volume_pair.reference.data
            grid = pv.UniformGrid(
                dimensions=arr.shape,
                spacing=self.volume_pair.reference.meta.spacing,
                origin=self.volume_pair.reference.meta.origin,
            )
            grid.point_data["values"] = arr.ravel(order="F")
            self.plotter.clear()
            self.plotter.add_volume(grid, cmap="gray", opacity="linear")
            self._build_surface_actors()
            self.plotter.reset_camera()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _build_surface_actors(self):
        if not hasattr(self, "segmentation"):
            return
        try:
            from .surface import build_surface_meshs, add_surface_actors

            self.surface_meshes = build_surface_meshs(self.segmentation, smoothing=1)
            self.surface_actors = add_surface_actors(self.plotter, self.surface_meshes)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _toggle_layer(self, state):
        sender = self.sender()
        label_name = sender.text()
        from .labels import Label

        label = getattr(Label, label_name)
        if label in self.surface_actors:
            actor = self.surface_actors[label]
            actor.SetVisibility(bool(state))

    def _enable_box_roi(self):
        try:
            from .roi_interactor import ROIInteractor

            if self.roi_interactor is None:
                self.roi_interactor = ROIInteractor(self.plotter, self._roi_created)
            self.roi_interactor.enable_box_roi()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _enable_sphere_roi(self):
        try:
            from .roi_interactor import ROIInteractor

            if self.roi_interactor is None:
                self.roi_interactor = ROIInteractor(self.plotter, self._roi_created)
            self.roi_interactor.enable_sphere_roi()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _roi_created(self, roi):
        self.current_roi = roi
        QMessageBox.information(self, "ROI", f"ROI created: {roi}")


def launch():
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
