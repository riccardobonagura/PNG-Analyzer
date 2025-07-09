import cv2
import numpy as np
from model.color_tools import convert_rgb_to_ycbcr

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


# All’interno della classe ImageModel:

    def convert_to_ycbcr(self):
        """
        Converte l'immagine corrente da RGB a YCbCr, aggiornando lo stato.
        """
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # Converti da BGR a RGB (OpenCV legge in BGR)
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        ycbcr_image = convert_rgb_to_ycbcr(rgb_image)

        # Converti YCbCr di nuovo in formato BGR per compatibilità GUI (solo per visione)
        self._current_image = cv2.cvtColor(ycbcr_image, cv2.COLOR_YCrCb2BGR)
