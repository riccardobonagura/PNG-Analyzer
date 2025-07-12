# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# create_subsampling_figure(
#     image_rgb: np.ndarray,
#     image_422: np.ndarray,
#     image_420: np.ndarray,
#     mem_orig: int,
#     mem_422: int,
#     mem_420: int,
#     y4: np.ndarray, cb4: np.ndarray, cr4: np.ndarray,
#     y4_422: np.ndarray, cb4_422: np.ndarray, cr4_422: np.ndarray,
#     y4_420: np.ndarray, cb4_420: np.ndarray, cr4_420: np.ndarray
# ) -> list[dict]
#     # Restituisce una lista di 3 dizionari, ognuno con:
#     # - 'image': immagine RGB
#     # - 'title': stringa con titolo e memoria
#     # - 'resolution': dimensioni Y e Cb/Cr
#     # - 'matrix_text': rappresentazione testuale della matrice 4×4 Y/Cb/Cr
# ========================================================


# ========================================================
# 1. IMPORT NECESSARI
import numpy as np
# ========================================================


# ========================================================
# 2. CREAZIONE DATI GREZZI PER FIGURA DI SUBSAMPLING
def create_subsampling_figure(
    image_rgb: np.ndarray,
    image_422: np.ndarray,
    image_420: np.ndarray,
    mem_orig: int,
    mem_422: int,
    mem_420: int,
    y4: np.ndarray, cb4: np.ndarray, cr4: np.ndarray,
    y4_422: np.ndarray, cb4_422: np.ndarray, cr4_422: np.ndarray,
    y4_420: np.ndarray, cb4_420: np.ndarray, cr4_420: np.ndarray,
) -> list[dict]:
    """
    Restituisce una lista di 3 dizionari contenenti i dati grezzi per la costruzione
    di una figura matplotlib che confronta original vs. subsampling.

    Ogni dizionario contiene:
    - 'image': immagine RGB
    - 'title': titolo con memoria
    - 'resolution': testo con dimensioni Y e Cb/Cr
    - 'matrix_text': testo formattato con valori Y/Cb/Cr 4x4
    """
    images = [image_rgb, image_422, image_420]
    titles = [
        f"Originale RGB\nMemoria: {mem_orig:.1f} KB",
        f"Subsampling 4:2:2\nMemoria: {mem_422:.1f} KB",
        f"Subsampling 4:2:0\nMemoria: {mem_420:.1f} KB",
    ]
    matrices = [
        (y4, cb4, cr4),
        (y4_422, cb4_422, cr4_422),
        (y4_420, cb4_420, cr4_420),
    ]

    result = []

    for i in range(3):
        y, cb, cr = matrices[i]
        matrix_text = ""
        for r in range(y.shape[0]):
            row = ""
            for c in range(y.shape[1]):
                row += f"{int(y[r, c])}/{int(cb[r, c])}/{int(cr[r, c])}  "
            matrix_text += row.strip() + "\n"

        resolution_text = (
            f"Y: {y.shape[1]}×{y.shape[0]}\n"
            f"Cb/Cr: {cb.shape[1]}×{cb.shape[0]}"
        )

        result.append({
            "image": images[i],
            "title": titles[i],
            "resolution": resolution_text,
            "matrix_text": matrix_text.strip()
        })

    return result
# ========================================================
