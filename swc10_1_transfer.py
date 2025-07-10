import bg_space as bg
from bg_atlasapi import BrainGlobeAtlas
from bg_space.core import AnatomicalSpace
from brainglobe_utils.IO.cells import get_cells, save_cells
from cellfinder.analyse.analyse import transform_points_to_atlas_space
import numpy as np
from cellfinder.analyse.analyse import transform_points_to_downsampled_space
import os

def Cellfinder_SwcTrans(filename, savefilename):
    # Load data
    data = np.loadtxt(filename, dtype=np.float32, delimiter=' ')
    data_position = data[:, 2:5]

    # Initialize
    size = data_position.shape
    cells = np.zeros(size)
    Imaris_cells = np.zeros(size)

    # Define boundaries and dimensions
    GetExtendMinX = -538
    GetExtendMinY = -8511
    GetExtendMinZ = -23.3
    GetSizeX = 5971
    GetSizeY = 7498
    GetSizeZ = 2025
    GetExtendMaxX = 9165
    GetExtendMaxY = 3673
    GetExtendMaxZ = 6051

    # Calculate pixel scale
    pixel_scale = np.array([
        GetSizeX / (GetExtendMaxX - GetExtendMinX),
        GetSizeY / (GetExtendMaxY - GetExtendMinY),
        GetSizeZ / (GetExtendMaxZ - GetExtendMinZ)
    ])
    # pixel_scale = np.array([1.62, 1.62, 3])  # Alternative manual scaling

    # Calculate pixel offset
    pixel_offset = np.array([GetExtendMinX, GetExtendMinY, GetExtendMinZ])

    # Perform coordinate transformation
    # cells[:, 0] = ((data_position[:, 2] / pixel_scale[2]) + pixel_offset[2] + GetExtendMinZ)/3  # Z-axis
    # cells[:, 2] = ((data_position[:, 1] / pixel_scale[1]) + pixel_offset[1] + GetExtendMinY)/1.625  # Y-axis
    # cells[:, 1] = ((data_position[:, 0] / pixel_scale[0]) + pixel_offset[0] + GetExtendMinZ)/1.625  # X-axis

    Imaris_cells[:, 2] = (data_position[:, 2] / pixel_scale[2]) + pixel_offset[2]  # Z-axis
    Imaris_cells[:, 1] = (data_position[:, 1] / pixel_scale[1]) + pixel_offset[1]  # Y-axis
    Imaris_cells[:, 0] = (data_position[:, 0] / pixel_scale[0]) + pixel_offset[0]  # X-axis

    cells[:, 0] = (Imaris_cells[:, 2] + abs(GetExtendMinZ)) / 3  # IS (Inferior-Superior)
    cells[:, 1] = (Imaris_cells[:, 1] + abs(GetExtendMinY)) / 1.62  # LR (Left-Right)
    cells[:, 2] = (Imaris_cells[:, 0] + abs(GetExtendMinX)) / 1.62  # AP (Anterior-Posterior)

    # If there is a Z-axis flipping issue, adjust here
    # Example: cells[:, 0] = -cells[:, 0]

    # Calculate FilamentsXYZ
    # FilamentsXYZ = cells / pixel_scale  # Add offset if needed
    # cells[:, 0] = (data_position[:, 2] + 23.3) / 3
    # cells[:, 1] = (data_position[:, 1] + 8511) / 1.62
    # cells[:, 2] = (data_position[:, 0] + 2699) / 1.62

    source_origin = 'spr'
    # source_space_re = bg.AnatomicalSpace(source_origin, (1218, 608, 1223), resolution=(10, 10, 10))  # IS AP LR
    source_space_re = bg.AnatomicalSpace(source_origin, (2025, 7498, 5971), resolution=(3, 1.62, 1.62))  # IS AP LR

    downsampled_origin = 'asl'
    downsampled_space = bg.AnatomicalSpace(downsampled_origin, (1320, 800, 1140), resolution=(10, 10, 10))

    # mapped_stack = bg.map_stack_to("asl", "asl", cells)

    # points = transform_points_to_downsampled_space.source_space.map_points_to("asl", points=cells)
    atlas = BrainGlobeAtlas('allen_mouse_10um')

    TT_POINT = transform_points_to_atlas_space(
        points=cells,
        source_space=source_space_re,
        atlas=atlas,
        deformation_field_paths=[
            "PATH/to/registration/deformation_field_0.tiff",
            "PATH/to/registration/deformation_field_1.tiff",
            "PATH/to/registration/deformation_field_2.tiff",
        ],
        downsampled_space=downsampled_space
    )

    # data[:, 2] = TT_POINT[:, 2] * 10  # -11400/2/2   # Z
    # data[:, 3] = TT_POINT[:, 1] * 10  # -8000/2      # Height
    # data[:, 4] = TT_POINT[:, 0] * 10  # Width

    # tt_downsample = transform_points_to_downsampled_space(points=cells, target_space=downsampled_space, source_space=source_space_re)
    # data[:, 2] = 11400 - (TT_POINT[:, 2] * 7.5 + 2000)  # -11400*2/3 -left +right
    # data[:, 3] = TT_POINT[:, 1] * 7.5 + 1000  # +2000#-8000/2  +up - down
    # data[:, 4] = TT_POINT[:, 0] * 10 + 100  # -11400/2  -ant  +post

    data[:, 2] = TT_POINT[:, 2] * 10  # /6.25 + 2500  # -11400/2/2   # Z (AP)
    data[:, 3] = TT_POINT[:, 1] * 10  # 6.25          # Height (X, LR)
    data[:, 4] = TT_POINT[:, 0] * 10  # 6.25 + 500    # Y (IS)

    np.savetxt(savefilename, data, fmt='%d')
    print('DONE')

if __name__ == "__main__":
    filedir = 'INPUT_DIR'
    outdir = 'OUTPUT_DIR'
    filename_list = os.listdir(filedir)
    for name in filename_list:
        filename = filedir + name
        outname = outdir + name
        Cellfinder_SwcTrans(filename, outname)
