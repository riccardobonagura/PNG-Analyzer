import numpy as np
from model import color_tools


def compute_directionality_grid(
    img: np.ndarray,
) -> tuple[float, np.ndarray]:
    """
    Calcola la direzionalità di Tamura per una immagine (array numpy).
    Se l'immagine è RGB, utilizza la componente Y di YCbCr come intensità luminosa.

    Args:
        img (np.ndarray): Immagine, array 2D (grayscale) o 3D (RGB).
        bin_width_deg (int): Ampiezza di ciascun bin dell'istogramma, in gradi (default: 10).
        grid_step (int): Passo della griglia per il campionamento dei pixel (default: 4).

    Returns:
        directionality (float): Valore scalare della direzionalità.
        hist (np.ndarray): Istogramma delle orientazioni.
    """
    bin_width_deg: int = 10
    grid_step: int = 8

    # RGB -> YCbCr, usa la componente Y come grigia
    ycbcr_img = color_tools.convert_rgb_to_ycbcr(img)
    img_gray = ycbcr_img[..., 0]


    # Campionamento griglia
    img_sampled = img_gray[::grid_step, ::grid_step]
    h, w = img_sampled.shape

    # Kernel Sobel
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    Ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=float)

    gx = np.zeros((h, w), dtype=float)
    gy = np.zeros((h, w), dtype=float)
    for i in range(1, h-1):
        for j in range(1, w-1):
            region = img_sampled[i-1:i+2, j-1:j+2]
            gx[i, j] = np.sum(region * Kx)
            gy[i, j] = np.sum(region * Ky)

    # Orientazioni in [0, π]
    orientations = np.arctan2(gy, gx)
    orientations = np.abs(orientations)

    # Bin regolari su [0, π]
    bin_width_rad = np.deg2rad(bin_width_deg)
    bin_edges = np.arange(0, np.pi + bin_width_rad, bin_width_rad)
    bins = len(bin_edges) - 1

    hist, _ = np.histogram(orientations[1:-1, 1:-1].flatten(), bins=bin_edges)

    # Direzionalità scalare
    peak = np.max(hist)
    mean_other = (np.sum(hist) - peak) / (bins - 1)
    directionality = peak / (mean_other + 1e-7)

    return directionality, hist