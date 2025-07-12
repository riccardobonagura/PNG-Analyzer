# ========================================================
# TABELLA DELLE FIRME DEI METODI DI AppController
#
# AppController(model: ImageModel)
#     # Costruttore del controller, riceve il model e fornisce metodi intermedi per la GUI.
#
# load_image(self, filepath: str) -> bool
#     # Carica un'immagine nel model dato un percorso. Restituisce True se il caricamento ha successo.
#
# reset_image(self) -> None
#     # Resetta l'immagine caricata nel model.
#
# is_image_loaded(self) -> bool
#     # Ritorna True se un'immagine è attualmente caricata nel model.
#
# get_current_image(self) -> np.ndarray | None
#     # Ritorna l'immagine BGR corrente (OpenCV), se presente.
#
# get_filepath(self) -> str
#     # Ritorna il percorso del file corrente.
#
# get_image_resolution(self) -> tuple[int, int]
#     # Ritorna la risoluzione (larghezza, altezza) dell'immagine.
#
# get_image_channels(self) -> int
#     # Ritorna il numero di canali dell'immagine corrente.
#
# get_color_space(self) -> str
#     # Ritorna lo spazio colore dell'immagine corrente.
#
# get_rgb_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura matplotlib dei canali RGB equalizzati e stretchati.
#
# get_ycbcr_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura matplotlib dei canali YCbCr.
#
# get_hsv_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura matplotlib dei canali HSV.
#
# get_rgb_histogram_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura con i 4 istogrammi RGB (R, G, B, composito).
#
# get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura di confronto tra YCbCr 4:4:4, 4:2:2, 4:2:0.
#
# get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure
#     # Ritorna la figura 2x2 con RGB originale/bilanciata e scatter HSV 3D.
#
# convert_image_to_jpeg(self, compression_level: str = "med") -> bytes
#     # Converte l'immagine corrente in JPEG (didattico) e restituisce i bytes JPEG.
#
# process_image_directionality(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[float, Figure]
#     # Calcola la direzionalità Tamura e ritorna valore scalare + istogramma polare.
#
# process_image_granularity(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[float, Figure]
#     # Calcola la granularità Tamura e ritorna valore scalare + immagine con granuli.
#
# process_image_contrast(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[float, Figure]
#     # Calcola il contrasto Tamura e ritorna valore scalare + mappa di contrasto.
# ========================================================

# ========================================================
# 1. IMPORT NECESSARI
import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from model.image_model import ImageModel
from model.color_tools import split_rgb_channels, split_ycbcr_channels, convert_rgb_to_ycbcr, compute_rgb_histograms


# ========================================================

# ========================================================
# 2. CLASSE DEL CONTROLLER
class AppController:

    def __init__(self, model: ImageModel):
        self.model = model

    def load_image(self, filepath: str) -> bool:
        # Richiede al model di caricare l'immagine dal file
        return self.model.load_image_from_file(filepath)

    def reset_image(self) -> None:
        # Ripristina l'immagine allo stato originale
        self.model.reset_to_original()

    def is_image_loaded(self) -> bool:
        # Verifica se un'immagine è stata caricata
        return self.model.is_image_loaded()

    def get_current_image(self) -> np.ndarray | None:
        # Ottiene l'immagine corrente dal model
        return self.model.get_current_image()

    def get_filepath(self) -> str:
        # Restituisce il percorso del file caricato
        return self.model.get_filepath()

    def get_image_resolution(self) -> tuple[int, int]:
        # Restituisce la risoluzione (larghezza, altezza) dell'immagine
        return self.model.get_resolution()

    def get_image_channels(self) -> int:
        # Restituisce il numero di canali dell'immagine corrente
        return self.model.get_num_channels()

    def bgr_to_rgb(self, image: np.ndarray) -> np.ndarray:
        return image[..., ::-1]

    def get_color_space(self) -> str:
        return self.model.get_color_space()

    def get_rgb_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        R, G, B = split_rgb_channels(rgb_image)

        def manual_eq(channel: np.ndarray) -> np.ndarray:
            hist = np.bincount(channel.flatten(), minlength=256)
            cdf = hist.cumsum()
            cdf_masked = np.ma.masked_equal(cdf, 0)
            cdf_min = cdf_masked.min()
            cdf_max = cdf_masked.max()
            eq = ((cdf_masked - cdf_min) * 255 / (cdf_max - cdf_min)).filled(0).astype(np.uint8)
            return eq[channel]

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

    def get_ycbcr_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ycbcr_image = convert_rgb_to_ycbcr(rgb_image)
        Y, Cb, Cr = split_ycbcr_channels(ycbcr_image)

        margin_factor = 0.85
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)

        axs = [
            fig.add_subplot(1, 2, 1),
            fig.add_subplot(3, 2, 2),
            fig.add_subplot(3, 2, 4),
            fig.add_subplot(3, 2, 6),
        ]

        axs[0].imshow(rgb_image)
        axs[0].set_title("Immagine RGB originale")
        axs[0].axis("off")
        axs[1].imshow(Y, cmap='gray')
        axs[1].set_title("Y (Luminanza)")
        axs[2].imshow(Cb, cmap='gray')
        axs[2].set_title("Cb (Blu-diff)")
        axs[3].imshow(Cr, cmap='gray')
        axs[3].set_title("Cr (Rosso-diff)")

        for ax in axs[1:]:
            ax.axis("off")

        fig.tight_layout()
        return fig

    def get_hsv_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        image = self.model.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")


        H, S, V = self.model.get_hsv_channels()

        margin_factor = 0.85
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)

        axs = [
            fig.add_subplot(1, 2, 1),  # HSV originale (in RGB)
            fig.add_subplot(3, 2, 2),  # H
            fig.add_subplot(3, 2, 4),  # S
            fig.add_subplot(3, 2, 6),  # V
        ]

        # Immagine originale in RGB
        axs[0].imshow(self.bgr_to_rgb(image))
        axs[0].set_title("Immagine HSV originale (in RGB)")
        axs[0].axis("off")

        # Canale H (Hue) visualizzato con cmap 'hsv'
        axs[1].imshow(H, cmap='hsv')
        axs[1].set_title("H (Tonalità)")

        # Canali S e V con cmap 'gray' (valori scalar)
        axs[2].imshow(S, cmap='gray')
        axs[2].set_title("S (Saturazione)")

        axs[3].imshow(V, cmap='gray')
        axs[3].set_title("V (Valore)")

        for ax in axs[1:]:
            ax.axis("off")

        fig.tight_layout()
        return fig

    def get_rgb_histogram_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        image = self.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hist_r, hist_g, hist_b, bins = compute_rgb_histograms(rgb_image)
        margin_factor = 0.75
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        axs = [
            fig.add_subplot(2, 2, 1),
            fig.add_subplot(2, 2, 2),
            fig.add_subplot(2, 2, 3),
            fig.add_subplot(2, 2, 4),
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

    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        data = self.model.get_ycbcr_subsampling_data()

        margin_factor = 0.85
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)
        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        axs = [[fig.add_subplot(3, 3, i + j * 3 + 1) for i in range(3)] for j in range(3)]

        titles = ["YCbCr 4:4:4", "YCbCr 4:2:2", "YCbCr 4:2:0"]
        images = [data["image_rgb"], data["image_422"], data["image_420"]]
        mems = [data["mem_orig"], data["mem_422"], data["mem_420"]]
        matrices = [
            (data["y4"], data["cb4"], data["cr4"]),
            (data["y4_422"], data["cb4_422"], data["cr4_422"]),
            (data["y4_420"], data["cb4_420"], data["cr4_420"]),
        ]

        for col in range(3):
            axs[0][col].imshow(images[col])
            axs[0][col].set_title(titles[col], fontsize=10)
            axs[0][col].axis("off")

            res_text = f"Memoria: {mems[col]:.1f} KB"
            axs[1][col].text(0.5, 0.5, res_text, fontsize=9, ha='center', va='center')
            axs[1][col].axis("off")

            # Matrici da mostrare
            Y, Cb, Cr = matrices[col]
            matrix_str = (
                    "Y:\n" + np.array2string(Y, separator=", ") + "\n\n" +
                    "Cb:\n" + np.array2string(Cb, separator=", ") + "\n\n" +
                    "Cr:\n" + np.array2string(Cr, separator=", ")
            )
            axs[2][col].text(
                0.5, 0.5, matrix_str,
                fontsize=8, family="monospace",
                va='center', ha='center',
                linespacing=1.4,
                transform=axs[2][col].transAxes
            )
            axs[2][col].axis("off")

        fig.tight_layout()
        return fig

    def get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100) -> Figure:
        data = self.model.get_hsv_scatter_comparison_data()
        fig = plt.figure(figsize=(screen_width * 0.9 / dpi, screen_height * 0.9 / dpi), dpi=dpi, constrained_layout=True)
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.imshow(data["image_rgb"])
        ax1.set_title("Immagine originale (RGB)")
        ax1.axis("off")
        h_o, s_o, v_o, c_o = data["scatter_data"]["original"]
        ax2 = fig.add_subplot(2, 2, 2, projection='3d')
        ax2.scatter(h_o, s_o, v_o, c=c_o, s=3, alpha=0.5)
        ax2.set_title("HSV scatter originale")
        ax2.set_xlabel("Hue")
        ax2.set_ylabel("Saturation")
        ax2.set_zlabel("Value")
        ax2.set_xlim(0, 179)
        ax2.set_ylim(0, 255)
        ax2.set_zlim(0, 255)
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.imshow(data["image_balanced_rgb"])
        ax3.set_title("Immagine bilanciata (gray world)")
        ax3.axis("off")
        h_b, s_b, v_b, c_b = data["scatter_data"]["balanced"]
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

    def convert_image_to_jpeg(self, compression_level: str = "med") -> bytes:
        """
        Converte l'immagine corrente (in RGB) in JPEG utilizzando la pipeline didattica.
        Il controller gestisce la conversione da BGR a RGB, seleziona la qualità,
        e invoca la pipeline del model.

        Args:
            compression_level (str): livello di compressione ('low', 'med', 'high').

        Returns:
            bytes: immagine JPEG codificata (senza codifica entropica).
        """
        from model.jpeg_tools import get_quant_tables
        from model.jpeg_pipeline import jpeg_encode_image

        # Step 1: Ottiene immagine corrente e la converte in RGB
        image_bgr = self.get_current_image()
        if image_bgr is None:
            raise RuntimeError("Nessuna immagine caricata.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Step 2: Ottiene le tabelle di quantizzazione dal livello richiesto
        q_luma, q_chroma = get_quant_tables(compression_level)

        # Step 3: Passa tutto alla pipeline JPEG per ottenere i bytes finali
        jpeg_bytes = jpeg_encode_image(image_rgb, q_luma, q_chroma)

        return jpeg_bytes

    def process_image_directionality(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[
        float, Figure]:
        from model.texture_tools import compute_directionality_grid

        image_bgr = self.get_current_image()
        if image_bgr is None:
            raise RuntimeError("Nessuna immagine caricata.")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        directionality, hist = compute_directionality_grid(image_rgb)
        # Step 3: Costruisce la figura matplotlib (solo istogramma polare)
        bins = len(hist)
        theta = np.linspace(0.0, np.pi, bins, endpoint=False)
        radii = hist.astype(np.float32)

        # Calcolo dimensioni dinamiche
        margin_factor = 0.7
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)

        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax = fig.add_subplot(111, polar=True)
        ax.set_theta_zero_location("N")  # 0° verso l'alto
        ax.set_theta_direction(-1)  # senso orario

        bars = ax.bar(theta, radii, width=np.pi / bins, bottom=0.0, align='edge', edgecolor='black')
        for bar in bars:
            bar.set_alpha(0.7)
            bar.set_facecolor("tab:blue")

        ax.set_title("Istogramma Polare", va='bottom')
        fig.suptitle(f"Direzionalità Tamura: {directionality:.3f}", fontsize=14)
        fig.tight_layout()
        return directionality, fig

    def process_image_granularity(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[float, Figure]:
        """
        Calcola la granularità Tamura e costruisce una figura matplotlib con i granuli sovrapposti all'immagine.

        Returns:
            Tuple contenente:
                - granularità (float)
                - figura matplotlib con l'immagine originale e granuli evidenziati
        """
        from model.texture_tools import tamura_granularity

        # Step 1: Ottiene immagine corrente in RGB
        image_bgr = self.get_current_image()
        if image_bgr is None:
            raise RuntimeError("Nessuna immagine caricata.")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Step 2: Calcola granularità e ottiene lista granuli
        granularity_value, granules_data = tamura_granularity(image_rgb)

        # Step 3: Costruzione figura con granuli sovrapposti
        margin_factor = 0.85
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)

        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax = fig.add_subplot(111)
        ax.imshow(image_rgb)
        ax.set_title(f"Granularità Tamura: {granularity_value:.4f}")
        ax.axis("off")

        # Step 4: Sovrapposizione dei granuli come cerchi
        for (x, y, area) in granules_data:
            radius = np.sqrt(area / np.pi)
            circle = plt.Circle((x, y), radius=radius, color='cyan', alpha=0.5, linewidth=1.2, fill=True)
            ax.add_patch(circle)

        return granularity_value, fig

    def process_image_contrast(self, screen_width: int, screen_height: int, dpi: int = 100) -> tuple[float, Figure]:
        """
        Calcola il contrasto Tamura e costruisce una figura matplotlib con la mappa di contrasto.

        Returns:
            Tuple contenente:
                - contrasto (float)
                - figura matplotlib con la mappa di contrasto
        """
        from model.texture_tools import tamura_contrast_map

        # Step 1: Ottiene immagine corrente in RGB
        image_bgr = self.get_current_image()
        if image_bgr is None:
            raise RuntimeError("Nessuna immagine caricata.")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Step 2: Calcola valore e mappa di contrasto
        contrast_value, contrast_map = tamura_contrast_map(image_rgb)

        # Step 3: Costruisce la figura matplotlib
        margin_factor = 0.85
        fig_width = int((screen_width * margin_factor) / dpi)
        fig_height = int((screen_height * margin_factor) / dpi)

        fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax = fig.add_subplot(111)
        im = ax.imshow(contrast_map, cmap="plasma", interpolation="nearest")
        ax.set_title(f"Contrasto Tamura: {contrast_value:.4f}")
        ax.axis("off")

        # Step 4: Aggiunge barra colore
        fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)

        return contrast_value, fig

# ========================================================
