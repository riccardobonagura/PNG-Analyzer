import numpy as np

def subsample_422(ycbcr: np.ndarray) -> np.ndarray:
    """
    Applica subsampling 4:2:2 ai canali cromatici (Cb e Cr).
    Per ogni coppia orizzontale di pixel, mantiene uno solo dei valori.
    """
    Y = ycbcr[:, :, 0]
    Cb = ycbcr[:, :, 1]
    Cr = ycbcr[:, :, 2]

    height, width = Y.shape
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

    return np.clip(np.stack([Y, subsampled_Cb, subsampled_Cr], axis=2), 0, 255)

def subsample_420(ycbcr: np.ndarray) -> np.ndarray:
    """
    Applica subsampling 4:2:0 ai canali cromatici (Cb e Cr).
    Per ogni blocco 2x2, mantiene solo il valore in alto a sinistra.
    """
    Y = ycbcr[:, :, 0]
    Cb = ycbcr[:, :, 1]
    Cr = ycbcr[:, :, 2]

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

def extract_center_matrix(ycbcr: np.ndarray, size=10) -> np.ndarray:
    """
    Estrae una matrice size×size dal centro dell'immagine YCbCr.
    Ogni elemento è un vettore [Y, Cb, Cr].
    """
    h, w, _ = ycbcr.shape
    start_y = h // 2 - size // 2
    start_x = w // 2 - size // 2
    return ycbcr[start_y:start_y+size, start_x:start_x+size, :]

def compute_chroma_memory_usage(ycbcr: np.ndarray, mode: str) -> int:
    """
    Calcola lo spazio occupato dai canali Cb e Cr (in byte) in base alla modalità di subsampling.
    Assumiamo 1 byte per componente per pixel.
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

def convert_ycbcr_to_rgb(image_ycbcr: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine YCbCr (float64) in RGB (uint8), usando la formula BT.601.
    Implementata manualmente a basso livello.
    """
    T_inv = np.array([
        [1.0, 0.0, 1.402],
        [1.0, -0.344136, -0.714136],
        [1.0, 1.772, 0.0]
    ])

    offset = np.array([0, 128, 128])

    shape = image_ycbcr.shape
    flat_ycbcr = image_ycbcr.reshape(-1, 3)
    flat_rgb = np.dot(flat_ycbcr - offset, T_inv.T)
    flat_rgb = np.clip(flat_rgb, 0, 255).astype(np.uint8)
    return flat_rgb.reshape(shape)