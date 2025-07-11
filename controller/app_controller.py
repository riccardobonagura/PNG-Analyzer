# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI DEL CONTROLLER (AppController)
#
# Costruttore:
#   AppController()
#       # Inizializza il controller e il modello associato.
#
# --- Sezione: Caricamento, reset e aggiornamento immagine ---
#   load_image(filepath: str) -> bool
#       # Carica l'immagine dal percorso file. Restituisce True se riuscito, False altrimenti.
#   reset_image()
#       # Ripristina l'immagine corrente allo stato originale.
#   update_image(new_image: np.ndarray)
#       # Aggiorna l'immagine corrente con una nuova versione modificata.
#
# --- Sezione: Query informazioni immagine ---
#   get_current_image() -> np.ndarray
#       # Restituisce l'immagine corrente come array NumPy.
#   get_original_image() -> np.ndarray
#       # Restituisce l'immagine originale come array NumPy.
#   get_image_resolution()
#       # Restituisce la risoluzione dell'immagine corrente (larghezza, altezza).
#   get_image_channels()
#       # Restituisce il numero di canali dell'immagine corrente.
#   get_color_space()
#       # Restituisce lo spazio colore associato all'immagine corrente.
#   is_image_loaded() -> bool
#       # Verifica se un'immagine è stata caricata.
#   get_filepath() -> str
#       # Restituisce il percorso del file caricato.
#
# --- Sezione: Query canali spazio colore ---
#   get_ycbcr_channels()
#       # Restituisce i canali Y, Cb, Cr come tuple di array numpy oppure None.
#   get_hsv_channels()
#       # Restituisce i canali H, S, V come tuple di array numpy oppure None.
#   get_rgb_channels()
#       # Restituisce i canali R, G, B come tuple di array numpy oppure None.
#
# --- Sezione: Conversioni colore ---
#   bgr_to_rgb(image: np.ndarray) -> np.ndarray
#       # Converte un'immagine da BGR a RGB.
#   rgb_to_bgr(image: np.ndarray) -> np.ndarray
#       # Converte un'immagine da RGB a BGR.
#
# --- Sezione: Generazione figure matplotlib ---
#   get_rgb_histogram_figure(screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#       # Genera una figura con 4 istogrammi RGB (R, G, B, composito).
#   get_rgb_figure(screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#       # Genera una figura con immagine RGB originale e canali separati equalizzati/stretched.
#   get_ycbcr_figure(screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#       # Genera una figura con immagine RGB e canali Y, Cb, Cr impilati.
#   get_hsv_figure(screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#       # Genera una figura con immagine RGB e canali H, S, V impilati.
#
# --- Sezione: Viste avanzate/model delegate ---
#   get_ycbcr_subsampling_figure(screen_width: int, screen_height: int)
#       # Restituisce la figura di confronto YCbCr subsampling dal model.
#   get_hsv_scatter_comparison_figure(screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#       # Restituisce la figura 2x2 HSV scatter/confronto tramite il model.
#
# --- Sezione: Conversione PNG -> JPEG ---
#   convert_image_to_jpeg(rgb_image: np.ndarray, compression_level: str = "med") -> bytes
#       # Converte un’immagine RGB in JPEG con livello di compressione selezionato.
# ========================================================

# ========================================================
# 1. IMPORT DELLE LIBRERIE NECESSARIE
import cv2
import numpy as np

from model import texture_tools
from model.image_model import ImageModel
from model.color_tools import (
    convert_rgb_to_ycbcr,
    convert_rgb_to_hsv_manual,
    split_ycbcr_channels,
    split_hsv_channels,
    split_rgb_channels,
    compute_rgb_histograms
)
from matplotlib.figure import Figure
from model.jpeg_pipeline import jpeg_encode_image


# ========================================================

# ========================================================
# 2. DEFINIZIONE DELLA CLASSE AppController
class AppController:
    """
    Controller dell'applicazione.
    Gestisce la logica di coordinamento tra View (GUI) e Model (ImageModel).
    La View non deve mai accedere direttamente al Model.
    """

    # ----------------------------------------------------
    # 2.1. Costruttore
    def __init__(self):
        # Inizializza l'istanza del modello dell'immagine.
        self.model = ImageModel()

    # ----------------------------------------------------
    # 2.2. Caricamento, reset e aggiornamento dell'immagine

    def load_image(self, filepath: str) -> bool:
        """
        Carica l'immagine dal percorso specificato.
        Args:
            filepath (str): percorso del file immagine.
        Returns:
            bool: True se caricamento riuscito, False altrimenti.
        """
        try:
            self.model.load_image_from_file(filepath)
            return True
        except Exception as e:
            print(f"[Errore] {e}")
            return False

    def reset_image(self):
        """
        Ripristina l'immagine corrente allo stato originale.
        """
        self.model.reset_to_original()

    def update_image(self, new_image: np.ndarray):
        """
        Aggiorna l'immagine corrente con una nuova versione modificata.
        Args:
            new_image (np.ndarray): nuova immagine da impostare.
        """
        self.model.set_current_image(new_image)

    # ----------------------------------------------------
    # 2.3. Query delle informazioni sull'immagine

    def get_current_image(self) -> np.ndarray:
        """
        Restituisce l'immagine corrente come array NumPy.
        Returns:
            np.ndarray: immagine corrente.
        """
        return self.model.get_current_image()

    def get_original_image(self) -> np.ndarray:
        """
        Restituisce l'immagine originale come array NumPy.
        Returns:
            np.ndarray: immagine originale.
        """
        return self.model.get_original_image()

    def get_image_resolution(self):
        """
        Restituisce la risoluzione dell'immagine corrente (larghezza, altezza).
        Returns:
            tuple: (width, height)
        """
        return self.model.get_resolution()

    def get_image_channels(self):
        """
        Restituisce il numero di canali dell'immagine corrente.
        Returns:
            int: numero di canali.
        """
        return self.model.get_num_channels()

    def get_color_space(self):
        """
        Restituisce lo spazio colore associato all'immagine corrente.
        Returns:
            str: spazio colore (es. "sRGB").
        """
        return self.model.get_color_space()

    def is_image_loaded(self) -> bool:
        """
        Verifica se un'immagine è stata caricata.
        Returns:
            bool: True se caricata, False altrimenti.
        """
        return self.model.is_image_loaded()

    def get_filepath(self) -> str:
        """
        Restituisce il percorso del file caricato.
        Returns:
            str: percorso del file.
        """
        return self.model.get_filepath()

    # ----------------------------------------------------
    # 2.4. Query dei canali spazio colore

    def get_ycbcr_channels(self):
        """
        Restituisce i canali Y, Cb, Cr come array numpy.
        Returns:
            tuple: (Y, Cb, Cr) oppure None se nessuna immagine caricata.
        """
        image = self.get_current_image()
        if image is None:
            return None
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ycbcr_image = convert_rgb_to_ycbcr(rgb_image)
        return split_ycbcr_channels(ycbcr_image)

    def get_hsv_channels(self):
        """
        Restituisce i canali H, S, V come array numpy.
        Returns:
            tuple: (H, S, V) oppure None se nessuna immagine caricata.
        """
        image = self.get_current_image()
        if image is None:
            return None
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv_image = convert_rgb_to_hsv_manual(rgb_image)
        return split_hsv_channels(hsv_image)

    def get_rgb_channels(self):
        """
        Restituisce i canali R, G, B come array numpy.
        Returns:
            tuple: (R, G, B) oppure None se nessuna immagine caricata.
        """
        image = self.get_current_image()
        if image is None:
            return None
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return split_rgb_channels(rgb_image)

# ========================================================

# ========================================================
    # 3. GENERAZIONE DELLE FIGURE MATPLOTLIB
    def bgr_to_rgb(self, image: np.ndarray) -> np.ndarray:
            """
            Converte un'immagine da BGR a RGB utilizzando cv2.
            Args:
                image (np.ndarray): immagine in formato BGR.
            Returns:
                np.ndarray: immagine convertita in formato RGB.
            """
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def rgb_to_bgr(self, image: np.ndarray) -> np.ndarray:
            """
            Converte un'immagine da RGB a BGR utilizzando cv2.
            Args:
                image (np.ndarray): immagine in formato RGB.
            Returns:
                np.ndarray: immagine convertita in formato BGR.
            """
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    def get_rgb_histogram_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
            """
            Genera una figura matplotlib che mostra 4 istogrammi:
            R, G, B e composito RGB con curve sovrapposte.
            Args:
                screen_width (int): larghezza dello schermo in pixel.
                screen_height (int): altezza dello schermo in pixel.
                dpi (int): densità di punti per pollice della figura.
            Returns:
                Figure: oggetto figura matplotlib.
            Raises:
                RuntimeError: se nessuna immagine è caricata.
            """
            image = self.get_current_image()
            if image is None:
                raise RuntimeError("Nessuna immagine caricata.")
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            hist_r, hist_g, hist_b, bins = compute_rgb_histograms(rgb_image)
            margin_factor = 0.85
            fig_width = int((screen_width * margin_factor) / dpi)
            fig_height = int((screen_height * margin_factor) / dpi)
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
            axs[3].set_title("Istogramma composito RGB")
            axs[3].legend()
            for ax in axs:
                ax.set_xlim([0, 255])
                ax.set_xlabel("Valore di Intensità")
                ax.set_ylabel("Frequenza")
                ax.grid(True)
            fig.tight_layout()
            return fig

    def get_rgb_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
            """
            Genera e restituisce una figura matplotlib che mostra l'immagine RGB e i suoi tre canali separati equalizzati e stretching manuale.
            Args:
                screen_width (int): larghezza dello schermo in pixel.
                screen_height (int): altezza dello schermo in pixel.
                dpi (int): densità di punti per pollice della figura.
            Returns:
                Figure: oggetto figura matplotlib.
            Raises:
                RuntimeError: se nessuna immagine è caricata.
            """
            image = self.get_current_image()
            if image is None:
                raise RuntimeError("Nessuna immagine caricata.")
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            R, G, B = split_rgb_channels(rgb_image)

            # Equalizzazione manuale dell'istogramma per ciascun canale
            def manual_eq(channel: np.ndarray) -> np.ndarray:
                hist = np.bincount(channel.flatten(), minlength=256)
                cdf = hist.cumsum()
                cdf_masked = np.ma.masked_equal(cdf, 0)
                cdf_min = cdf_masked.min()
                cdf_max = cdf_masked.max()
                eq = ((cdf_masked - cdf_min) * 255 / (cdf_max - cdf_min)).filled(0).astype(np.uint8)
                return eq[channel]

            # Stretching manuale dell'istogramma per ciascun canale
            def stretch(channel: np.ndarray) -> np.ndarray:
                c_min, c_max = np.min(channel), np.max(channel)
                if c_max - c_min == 0:
                    return np.zeros_like(channel)
                stretched = (channel - c_min) * 255.0 / (c_max - c_min)
                return stretched.astype(np.uint8)

            R_eq = manual_eq(R)
            G_eq = manual_eq(G)
            B_eq = manual_eq(B)
            R_stretched = stretch(R_eq)
            G_stretched = stretch(G_eq)
            B_stretched = stretch(B_eq)
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
            axs[0].imshow(rgb_image)
            axs[0].set_title("Immagine RGB originale")
            axs[0].axis("off")
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

# ========================================================

# ========================================================
# 4. GENERAZIONE DI FIGURE PER SPAZI COLORE E VISTE AVANZATE

    def get_ycbcr_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        """
        Genera e restituisce una figura matplotlib che mostra:
        - Immagine RGB originale (a sinistra)
        - Canali Y, Cb, Cr impilati verticalmente (a destra)
        Args:
            screen_width (int): larghezza dello schermo in pixel.
            screen_height (int): altezza dello schermo in pixel.
            dpi (int): densità di punti per pollice della figura.
        Returns:
            Figure: oggetto figura matplotlib.
        Raises:
            RuntimeError: se nessuna immagine è caricata.
        """
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        Y, Cb, Cr = self.get_ycbcr_channels()
        fig_width = int((screen_width * 0.85) / dpi)
        fig_height = int((screen_height * 0.85) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax_rgb = fig.add_subplot(1, 2, 1)
        ax_y = fig.add_subplot(3, 2, 2)
        ax_cb = fig.add_subplot(3, 2, 4)
        ax_cr = fig.add_subplot(3, 2, 6)
        ax_rgb.imshow(rgb_image)
        ax_rgb.set_title("Immagine RGB originale")
        ax_rgb.axis("off")
        ax_y.imshow(Y, cmap='gray')
        ax_y.set_title("Y (Luminanza)")
        ax_y.axis("off")
        ax_cb.imshow(Cb, cmap='gray')
        ax_cb.set_title("Cb (Blu-diff)")
        ax_cb.axis("off")
        ax_cr.imshow(Cr, cmap='gray')
        ax_cr.set_title("Cr (Rosso-diff)")
        ax_cr.axis("off")
        fig.tight_layout()
        return fig

    def get_hsv_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        """
        Genera una figura matplotlib per visualizzare RGB e i 3 canali HSV.
        Layout:
        - RGB a sinistra
        - H/S/V verticali a destra
        Args:
            screen_width (int): larghezza dello schermo in pixel.
            screen_height (int): altezza dello schermo in pixel.
            dpi (int): densità di punti per pollice della figura.
        Returns:
            Figure: oggetto figura matplotlib.
        Raises:
            RuntimeError: se nessuna immagine è caricata.
        """
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        H, S, V = self.get_hsv_channels()
        fig_width = int((screen_width * 0.85) / dpi)
        fig_height = int((screen_height * 0.85) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        axs = [
            fig.add_subplot(1, 2, 1),  # Immagine RGB originale
            fig.add_subplot(3, 2, 2),  # H
            fig.add_subplot(3, 2, 4),  # S
            fig.add_subplot(3, 2, 6),  # V
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

    # ----------------------------------------------------
    # 4.1. Viste avanzate e funzioni custom

    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int):
        """
        Restituisce la figura di confronto YCbCr subsampling dal model.
        Args:
            screen_width (int): larghezza dello schermo in pixel.
            screen_height (int): altezza dello schermo in pixel.
        Returns:
            Figure: oggetto figura matplotlib.
        """
        return self.model.get_ycbcr_subsampling_figure(screen_width, screen_height)

    def get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        """
        Restituisce la figura 2x2 HSV scatter/confronto tramite il model.
        Args:
            screen_width (int): larghezza della figura in pixel.
            screen_height (int): altezza della figura in pixel.
            dpi (int): risoluzione DPI della figura matplotlib.
        Returns:
            Figure: oggetto matplotlib Figure.
        """
        return self.model.get_hsv_scatter_comparison_figure(
            screen_width=screen_width,
            screen_height=screen_height,
            dpi=dpi
        )

    # ----------------------------------------------------
    # 4.2. Conversione immagine PNG -> JPEG

    def convert_image_to_jpeg(self, rgb_image: np.ndarray, compression_level: str = "med") -> bytes:
        """
        Orchestrates the JPEG conversion pipeline.
        Args:
            rgb_image (np.ndarray): immagine RGB, shape (H, W, 3), dtype uint8.
            compression_level (str): livello di compressione ("low", "med", "high").
        Returns:
            bytes: JPEG encoded image.
        """
        from model.jpeg_tools import get_quant_tables
        luma_tbl, chroma_tbl = get_quant_tables(compression_level)
        jpeg_bytes = jpeg_encode_image(rgb_image, luma_quant_table=luma_tbl, chroma_quant_table=chroma_tbl)
        return jpeg_bytes
# ========================================================


# 5 Texture

    def process_image_directionality(self, rgb_image: np.ndarray) -> tuple [float, Figure]:
        """
        Calcola la direzionalità Tamura, l'istogramma delle orientazioni e una figura del suo istogramma polare.

        Args:
            rgb_image (np.ndarray): Immagine (grayscale o RGB, array numpy).

        Returns:
            directionality (float): Valore scalare della direzionalità.
            hist (np.ndarray): Istogramma delle orientazioni.
            fig (Figure): Figura matplotlib dell'istogramma polare.
        """
        directionality, hist = texture_tools.compute_directionality_grid(rgb_image)

        # Costruisci la figura dell'istogramma polare
        bin_width_deg = 10
        bin_width_rad = np.deg2rad(bin_width_deg)
        bins = len(hist)
        theta = np.linspace(0, np.pi, bins, endpoint=False) + bin_width_rad / 2  # centro del bin

        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111, polar=True)
        bars = ax.bar(theta, hist, width=bin_width_rad, color='C0', alpha=0.7, align='center', edgecolor='black')

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_xticks(np.deg2rad(np.arange(0, 181, 30)))
        ax.set_title("Tamura Directionality Histogram (Polar)", va='bottom')
        ax.grid(True)

        return directionality, fig