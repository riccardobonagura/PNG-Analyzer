# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# subsample_422(ycbcr: np.ndarray) -> np.ndarray
#     # Applica subsampling 4:2:2 ai canali Cb/Cr, mantiene le copie orizzontali.
#
# subsample_420(ycbcr: np.ndarray) -> np.ndarray
#     # Applica subsampling 4:2:0 ai canali Cb/Cr, mantiene le copie su blocchi 2x2.
#
# extract_center_matrix(ycbcr: np.ndarray, size: int = 10) -> np.ndarray
#     # Estrae una matrice size×size dal centro dell’immagine YCbCr.
#
# compute_chroma_memory_usage(ycbcr: np.ndarray, mode: str) -> int
#     # Calcola lo spazio occupato dai canali Cb/Cr (in byte) in base alla modalità.
#
# ========================================================



# ========================================================
# 1. IMPORT NECESSARI
import numpy as np
from model import color_tools


# ========================================================

# ========================================================
# 2. SUBSAMPLING 4:2:2 (lazy, mantiene le copie)
def subsample_422(ycbcr: np.ndarray) -> np.ndarray: #ndarray = n-dimensional array
    """
    Applica subsampling 4:2:2 ai canali cromatici (Cb e Cr).
    Per ogni coppia orizzontale di pixel, mantiene uno solo dei valori.
    Restituisce array YCbCr con stessi shape e dtype dell'input.
    """
    Y, Cb, Cr = color_tools.split_ycbcr_channels(ycbcr)

    height, width = Y.shape

    # copia con tutti zero
    subsampled_Cb = np.zeros_like(Cb)
    subsampled_Cr = np.zeros_like(Cr)

    # Subsampling orizzontale: copia solo i valori delle colonne pari
    for i in range(height):
        for j in range(0, width, 2):
            cb_val = Cb[i, j]
            cr_val = Cr[i, j]
            subsampled_Cb[i, j] = cb_val
            subsampled_Cr[i, j] = cr_val
            if j + 1 < width:
                subsampled_Cb[i, j + 1] = cb_val
                subsampled_Cr[i, j + 1] = cr_val

    #riassembla i canali
    return np.clip(np.stack([Y, subsampled_Cb, subsampled_Cr], axis=2), 0, 255)
# ========================================================

# ========================================================
# 3. SUBSAMPLING 4:2:0 (lazy, mantiene le copie)
def subsample_420(ycbcr: np.ndarray) -> np.ndarray:
    """
    Applica subsampling 4:2:0 ai canali cromatici (Cb e Cr).
    Per ogni blocco 2x2, mantiene solo il valore in alto a sinistra.
    Restituisce array YCbCr con stessi shape e dtype dell'input.
    """
    Y, Cb, Cr = color_tools.split_ycbcr_channels(ycbcr)

    height, width = Y.shape
    subsampled_Cb = np.zeros_like(Cb)
    subsampled_Cr = np.zeros_like(Cr)

    for i in range(0, height, 2):
        for j in range(0, width, 2):
            cb_val = Cb[i, j]
            cr_val = Cr[i, j]
            for di in range(2):
                for dj in range(2):
                    if i + di < height and j + dj < width:
                        subsampled_Cb[i+di, j+dj] = cb_val
                        subsampled_Cr[i+di, j+dj] = cr_val

    return np.clip(np.stack([Y, subsampled_Cb, subsampled_Cr], axis=2), 0, 255)
# ========================================================

# ========================================================
# 4. ESTRAZIONE MATRICE DAL CENTRO
def extract_center_matrix(ycbcr: np.ndarray, size: int = 10) -> np.ndarray:
    """
    Estrae una matrice size×size dal centro dell'immagine YCbCr.
    Ogni elemento è un vettore [Y, Cb, Cr], quindi un pixel.
    Questa matrice verrà usata come "dimostrazione" del sampling.
    """
    h, w, _ = ycbcr.shape
    start_y = h // 2 - size // 2
    start_x = w // 2 - size // 2
    return ycbcr[start_y:start_y+size, start_x:start_x+size, :]
# ========================================================

# ========================================================
# 5. CALCOLO OCCUPAZIONE MEMORIA CANALI CROMATICI
def compute_chroma_memory_usage(ycbcr: np.ndarray, mode: str) -> int:
    """
    Calcola lo spazio occupato dai canali Cb e Cr (in byte) in base alla modalità di subsampling.
    Assume 1 byte per componente per pixel.
    """
    height, width = ycbcr.shape[:2]
    if mode == "444":  # no subsampling
        return 2 * height * width  # Cb + Cr
    elif mode == "422":
        return 2 * height * (width // 2)
    elif mode == "420":
        return 2 * (height // 2) * (width // 2)
    else:
        raise ValueError(f"Modalità non supportata: {mode}")
# ========================================================
