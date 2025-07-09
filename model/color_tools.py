import numpy as np

def convert_rgb_to_ycbcr(rgb_image: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine RGB (uint8) in YCbCr (standard BT.601) usando operazioni matriciali.
    Restituisce un'immagine YCbCr in uint8 con shape (H, W, 3).
    """

    if rgb_image.dtype != np.uint8:
        raise ValueError("L'immagine deve essere in formato uint8")

    # Assicuriamoci che sia RGB, non BGR (controllato nel model)
    R = rgb_image[:, :, 0].astype(np.float32)
    G = rgb_image[:, :, 1].astype(np.float32)
    B = rgb_image[:, :, 2].astype(np.float32)

    # Calcolo canali
    Y  =  0.299    * R + 0.587    * G + 0.114    * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5      * B + 128
    Cr =  0.5      * R - 0.418688 * G - 0.081312 * B + 128

    # Stack e clip
    ycbcr = np.stack((Y, Cb, Cr), axis=-1)
    ycbcr = np.clip(ycbcr, 0, 255).astype(np.uint8)

    return ycbcr
