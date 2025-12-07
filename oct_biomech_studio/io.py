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
    if ext in (".tif", ".tiff"):
        try:
            import tifffile
            import numpy as np
        except ImportError as e:
            raise ImportError("tifffile is required to load TIFF: pip install tifffile") from e
        
        with tifffile.TiffFile(str(p)) as tif:
            # 获取所有帧
            images = []
            for page in tif.pages:
                images.append(page.asarray())
            
            if not images:
                raise ValueError("No image frames found in TIFF file")
            
            arr = np.stack(images, axis=0)
            
        # 确保是3D数据
        if arr.ndim == 2:
            arr = arr[np.newaxis, ...]
        elif arr.ndim > 3:
            arr = arr.reshape(arr.shape[0], arr.shape[1], -1)
        
        meta = _default_meta(
            (int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2])), str(p)
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
