from typing import Tuple
from pathlib import Path
from .models import VolumeMeta, Volume, Segmentation, VolumePair


def _identity_direction() -> Tuple[
    float, float, float, float, float, float, float, float, float
]:
    return (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def _default_meta(shape: Tuple[int, int, int], path: str) -> VolumeMeta:
    return VolumeMeta(
        origin=(0.0, 0.0, 0.0),
        spacing=(1.0, 1.0, 1.0),
        direction=_identity_direction(),
        shape=shape,
        path=path,
    )


def load_volume(path: str) -> Volume:
    p = Path(path)
    
    if p.is_dir():
        try:
            import SimpleITK as sitk
        except ImportError:
            raise ImportError("SimpleITK is required to load DICOM series")
            
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesFileNames(str(p))
        if not series_ids:
            raise ValueError(f"No DICOM series found in {path}")
            
        reader.SetFileNames(series_ids)
        img = reader.Execute()
        
        arr = sitk.GetArrayFromImage(img)
        meta = VolumeMeta(
            origin=img.GetOrigin(),
            spacing=img.GetSpacing(),
            direction=tuple(img.GetDirection()),
            shape=(int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2])),
            path=str(p),
        )
        return Volume(data=arr, meta=meta)

    ext = p.suffix.lower()
    if ext == ".npy":
        import numpy as np

        arr = np.load(str(p))
        if arr.ndim != 3:
            raise ValueError("volume must be 3D")
        meta = _default_meta(
            (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2])), str(p)
        )
        return Volume(data=arr, meta=meta)
    if ext in (".nii", ".gz") or p.name.endswith(".nii.gz"):
        try:
            import SimpleITK as sitk
            import numpy as np
        except Exception:
            raise ImportError("SimpleITK is required to load NIfTI")
        img = sitk.ReadImage(str(p))
        arr = sitk.GetArrayFromImage(img)
        origin = img.GetOrigin()
        spacing = img.GetSpacing()
        direction = tuple(img.GetDirection())
        shape = (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2]))
        meta = VolumeMeta(
            origin=origin,
            spacing=spacing,
            direction=direction,
            shape=shape,
            path=str(p),
        )
        return Volume(data=arr, meta=meta)
    if ext in (".dcm",):
        try:
            import SimpleITK as sitk
        except Exception:
            raise ImportError("SimpleITK is required to load DICOM")
        img = sitk.ReadImage(str(p))
        arr = sitk.GetArrayFromImage(img)
        origin = img.GetOrigin()
        spacing = img.GetSpacing()
        direction = tuple(img.GetDirection())
        shape = (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2]))
        meta = VolumeMeta(
            origin=origin,
            spacing=spacing,
            direction=direction,
            shape=shape,
            path=str(p),
        )
        return Volume(data=arr, meta=meta)
    raise NotImplementedError("unsupported format")


def load_segmentation(path: str) -> Segmentation:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".npy":
        import numpy as np

        arr = np.load(str(p))
        if arr.ndim != 3:
            raise ValueError("segmentation must be 3D")
        meta = _default_meta(
            (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2])), str(p)
        )
        return Segmentation(labels=arr, meta=meta)
    if ext in (".nii", ".gz") or p.name.endswith(".nii.gz"):
        try:
            import SimpleITK as sitk
        except Exception:
            raise ImportError("SimpleITK is required to load NIfTI")
        img = sitk.ReadImage(str(p))
        arr = sitk.GetArrayFromImage(img)
        origin = img.GetOrigin()
        spacing = img.GetSpacing()
        direction = tuple(img.GetDirection())
        shape = (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2]))
        meta = VolumeMeta(
            origin=origin,
            spacing=spacing,
            direction=direction,
            shape=shape,
            path=str(p),
        )
        return Segmentation(labels=arr, meta=meta)
    raise NotImplementedError("unsupported format")


def load_volume_pair(reference_path: str, deformed_path: str) -> VolumePair:
    ref = load_volume(reference_path)
    defo = load_volume(deformed_path)
    return VolumePair(reference=ref, deformed=defo)
