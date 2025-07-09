import numpy as np
from matplotlib.figure import Figure


def convert_rgb_to_ycbcr(rgb_image: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine RGB (uint8) in YCbCr (standard BT.601) usando operazioni matriciali.
    Restituisce un'immagine YCbCr in uint8 con shape (H, W, 3).
    """
    if rgb_image.dtype != np.uint8:
        raise ValueError("L'immagine deve essere in formato uint8")

    # Assicuriamoci che sia RGB, non BGR
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


def create_ycbcr_figure(ycbcr_image: np.ndarray) -> Figure:
    """
    Crea e restituisce un oggetto Figure contenente i 3 canali Y, Cb e Cr come immagini in scala di grigio.
    Può essere integrato direttamente nella GUI Tkinter tramite FigureCanvasTkAgg.
    """
    if ycbcr_image.dtype != np.uint8 or ycbcr_image.shape[2] != 3:
        raise ValueError("Immagine YCbCr non valida.")

    Y  = ycbcr_image[:, :, 0]
    Cb = ycbcr_image[:, :, 1]
    Cr = ycbcr_image[:, :, 2]

    fig = Figure(figsize=(8, 3))
    axs = fig.subplots(1, 3)

    axs[0].imshow(Y, cmap='gray')
    axs[0].set_title("Y (Luminanza)")
    axs[1].imshow(Cb, cmap='gray')
    axs[1].set_title("Cb (Blu-diff)")
    axs[2].imshow(Cr, cmap='gray')
    axs[2].set_title("Cr (Rosso-diff)")

    for ax in axs:
        ax.axis("off")

    fig.tight_layout()
    return fig

import numpy as np
from matplotlib.figure import Figure

def convert_rgb_to_hsv_manual(rgb_image: np.ndarray) -> np.ndarray:
    """
    Converte un'immagine RGB in HSV manualmente, senza usare funzioni di libreria.
    Restituisce un'immagine HSV con H in [0, 179], S e V in [0, 255], dtype=uint8.
    """
    # Normalizza in [0,1]
    rgb_image = rgb_image.astype(np.float32) / 255.0
    R, G, B = rgb_image[:, :, 0], rgb_image[:, :, 1], rgb_image[:, :, 2]

    Cmax = np.max(rgb_image, axis=2)
    Cmin = np.min(rgb_image, axis=2)
    delta = Cmax - Cmin

    H = np.zeros_like(Cmax)

    # Calcolo di H (Hue) in gradi
    mask = delta != 0

    # Dove il massimo è R
    idx = (Cmax == R) & mask
    H[idx] = (60 * ((G[idx] - B[idx]) / delta[idx]) + 360) % 360

    # Dove il massimo è G
    idx = (Cmax == G) & mask
    H[idx] = (60 * ((B[idx] - R[idx]) / delta[idx]) + 120) % 360

    # Dove il massimo è B
    idx = (Cmax == B) & mask
    H[idx] = (60 * ((R[idx] - G[idx]) / delta[idx]) + 240) % 360

    H[~mask] = 0  # Se delta == 0, H è indefinito → lo fissiamo a 0

    # Calcolo di S (Saturazione)
    S = np.zeros_like(Cmax)
    S[Cmax != 0] = delta[Cmax != 0] / Cmax[Cmax != 0]

    # Calcolo di V (Valore)
    V = Cmax

    # Scaling per imitare output OpenCV
    H = (H / 2).astype(np.uint8)          # da [0,360] → [0,180)
    S = (S * 255).astype(np.uint8)        # da [0,1] → [0,255]
    V = (V * 255).astype(np.uint8)

    hsv_image = np.stack([H, S, V], axis=-1)
    return hsv_image



def create_hsv_figure(rgb_image: np.ndarray, hsv_image: np.ndarray, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
    """
    Crea una figura matplotlib per visualizzare RGB e i 3 canali HSV.
    Layout coerente: RGB a sinistra, H/S/V verticali a destra.
    """
    from matplotlib.figure import Figure

    H = hsv_image[:, :, 0]
    S = hsv_image[:, :, 1]
    V = hsv_image[:, :, 2]

    fig_width = int((screen_width * 0.85) / dpi)
    fig_height = int((screen_height * 0.85) / dpi)

    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    axs = [
        fig.add_subplot(1, 2, 1),        # Immagine RGB originale
        fig.add_subplot(3, 2, 2),        # H
        fig.add_subplot(3, 2, 4),        # S
        fig.add_subplot(3, 2, 6),        # V
    ]

    axs[0].imshow(rgb_image)
    axs[0].set_title("Immagine RGB originale")
    axs[0].axis("off")

    axs[1].imshow(H, cmap='hsv')
    axs[1].set_title("H (Tonalità)")

    axs[2].imshow(S, cmap='gray')
    axs[2].set_title("S (Saturazione)")

    axs[3].imshow(V, cmap='gray')
    axs[3].set_title("V (Luminosità)")

    for ax in axs[1:]:
        ax.axis("off")

    fig.tight_layout()
    return fig


from matplotlib.figure import Figure
import numpy as np
import cv2

def create_rgb_figure(rgb_image: np.ndarray, screen_width: int, screen_height: int, dpi=100) -> Figure:
    """
    Crea una figura matplotlib che visualizza l'immagine RGB e i suoi tre canali separati.
    Ogni canale è migliorato con equalizzazione, stretching lineare e colormap pseudocolore.
    """
    # Estrai canali
    R_raw = rgb_image[:, :, 0]
    G_raw = rgb_image[:, :, 1]
    B_raw = rgb_image[:, :, 2]

    # Converti in uint8 se necessario
    if R_raw.dtype != np.uint8:
        R_raw = np.clip(R_raw, 0, 255).astype(np.uint8)
        G_raw = np.clip(G_raw, 0, 255).astype(np.uint8)
        B_raw = np.clip(B_raw, 0, 255).astype(np.uint8)

    # 1. Equalizzazione istogramma (più contrasto locale)
    R_eq = cv2.equalizeHist(R_raw)
    G_eq = cv2.equalizeHist(G_raw)
    B_eq = cv2.equalizeHist(B_raw)

    # 2. Stretching lineare su ciascun canale (espansione dinamica)
    def stretch(channel):
        c_min, c_max = np.min(channel), np.max(channel)
        if c_max - c_min == 0:
            return np.zeros_like(channel)
        stretched = (channel - c_min) * 255.0 / (c_max - c_min)
        return stretched.astype(np.uint8)

    R_stretched = stretch(R_eq)
    G_stretched = stretch(G_eq)
    B_stretched = stretch(B_eq)

    # 3. Imposta dimensioni figura
    margin_factor = 0.85
    fig_width = int((screen_width * margin_factor) / dpi)
    fig_height = int((screen_height * margin_factor) / dpi)

    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    axs = [
        fig.add_subplot(1, 2, 1),  # RGB intera
        fig.add_subplot(3, 2, 2),  # R
        fig.add_subplot(3, 2, 4),  # G
        fig.add_subplot(3, 2, 6),  # B
    ]

    # Visualizzazione immagine originale RGB
    axs[0].imshow(rgb_image)
    axs[0].set_title("Immagine RGB originale")
    axs[0].axis("off")

    # 4. Visualizzazione canali con colormap pseudocolore (viridis)
    axs[1].imshow(R_stretched, cmap='viridis')
    axs[1].set_title("R (Rosso) - equalizzato")

    axs[2].imshow(G_stretched, cmap='viridis')
    axs[2].set_title("G (Verde) - equalizzato")

    axs[3].imshow(B_stretched, cmap='viridis')
    axs[3].set_title("B (Blu) - equalizzato")

    for ax in axs[1:]:
        ax.axis("off")

    fig.tight_layout()
    return fig



def compute_rgb_histograms(rgb_image: np.ndarray, num_bins: int = 256):
    """
    Calcola gli istogrammi dei tre canali R, G, B e uno composito.
    Non usa funzioni di libreria, ma opera a basso livello.

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


def create_rgb_histogram_figure(rgb_image: np.ndarray, screen_width: int, screen_height: int, separate: bool,
                                dpi=100) -> Figure:
    """
    Crea una figura matplotlib che mostra gli istogrammi RGB.

    - Se `separate=True`, visualizza 4 subplot: R, G, B e composito sovrapposto.
    - Se `separate=False`, visualizza solo il composito sovrapposto.
    """

    hist_r, hist_g, hist_b, bins = compute_rgb_histograms(rgb_image)

    # Calcolo dimensioni dinamiche
    margin_factor = 0.85
    fig_width = int((screen_width * margin_factor) / dpi)
    fig_height = int((screen_height * margin_factor) / dpi)

    if separate:
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        axs = [
            fig.add_subplot(2, 2, 1),  # R
            fig.add_subplot(2, 2, 2),  # G
            fig.add_subplot(2, 2, 3),  # B
            fig.add_subplot(2, 2, 4),  # Composito
        ]

        axs[0].bar(bins, hist_r, color='red')
        axs[0].set_title("Istogramma R (Rosso)")
        axs[1].bar(bins, hist_g, color='green')
        axs[1].set_title("Istogramma G (Verde)")
        axs[2].bar(bins, hist_b, color='blue')
        axs[2].set_title("Istogramma B (Blu)")

        axs[3].plot(bins, hist_r, color='red', label='R')
        axs[3].plot(bins, hist_g, color='green', label='G')
        axs[3].plot(bins, hist_b, color='blue', label='B')
        axs[3].set_title("Composito RGB (curve sovrapposte)")
        axs[3].legend()

        for ax in axs:
            ax.set_xlim([0, 255])
            ax.set_xlabel("Valore di Intensità")
            ax.set_ylabel("Frequenza")
            ax.grid(True)

        fig.tight_layout()

    else:
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(bins, hist_r, color='red', label='R')
        ax.plot(bins, hist_g, color='green', label='G')
        ax.plot(bins, hist_b, color='blue', label='B')
        ax.set_title("Istogramma RGB composito (curve sovrapposte)")
        ax.set_xlim([0, 255])
        ax.set_xlabel("Valore di Intensità")
        ax.set_ylabel("Frequenza")
        ax.legend()
        ax.grid(True)

    return fig
