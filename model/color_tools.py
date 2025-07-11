# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# convert_rgb_to_ycbcr(rgb_image: np.ndarray) -> np.ndarray
#     # Converte un’immagine RGB uint8 in YCbCr uint8 con shape (H, W, 3)
#
# split_ycbcr_channels(ycbcr_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
#     # Restituisce i canali Y, Cb, Cr come array 2D
#
# convert_rgb_to_hsv_manual(rgb_image: np.ndarray) -> np.ndarray
#     # Converte un’immagine RGB in HSV manualmente, restituisce HSV uint8
#
# split_hsv_channels(hsv_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
#     # Restituisce i canali H, S, V come array 2D
#
# split_rgb_channels(rgb_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
#     # Restituisce i canali R, G, B come array 2D
#
# compute_rgb_histograms(rgb_image: np.ndarray, num_bins: int = 256) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
#     # Calcola gli istogrammi dei tre canali R, G, B, restituisce hist_r, hist_g, hist_b, bins
#
# gray_world_white_balance(img_rgb: np.ndarray) -> np.ndarray
#     # Applica il bilanciamento del bianco "gray world" su un’immagine RGB
# ========================================================


# ========================================================
# 1. IMPORT NECESSARI
import numpy as np
# ========================================================

# ========================================================
# 2. CONVERSIONE DA RGB A YCbCr
def convert_rgb_to_ycbcr(rgb_image: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine RGB (uint8) in YCbCr (standard BT.601) usando operazioni matriciali.
    Restituisce un'immagine YCbCr in uint8 con shape (H, W, 3).
    """
    if rgb_image.dtype != np.uint8:
        raise ValueError("L'immagine deve essere in formato uint8")
    R = rgb_image[:, :, 0].astype(np.float32)
    G = rgb_image[:, :, 1].astype(np.float32)
    B = rgb_image[:, :, 2].astype(np.float32)
    Y  =  0.299    * R + 0.587    * G + 0.114    * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5      * B + 128
    Cr =  0.5      * R - 0.418688 * G - 0.081312 * B + 128
    ycbcr = np.stack((Y, Cb, Cr), axis=-1)
    ycbcr = np.clip(ycbcr, 0, 255).astype(np.uint8)
    return ycbcr
# ========================================================

# ========================================================
# 3. SEPARAZIONE CANALI YCbCr
def split_ycbcr_channels(ycbcr_image: np.ndarray):
    """
    Restituisce i canali Y, Cb, Cr come array 2D.
    """
    if ycbcr_image.dtype != np.uint8 or ycbcr_image.shape[2] != 3:
        raise ValueError("Immagine YCbCr non valida.")
    Y  = ycbcr_image[:, :, 0]
    Cb = ycbcr_image[:, :, 1]
    Cr = ycbcr_image[:, :, 2]
    return Y, Cb, Cr
# ========================================================

# ========================================================
# 4. CONVERSIONE DA RGB A HSV (calcolo manuale)
def convert_rgb_to_hsv_manual(rgb_image: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine RGB in HSV manualmente, senza usare funzioni di libreria.
    Restituisce un'immagine HSV con H in [0, 179], S e V in [0, 255], dtype=uint8.
    """
    rgb_image = rgb_image.astype(np.float32) / 255.0
    R, G, B = rgb_image[:, :, 0], rgb_image[:, :, 1], rgb_image[:, :, 2]
    Cmax = np.max(rgb_image, axis=2)
    Cmin = np.min(rgb_image, axis=2)
    delta = Cmax - Cmin
    H = np.zeros_like(Cmax)
    mask = delta != 0
    idx = (Cmax == R) & mask
    H[idx] = (60 * ((G[idx] - B[idx]) / delta[idx]) + 360) % 360
    idx = (Cmax == G) & mask
    H[idx] = (60 * ((B[idx] - R[idx]) / delta[idx]) + 120) % 360
    idx = (Cmax == B) & mask
    H[idx] = (60 * ((R[idx] - G[idx]) / delta[idx]) + 240) % 360
    H[~mask] = 0
    S = np.zeros_like(Cmax)
    S[Cmax != 0] = delta[Cmax != 0] / Cmax[Cmax != 0]
    V = Cmax
    H = (H / 2).astype(np.uint8)          # da [0,360] → [0,180)
    S = (S * 255).astype(np.uint8)        # da [0,1] → [0,255]
    V = (V * 255).astype(np.uint8)
    hsv_image = np.stack([H, S, V], axis=-1)
    return hsv_image
# ========================================================

# ========================================================
# 5. SEPARAZIONE CANALI HSV
def split_hsv_channels(hsv_image: np.ndarray):
    """
    Restituisce i canali H, S, V come array 2D.
    """
    if hsv_image.dtype != np.uint8 or hsv_image.shape[2] != 3:
        raise ValueError("Immagine HSV non valida.")
    H = hsv_image[:, :, 0]
    S = hsv_image[:, :, 1]
    V = hsv_image[:, :, 2]
    return H, S, V
# ========================================================

# ========================================================
# 6. SEPARAZIONE CANALI RGB
def split_rgb_channels(rgb_image: np.ndarray):
    """
    Restituisce i canali R, G, B come array 2D.
    """
    if rgb_image.dtype != np.uint8 or rgb_image.shape[2] != 3:
        raise ValueError("Immagine RGB non valida.")
    R = rgb_image[:, :, 0]
    G = rgb_image[:, :, 1]
    B = rgb_image[:, :, 2]
    return R, G, B
# ========================================================

# ========================================================
# 7. ISTOGRAMMI RGB MANUALI
def compute_rgb_histograms(rgb_image: np.ndarray, num_bins: int = 256):
    """
    Calcola gli istogrammi dei tre canali R, G, B.
    Ritorna:
    - hist_r, hist_g, hist_b: array (256,) con le occorrenze per ogni valore [0-255]
    - bins: array con i valori dei bin centrati
    """
    height, width, _ = rgb_image.shape
    hist_r = np.zeros(num_bins, dtype=np.int32)
    hist_g = np.zeros(num_bins, dtype=np.int32)
    hist_b = np.zeros(num_bins, dtype=np.int32)
    R = rgb_image[:, :, 0].flatten()
    G = rgb_image[:, :, 1].flatten()
    B = rgb_image[:, :, 2].flatten()
    for val in R:
        hist_r[val] += 1
    for val in G:
        hist_g[val] += 1
    for val in B:
        hist_b[val] += 1
    bins = np.arange(num_bins)
    return hist_r, hist_g, hist_b, bins
# ========================================================

# ========================================================
# 8. BILANCIAMENTO DEL BIANCO (GRAY WORLD)
def gray_world_white_balance(img_rgb: np.ndarray) -> np.ndarray:
    """
    Applica il bilanciamento del bianco "gray world" su un'immagine RGB.
    img_rgb: array numpy H x W x 3, dtype uint8 (valori 0-255)
    Restituisce una nuova immagine RGB bilanciata, dtype uint8.
    """
    img = img_rgb.astype(np.float32)
    # Calcola la media di ciascun canale
    mean_r = np.mean(img[:, :, 0])
    mean_g = np.mean(img[:, :, 1])
    mean_b = np.mean(img[:, :, 2])
    mean_gray = (mean_r + mean_g + mean_b) / 3.0

    # Calcola i fattori di correzione
    scale_r = mean_gray / mean_r if mean_r > 0 else 1.0
    scale_g = mean_gray / mean_g if mean_g > 0 else 1.0
    scale_b = mean_gray / mean_b if mean_b > 0 else 1.0

    # Applica la correzione
    img_balanced = np.zeros_like(img)
    img_balanced[:, :, 0] = img[:, :, 0] * scale_r
    img_balanced[:, :, 1] = img[:, :, 1] * scale_g
    img_balanced[:, :, 2] = img[:, :, 2] * scale_b

    # Clippa e converte in uint8
    img_balanced = np.clip(img_balanced, 0, 255).astype(np.uint8)
    return img_balanced
# ========================================================