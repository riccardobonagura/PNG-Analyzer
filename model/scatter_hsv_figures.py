# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# create_hsv_scatter_comparison_figure(
#     image_rgb: np.ndarray,
#     image_balanced_rgb: np.ndarray,
#     convert_rgb_to_hsv,
#     stride: int = 8,
#     screen_width: int = 1200,
#     screen_height: int = 800,
#     dpi: int = 100
# ) -> matplotlib.figure.Figure
#     # Crea una figura 2x2 di confronto tra immagine RGB e scatter HSV (originale e bilanciata gray world).
# ========================================================


# ========================================================
# 1. IMPORT NECESSARI
import numpy as np
import matplotlib.pyplot as plt

from model.color_tools import convert_rgb_to_hsv_manual
# ========================================================

# ========================================================
# 2. CREAZIONE FIGURA DI CONFRONTO SCATTER HSV
def create_hsv_scatter_comparison_figure(
    image_rgb: np.ndarray,
    image_balanced_rgb: np.ndarray,
    convert_rgb_to_hsv,
    stride: int = 8,
    screen_width: int = 1200,
    screen_height: int = 800,
    dpi: int = 100
):
    """
    Crea una figura 2x2:
    - In alto a sinistra: immagine RGB originale
    - In alto a destra: scatter plot HSV originale
    - In basso a sinistra: immagine RGB bilanciata (gray world)
    - In basso a destra: scatter plot HSV bilanciata

    Args:
        image_rgb: np.ndarray, immagine RGB originale (uint8)
        image_balanced_rgb: np.ndarray, immagine RGB bilanciata (uint8)
        convert_rgb_to_hsv: funzione che converte RGB (0-255) in HSV (0-179/255/255)
        stride: int, campionamento pixel
        screen_width: int, larghezza figura in pixel
        screen_height: int, altezza figura in pixel
        dpi: int, DPI figura
    Returns:
        matplotlib.figure.Figure
    """
    # Campionamento pixel
    h, w = image_rgb.shape[:2]
    ys = np.arange(0, h, stride)
    xs = np.arange(0, w, stride)
    X, Y = np.meshgrid(xs, ys)
    coords = np.stack([Y.flatten(), X.flatten()], axis=1)

    # Funzione per ottenere punti HSV e colori RGB
    def get_hsv_scatter_data(img_rgb: np.ndarray):
        img_hsv = convert_rgb_to_hsv_manual(img_rgb)
        hsv_pixels = img_hsv[ys][:, xs].reshape(-1, 3)
        rgb_pixels = img_rgb[ys][:, xs].reshape(-1, 3) / 255.0
        h = hsv_pixels[:, 0]
        s = hsv_pixels[:, 1]
        v = hsv_pixels[:, 2]
        return h, s, v, rgb_pixels

    h_o, s_o, v_o, c_o = get_hsv_scatter_data(image_rgb)
    h_b, s_b, v_b, c_b = get_hsv_scatter_data(image_balanced_rgb)

    # Crea figura
    fig = plt.figure(figsize=(screen_width * 0.9 / dpi, screen_height * 0.9 / dpi), dpi=dpi, constrained_layout=True)

    # Immagine RGB originale
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.imshow(image_rgb)
    ax1.set_title("Immagine originale (RGB)")
    ax1.axis('off')

    # Scatter HSV originale
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    ax2.scatter(h_o, s_o, v_o, c=c_o, s=3, alpha=0.5)
    ax2.set_title("HSV scatter originale")
    ax2.set_xlabel("Hue")
    ax2.set_ylabel("Saturation")
    ax2.set_zlabel("Value")
    ax2.set_xlim(0, 179)
    ax2.set_ylim(0, 255)
    ax2.set_zlim(0, 255)

    # Immagine RGB bilanciata
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.imshow(image_balanced_rgb)
    ax3.set_title("Immagine bilanciata (gray world)")
    ax3.axis('off')

    # Scatter HSV bilanciata
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    ax4.scatter(h_b, s_b, v_b, c=c_b, s=3, alpha=0.5)
    ax4.set_title("HSV scatter bilanciata")
    ax4.set_xlabel("Hue")
    ax4.set_ylabel("Saturation")
    ax4.set_zlabel("Value")
    ax4.set_xlim(0, 179)
    ax4.set_ylim(0, 255)
    ax4.set_zlim(0, 255)

    return fig
# ========================================================