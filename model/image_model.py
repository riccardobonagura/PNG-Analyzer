import cv2
import numpy as np

import model.scatter_hsv_figures as scatter_figs
from model.color_tools import (
    convert_rgb_to_ycbcr,
    convert_rgb_to_hsv_manual,
    split_ycbcr_channels,
    split_hsv_channels,
    split_rgb_channels,
    gray_world_white_balance,
)


class ImageModel:
    """
    Gestisce lo stato dell'immagine PNG corrente:
    - Caricamento
    - Stato originale vs modificato
    - Accesso a dimensioni, canali, spazio colore
    """

    def __init__(self):
        self._original_image = None
        self._current_image = None
        self._filepath = None

    def load_image_from_file(self, filepath: str):
        """
        Carica un'immagine PNG dal percorso specificato.
        Se l'immagine ha 4 canali (RGBA), converte in RGB.
        """
        image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("Impossibile caricare l'immagine.")

        # Rimuovi canale alpha se presente
        if image.shape[-1] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        self._original_image = image.copy()
        self._current_image = image
        self._filepath = filepath

    def reset_to_original(self):
        """
        Ripristina l'immagine corrente allo stato originale.
        """
        if self._original_image is not None:
            self._current_image = self._original_image.copy()

    def get_resolution(self):
        """
        Restituisce la risoluzione dell'immagine corrente (larghezza, altezza).
        """
        if self._current_image is None:
            return None
        height, width = self._current_image.shape[:2]
        return width, height

    def get_num_channels(self):
        """
        Restituisce il numero di canali dell'immagine corrente.
        """
        if self._current_image is None:
            return None
        return self._current_image.shape[2] if len(self._current_image.shape) == 3 else 1

    def get_color_space(self):
        """
        Restituisce lo spazio colore associato (assunto come sRGB).
        """
        if self._current_image is None:
            return None
        return "sRGB"  # Default di OpenCV in BGR (poi convertito in RGB)

    def get_current_image(self):
        """
        Restituisce l'immagine corrente come array NumPy.
        """
        return self._current_image

    def get_original_image(self):
        """
        Restituisce l'immagine originale.
        """
        return self._original_image

    def set_current_image(self, image: np.ndarray):
        """
        Sostituisce l'immagine corrente con una nuova versione modificata.
        """
        self._current_image = image

    def is_image_loaded(self):
        """
        Verifica se un'immagine è stata caricata.
        """
        return self._current_image is not None

    def get_filepath(self):
        """
        Restituisce il percorso del file caricato.
        """
        return self._filepath

    def get_ycbcr_channels(self):
        """
        Restituisce i canali Y, Cb, Cr dell'immagine corrente.
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        ycbcr = convert_rgb_to_ycbcr(rgb_image)
        return split_ycbcr_channels(ycbcr)

    def get_hsv_channels(self):
        """
        Restituisce i canali H, S, V dell'immagine corrente.
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        hsv = convert_rgb_to_hsv_manual(rgb_image)
        return split_hsv_channels(hsv)

    def get_rgb_channels(self):
        """
        Restituisce i canali R, G, B dell'immagine corrente.
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        return split_rgb_channels(rgb_image)

    # --- Custom/Advanced Views (placeholder) ---
    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int, dpi: int = 100):
        """
        Restituisce una figura che confronta l'immagine originale con le versioni subsampled (4:2:2, 4:2:0)
        mostrando: immagine, risoluzioni, spazio occupato (Y+Cb+Cr), matrici 4x4 centrali dei canali Y, Cb, Cr.
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        import model.subsampling_tools as tools
        import model.subsampling_figure as figs

        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)

        # Conversione in YCbCr
        ycbcr = convert_rgb_to_ycbcr(image_rgb)
        ycbcr_422 = tools.subsample_422(ycbcr)
        ycbcr_420 = tools.subsample_420(ycbcr)

        # Per visualizzazione corretta: convertiamo le versioni subsampled in RGB
        image_422 = tools.convert_ycbcr_to_rgb(ycbcr_422)
        image_420 = tools.convert_ycbcr_to_rgb(ycbcr_420)

        # Estrai le matrici 4x4 centrali dei canali per ogni versione
        def estrai_matrici(ycbcr_img):
            mat = tools.extract_center_matrix(ycbcr_img, size=4)
            return mat[:, :, 0], mat[:, :, 1], mat[:, :, 2]

        y4, cb4, cr4 = estrai_matrici(ycbcr)
        y4_422, cb4_422, cr4_422 = estrai_matrici(ycbcr_422)
        y4_420, cb4_420, cr4_420 = estrai_matrici(ycbcr_420)

        # Calcola risoluzioni per ogni versione
        h, w = ycbcr.shape[:2]
        h_422, w_422 = ycbcr_422.shape[:2]
        h_420, w_420 = ycbcr_420.shape[:2]

        # Spazio occupato: Y + Cb + Cr in byte per ogni versione (1 byte per componente per pixel)
        def memoria_totale(ycbcr_img, mode):
            Y_bytes = ycbcr_img.shape[0] * ycbcr_img.shape[1]
            C_bytes = tools.compute_chroma_memory_usage(ycbcr_img, mode)
            return (Y_bytes + C_bytes) / 1024  # in KB

        mem_orig = memoria_totale(ycbcr, "444")
        mem_422 = memoria_totale(ycbcr_422, "422")
        mem_420 = memoria_totale(ycbcr_420, "420")

        # Chiama la funzione di creazione figura, che accetta già tutti i dati
        return figs.create_subsampling_figure(
            image_rgb=image_rgb,
            image_422=image_422,
            image_420=image_420,
            mem_orig=mem_orig,
            mem_422=mem_422,
            mem_420=mem_420,
            y4=y4, cb4=cb4, cr4=cr4,
            y4_422=y4_422, cb4_422=cb4_422, cr4_422=cr4_422,
            y4_420=y4_420, cb4_420=cb4_420, cr4_420=cr4_420,
            screen_width=screen_width,
            screen_height=screen_height,
            dpi=dpi
        )

    def get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100):
        """
        Restituisce una figura 2x2 con:
        - Immagine RGB originale (in alto a sinistra)
        - Scatter plot HSV originale (in alto a destra)
        - Immagine RGB bilanciata gray world (in basso a sinistra)
        - Scatter plot HSV bilanciata (in basso a destra)
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # Conversione da BGR (OpenCV) a RGB

        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)

        # White balance gray world (su RGB)
        image_balanced_rgb = gray_world_white_balance(image_rgb)

        fig = scatter_figs.create_hsv_scatter_comparison_figure(
            image_rgb=image_rgb,
            image_balanced_rgb=image_balanced_rgb,
            convert_rgb_to_hsv=convert_rgb_to_hsv_manual,
            stride=8,
            screen_width=screen_width,
            screen_height=screen_height,
            dpi=dpi
        )
        return fig
