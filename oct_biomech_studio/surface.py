import pyvista as pv
import numpy as np
from .labels import Label, LABEL_COLORS


def _mesh_from_label(
    labels: np.ndarray, label_value: int, origin, spacing, smoothing: int = 0
):
    mask = (labels == label_value).astype(np.uint8)
    grid = pv.UniformGrid(dimensions=labels.shape, spacing=spacing, origin=origin)
    grid.point_data["mask"] = mask.ravel(order="F")
    surf = grid.contour(isosurfaces=[0.5], method="marching_cubes")
    if smoothing > 0:
        surf = surf.smooth(n_iter=smoothing)
    return surf


def build_surface_meshs(segmentation, smoothing: int = 0):
    labels = segmentation.labels
    meta = segmentation.meta
    meshes = {}
    for label in [Label.ILM, Label.OPL_Henles, Label.IS_OS, Label.IBRPE, Label.OBRPE]:
        try:
            mesh = _mesh_from_label(
                labels, label.value, meta.origin, meta.spacing, smoothing
            )
            meshes[label] = mesh
        except Exception:
            meshes[label] = None
    return meshes



def add_surface_actors(plotter, meshes):
    actors = {}
    for label, mesh in meshes.items():
        if mesh is None or mesh.n_points == 0:
            continue
        color = LABEL_COLORS[label]
        # 美化渲染：启用 PBR，增加平滑着色，模拟生物组织质感
        actor = plotter.add_mesh(
            mesh,
            color=color,
            opacity=0.85,
            name=f"surf_{label.name}",
            pbr=True,             # 基于物理的渲染
            metallic=0.1,         # 低金属度（有机物）
            roughness=0.3,        # 较低粗糙度（湿润/光滑）
            diffuse=0.8,
            specular=0.5,
            smooth_shading=True,  # 平滑着色
        )
        actors[label] = actor
    return actors
