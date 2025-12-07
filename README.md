# OCT-BiomechStudio

A PySide6 + PyVista desktop application for **OCT-based 3D biomechanical analysis**.

## Features

- **Data Loading**: `.npy`, `.nii.gz`, `.dcm`, `.tiff` volume pairs (reference + deformed)  
- **Segmentation**: Built-in label mapping for retinal layers (ILM, OPL-Henles, IS/OS, IBRPE, OBRPE)  
- **3D Visualization**: Volume + Marching Cubes surface rendering with layer toggles  
- **ROI Tools**: Interactive Box & Sphere ROI widgets  
- **DVC Engine**: FFT / Newton-Raphson placeholder (ready for your algorithm)  
- **Export**: CSV reports & screenshots

## Quick Start

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. Run the GUI
   ```bash
   python -m oct_biomech_studio.app
   ```

3. Load a volume pair via **File → Load Volume Pair** and explore.

## Requirements

- Python ≥ 3.9
- PySide6 ≥ 6.5
- PyVista ≥ 0.42
- NumPy, SimpleITK, ruff

## Project Structure

```
oct_biomech_studio/
├── __init__.py
├── app.py                 # GUI entry
├── labels.py              # Retinal layer enum & colors
├── models.py              # Data models
├── io.py                  # Volume/segmentation loaders
├── surface.py             # Marching Cubes utilities
├── roi.py                 # ROI geometry
├── roi_interactor.py      # ROI widgets
└── dvc.py                 # DVC algorithm interfaces

tests/
└── test_*.py              # Unit tests
```

## Contributing

- Use `ruff check . && ruff format .` before commits.
- Add tests for new features.

## License

MIT

## Add New Features

- **DVC Algorithm**: Implement your own DVC method in `dvc.py`.
- **Visualization**: Enhance 3D rendering with PyVista's features.
- **Export Formats**: Add support for `.obj`, `.stl`, `.png`, `.jpg`.

test-llm
test2
### 分割.mha文件可视化
### 生成掩膜.mha文件
### test3
