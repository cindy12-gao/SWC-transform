# SWC Transformation Pipeline
This pipeline transforms SWC files from Imaris filament reconstructions to align with the Allen Mouse Brain Atlas.

## Prerequisites
- **Imaris** v10.1.0
- **Python** 3.10 (for cellfinder and BrainGlobe) and **Python** 3.7 (for Imaris plugins)
- **BrainGlobe** (v1.3.1)
- **Amira** v2022 (for visualization)

## Installation

### 1. Set up "cellfinder" environment for SWC transformation
```bash
conda create -n cellfinder python=3.10
conda activate cellfinder
pip install cellfinder==0.8.1
pip install bg_space
pip install bg_atlasapi
```

### 2. Install SWC plugins for Imaris
 1.	Download plugins from:
    [https://github.com/Elsword016/Swc-plugins-for-Imaris-10]
   	
 2.	Set up environment:
```bash
cd PATH\TO\Swc-plugins-for-Imaris-10-main
conda env create -f environment.yml
```

 3. Configure Imaris:
    - Open Preferences (Ctrl+P) → Custom Tools
    - set “Python 3.7 Application” to: `~/Anaconda/envs/imarisbridge/python.exe`

### 3. Install BrainGlobe for Allen mouse brain registration
   - Create environment and install BrainGlobe following the documentation in [BrainGlobe](https://brainglobe.info/documentation/index.html)

## Usage
### 1. Allen Mouse Brain Registration (BrainGlobe)
   1. Download atlas
  ```
   brainglobe install -a allen-mouse_10um
   ```

   2. Registration
```python
   brainmapper -s PATH_to_signal_channel -b PATH_to_Reference_channel -o PATH_to_output_directory -v 1 1 1 --orientation asr --atlas allen_mouse_10um --no-detection
 ```
   - Atlas: allen_mouse_10um
     
   - Voxel size: `-v`
    - If the voxel size of your data is `1x2x3` (XYZ), use `3 2 1` (ZYX)
     
   - Orientation: `--orientation`

| View        | First Plane              | Description             | Code   |
|-------------|--------------------------|-------------------------|--------|
| Coronal     | Olfactory bulb           | Dorsal up              | `asr`  |
| Coronal     | Olfactory bulb           | Ventral up             | `ail`  |
| Coronal     | Cerebellum               | Dorsal up              | `psl`  |
| Coronal     | Cerebellum               | Ventral up             | `pir`  |
| Horizontal  | Dorsal                   | Olfactory bulb up      | `sal`  |
| Horizontal  | Dorsal                   | Cerebellum up          | `spr`  |
| Horizontal  | Ventral                  | Olfactory bulb up      | `iar`  |
| Horizontal  | Ventral                  | Cerebellum up          | `ipl`  |

   3. Output files (deformation field files):
  ```bash
/Registration/
├── deformation_field_0.tiff
└── deformation_field_1.tiff
└── deformation_field_2.tiff
```

### 2. Export SWC from Imaris
 1.	Complete neuronal reconstruction using Filament tool
   - Notes: For accurate SWC file registration, the raw data used for registration and filaments must have matching orientations and scales.
     
 2.	Export filaments to SWC:
   - Use “SWC exporter 1.0” from ImageProcessing menu
   - Set output folder
     
### 3. Transform SWC files
 1.	Open `swc10_1_transfer.py` ("`./SWC/swc10_1_transfer.py`")
   - Demo file: `./SWC/Example/swc10_1_transfer_demo.py`
     
 2.	Configure parameters:
   - Define boundaries and dimensions (find in Imaris Image Properties)
```python
    GetExtendMinX = Coordinates_Min_X
    GetExtendMinY = Coordinates_Min_Y
    GetExtendMinZ = Coordinates_Min_Z
    GetSizeX = Size_X
    GetSizeY = Size_Y
    GetSizeZ = Size_Z
    GetExtendMaxX = Coordinates_Max_X
    GetExtendMaxY = Coordinates_Max_Y
    GetExtendMaxZ = Coordinates_Max_Z
```

   - Define orientation (Same as orientation in Registration)
```python
source_origin = 'spr'  
```

   - Define source space (IS, AP, LR dimensions)
     - IS (Inferior-Superior)
     - AP (Anterior-Posterior)
     - LR (Left-Right)
```python
source_space_re = bg.AnatomicalSpace(source_origin, (Size_IS, Size_AP, Size_LR), resolution=(Voxel_Size_IS, Voxel_Size_AP, Voxel_Size_LR))
```
For example, 
In `spr` orientation, 
```python
Size_IS = Size_Z
Size_AP = Size_Y
Size_LR = Size_X
Voxel_Size_IS = Voxel_Size_Z
Voxel_Size_AP = Voxel_Size_Y
Voxel_Size_LR = Voxel_Size_X
```

   - Set deformation_field_paths
```python
deformation_field_paths=[
            "PATH/to/registration/deformation_field_0.tiff",
            "PATH/to/registration/deformation_field_1.tiff",
            "PATH/to/registration/deformation_field_2.tiff",
        ]
```
Demo files: `./SWC/Example/Demo_registration/Registraion/`

   - Set input/output paths
```python
filedir = 'INPUT_DIR'    # SWC input folder
outdir = 'OUTPUT_DIR'    # SWC Output folder
```
  - Demo files: `./SWC/Example/SWC_Input/`
    
 3.	Save the configured `swc10_1_transfer.py`
    
 4. Run SWC Transformation
  - Set environment to “cellfinder”
    ```bash
    conda activate cellfinder
    ```
    
  - Run swc10-1transer.py
    - Demo file: `./SWC/Example/swc10_1_transfer_demo.py`

  ```bash
   cd PATH/to/folder
   python swc10_1_transfer.py
  ```
   - Output files will be saved in the specified output folder.
     
### 4. Visualize Results
  1. Open Amira
  2. Load Allen Adult Mouse Brain Contour (10µm resolution) ("`./SWC/ccf_22_1.stl`")
  3. Import transformed SWC files
     - Demo files: `./SWC/Example/SWC_Output/`

## Workflow Diagram
```
Imaris → Export SWC using SWC plugins→ Transform using Python → Transformed SWC → Visualize in Amira
   ↑                                               ↑
Filaments                                Registration Fields  
                                                   ↑
                                              Registration
```

## References
- Cellfinder [https://github.com/brainglobe/cellfinder]
- Swc-plugins-for-Imaris-10 [https://github.com/Elsword016/Swc-plugins-for-Imaris-10]
- [Brainglobe Documentation](https://brainglobe.info)
- [SWC Documentation](https://swc-specification.readthedocs.io/en/latest/swc.html)
