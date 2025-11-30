# preprocess.py
import os
import numpy as np
import nibabel as nib
import pydicom
import cv2
from skimage.transform import resize
import torch


def read_nifti(path):
    img = nib.load(path)
    arr = img.get_fdata()
    return arr, img.affine


def read_dicom_folder(path):
    # If a single file is DICOM, read it. If folder, user should zip/extract first.
    dcm = pydicom.dcmread(path)
    arr = dcm.pixel_array
    return arr, None


def read_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Not an image readable by OpenCV")
    return img.astype(np.float32), None


def preprocess_scan(path, scanner_type="MRI", meta=None):
    """
    Returns: torch tensor ready for model (C x D x H x W) or C x H x W for 2D models
    and info dict with original shapes, etc.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in [".nii", ".nii.gz", ".mgh"]:
        arr, affine = read_nifti(path)
    elif ext in [".dcm"]:
        arr, affine = read_dicom_folder(path)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        arr, affine = read_image(path)
    else:
        # attempt to read as nifti first
        try:
            arr, affine = read_nifti(path)
        except Exception as e:
            raise ValueError("Unknown file type")

    # Basic pipeline per scanner (toy example)
    if scanner_type.upper() in ["MRI", "FMRI"]:
        # MRI: typically 3D. Normalize, resample to 1mm^3 and center-crop/pad to 160^3
        arr = np.nan_to_num(arr)
        if arr.ndim == 2:
            arr = arr[np.newaxis, ...]
        # intensity norm
        arr = (arr - np.mean(arr)) / (np.std(arr)+1e-8)
        target_shape = (160, 160, 160)
        # quick resize to target (slow for large data — replace with proper resampling)
        # compute resize for 3D
        if arr.ndim == 3:
            arr = resize(arr, target_shape, preserve_range=True,
                         anti_aliasing=True)
        else:
            arr = resize(arr[0], target_shape,
                         preserve_range=True, anti_aliasing=True)
        tensor = torch.from_numpy(arr).float().unsqueeze(0)  # 1 x D x H x W
    elif scanner_type.upper() == "PET":
        # PET often 3D; emphasize SUV normalization or z-score
        arr = (arr - np.mean(arr)) / (np.std(arr)+1e-8)
        arr = resize(arr, (128, 128, 128), preserve_range=True)
        tensor = torch.from_numpy(arr).float().unsqueeze(0)
    elif scanner_type.upper() == "CT":
        # CT: windowing may be applied
        arr = np.clip(arr, -1000, 1000)
        arr = (arr - np.mean(arr)) / (np.std(arr)+1e-8)
        arr = resize(arr, (128, 128, 128), preserve_range=True)
        tensor = torch.from_numpy(arr).float().unsqueeze(0)
    else:
        # fallback: return 2D scaled image
        arr = cv2.resize(arr.astype(np.float32), (224, 224))
        arr = (arr - arr.mean()) / (arr.std()+1e-8)
        tensor = torch.from_numpy(arr).unsqueeze(
            0).unsqueeze(0).float()  # 1 x 1 x H x W

    info = {"orig_shape": arr.shape, "scanner_type": scanner_type}
    return tensor, info
