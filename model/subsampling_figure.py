from matplotlib.figure import Figure
import numpy as np

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
    screen_width: int,
    screen_height: int,
    dpi: int = 100
) -> Figure:
    """
    Crea una figura matplotlib con:
    - Immagine originale RGB
    - Immagini con subsampling 4:2:2 e 4:2:0
    - Risoluzioni cromatiche e memoria
    - Matrici centrali 4x4 di Y, Cb, Cr
    """
    margin_factor = 0.85
    fig_width = int((screen_width * margin_factor) / dpi)
    fig_height = int((screen_height * margin_factor) / dpi)
    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)

    # Layout: 3 colonne (RGB, 422, 420), 3 righe (immagini, testo, matrici)
    axs = [[fig.add_subplot(3, 3, i + j * 3 + 1) for i in range(3)] for j in range(3)]

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

    for col in range(3):
        axs[0][col].imshow(images[col].astype(np.uint8))
        axs[0][col].set_title(titles[col], fontsize=10)
        axs[0][col].axis("off")

        # Riga testo: risoluzione Y e Cb/Cr
        y, cb, cr = matrices[col]
        axs[1][col].text(
            0.5, 0.5,
            f"Y: {y.shape[1]}×{y.shape[0]}\n"
            f"Cb/Cr: {cb.shape[1]}×{cb.shape[0]}",
            fontsize=9, ha='center', va='center'
        )
        axs[1][col].axis("off")

        # Riga matrici Y/Cb/Cr
        matrix_text = ""
        for i in range(y.shape[0]):
            row_text = ""
            for j in range(y.shape[1]):
                row_text += f"{int(y[i, j])}/{int(cb[i, j])}/{int(cr[i, j])}  "
            matrix_text += row_text.strip() + "\n"

        axs[2][col].text(
            0.5, 0.5, matrix_text,
            fontsize=8,
            family="monospace",
            va='center',
            ha='center',
            linespacing=1.4,
            transform=axs[2][col].transAxes
        )
        axs[2][col].axis("off")

    fig.tight_layout()
    return fig
