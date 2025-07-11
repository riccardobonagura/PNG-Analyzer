import cv2
import numpy as np
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


class AppController:
    """
    Gestisce la logica di coordinamento tra View (GUI) e Model (ImageModel).
    La View non deve mai accedere direttamente al Model.
    """

    def __init__(self):
        self.model = ImageModel()

    # --- Image Loading/Resetting/Updating ---

    def load_image(self, filepath: str) -> bool:
        try:
            self.model.load_image_from_file(filepath)
            return True
        except Exception as e:
            print(f"[Errore] {e}")
            return False

    def reset_image(self):
        self.model.reset_to_original()

    def update_image(self, new_image):
        self.model.set_current_image(new_image)

    # --- Image Information Queries ---

    def get_current_image(self):
        return self.model.get_current_image()

    def get_original_image(self):
        return self.model.get_original_image()

    def get_image_resolution(self):
        return self.model.get_resolution()

    def get_image_channels(self):
        return self.model.get_num_channels()

    def get_color_space(self):
        return self.model.get_color_space()

    def is_image_loaded(self):
        return self.model.is_image_loaded()

    def get_filepath(self):
        return self.model.get_filepath()

    # --- Color Space Data: Provide All Model Data Needed by View ---

    def get_ycbcr_channels(self):
        """
        Restituisce i canali Y, Cb, Cr come array numpy.
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
        """
        image = self.get_current_image()
        if image is None:
            return None
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return split_rgb_channels(rgb_image)

    # --- Matplotlib Figure Generation ---

    def bgr_to_rgb(self, image):
        """
        Converte un'immagine BGR in RGB usando cv2.
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def rgb_to_bgr(self, image):
        """
        Converte un'immagine RGB in BGR usando cv2.
        """
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    def get_rgb_histogram_figure(self, screen_width: int, screen_height: int, dpi=100) -> Figure:
        """
        Genera una figura matplotlib che mostra 4 istogrammi:
        R, G, B e composito RGB con curve sovrapposte.
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

    def get_rgb_figure(self, screen_width: int, screen_height: int, dpi=100) -> Figure:
        """
        Genera e restituisce una figura matplotlib che mostra l'immagine RGB e i suoi tre canali separati.
        """
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        R, G, B = split_rgb_channels(rgb_image)

        # Manual histogram equalization and stretching (didactic)
        def manual_eq(channel):
            # Histogram equalization (manual)
            hist = np.bincount(channel.flatten(), minlength=256)
            cdf = hist.cumsum()
            cdf_masked = np.ma.masked_equal(cdf, 0)
            cdf_min = cdf_masked.min()
            cdf_max = cdf_masked.max()
            eq = ((cdf_masked - cdf_min) * 255 / (cdf_max - cdf_min)).filled(0).astype(np.uint8)
            return eq[channel]

        def stretch(channel):
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

    def get_ycbcr_figure(self, screen_width: int, screen_height: int, dpi=100) -> Figure:
        """
        Genera e restituisce una figura matplotlib che mostra l'immagine RGB originale a sinistra,
        e i canali Y, Cb, Cr impilati verticalmente a destra (layout come HSV).
        """
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        Y, Cb, Cr = self.get_ycbcr_channels()

        fig_width = int((screen_width * 0.85) / dpi)
        fig_height = int((screen_height * 0.85) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        # 1 row, 2 columns; right col is for Y, Cb, Cr (vertical stack)
        ax_rgb = fig.add_subplot(1, 2, 1)
        ax_y = fig.add_subplot(3, 2, 2)
        ax_cb = fig.add_subplot(3, 2, 4)
        ax_cr = fig.add_subplot(3, 2, 6)

        # Original RGB image
        ax_rgb.imshow(rgb_image)
        ax_rgb.set_title("Immagine RGB originale")
        ax_rgb.axis("off")

        # Y channel
        ax_y.imshow(Y, cmap='gray')
        ax_y.set_title("Y (Luminanza)")
        ax_y.axis("off")
        # Cb channel
        ax_cb.imshow(Cb, cmap='gray')
        ax_cb.set_title("Cb (Blu-diff)")
        ax_cb.axis("off")
        # Cr channel
        ax_cr.imshow(Cr, cmap='gray')
        ax_cr.set_title("Cr (Rosso-diff)")
        ax_cr.axis("off")

        fig.tight_layout()
        return fig

    def get_hsv_figure(self, screen_width: int, screen_height: int, dpi=100) -> Figure:
        """
        Genera una figura matplotlib per visualizzare RGB e i 3 canali HSV.
        Layout coerente: RGB a sinistra, H/S/V verticali a destra.
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

    # --- Custom/Advanced Views (e.g. Subsampling) ---

    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int):
        """
        Metodo placeholder: da implementare se necessario.
        """
        return self.model.get_ycbcr_subsampling_figure(screen_width, screen_height)

    def get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi=100) -> Figure:
        """
        Restituisce la figura 2x2 HSV scatter/confronto tramite il model.
        La view può poi visualizzare la Figure come desidera.

        Args:
            screen_width: Larghezza della figura in pixel.
            screen_height: Altezza della figura in pixel.
            dpi: Risoluzione DPI della figura matplotlib.

        Returns:
            Figure: Oggetto matplotlib Figure pronto per la visualizzazione.
        """
        return self.model.get_hsv_scatter_comparison_figure(
            screen_width=screen_width,
            screen_height=screen_height,
            dpi=dpi
        )

    # CONVERSIONE PNG -> JPEG
    def convert_image_to_jpeg(self, rgb_image: np.ndarray):
        """
        Orchestrates the JPEG conversion pipeline.
        Args:
            rgb_image: np.ndarray, shape (H, W, 3), dtype uint8
        Returns:
            jpeg_data: dict with quantized DCT blocks for Y, Cb, Cr channels
        """

        # Run the JPEG pipeline
        jpeg_data = jpeg_encode_image(rgb_image)

        # You can now use jpeg_data for further processing,
        # such as saving to a file, passing to the view for display, etc.
        
        return jpeg_data


