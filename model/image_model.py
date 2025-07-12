# ========================================================
# 0. TABELLA DELLE FIRME DEI METODI DELLA CLASSE IMAGEMODEL, classe principale del model
#
# ImageModel.__init__(self)
#     # Inizializza lo stato interno della classe ImageModel.
#
# ImageModel.load_image_from_file(self, filepath: str)
#     # Carica un'immagine PNG dal percorso specificato, gestisce RGBA→BGR.
#
# ImageModel.reset_to_original(self)
#     # Ripristina l'immagine corrente allo stato originale.
#
# ImageModel.get_resolution(self)
#     # Restituisce la risoluzione dell'immagine corrente (larghezza, altezza).
#
# ImageModel.get_num_channels(self)
#     # Restituisce il numero di canali dell'immagine corrente.
#
# ImageModel.get_color_space(self)
#     # Restituisce lo spazio colore associato (assunto come sRGB).
#
# ImageModel.get_current_image(self)
#     # Restituisce l'immagine corrente come array NumPy.
#
# ImageModel.get_original_image(self)
#     # Restituisce l'immagine originale come array NumPy.
#
# ImageModel.set_current_image(self, image: np.ndarray)
#     # Sostituisce l'immagine corrente con un nuovo array.
#
# ImageModel.is_image_loaded(self)
#     # Restituisce True se un'immagine è stata caricata, False altrimenti.
#
# ImageModel.get_filepath(self)
#     # Restituisce il percorso del file caricato.
#
# ImageModel.get_ycbcr_channels(self)
#     # Restituisce i canali Y, Cb, Cr dell'immagine corrente come tuple di array.
#
# ImageModel.get_hsv_channels(self)
#     # Restituisce i canali H, S, V dell'immagine corrente come tuple di array.
#
# ImageModel.get_rgb_channels(self)
#     # Restituisce i canali R, G, B dell'immagine corrente come tuple di array.
#
# ImageModel.get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int, dpi: int = 100)
#     # Restituisce una figura matplotlib che confronta original/subsampled YCbCr (4:4:4, 4:2:2, 4:2:0) con matrici centrali e spazio memoria.
#
# ImageModel.get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100)
#     # Restituisce una figura matplotlib 2x2 con RGB originale, RGB bilanciata, scatter HSV originale e scatter HSV bilanciata.
# ========================================================

# ========================================================
# 1. IMPORT DELLE LIBRERIE
import cv2
import numpy as np

import model.color_tools
from model.color_tools import create_hsv_scatter_comparison_figure

# ========================================================

# ========================================================
# 2. DEFINIZIONE DELLA CLASSE ImageModel
class ImageModel:
    """
    Gestisce lo stato dell'immagine PNG corrente:
    - Caricamento da file
    - Stato originale vs modificato
    - Accesso a dimensioni, canali, spazio colore
    """

    # ----------------------------------------------------
    # 2.1. Costruttore
    def __init__(self):
        # Inizializza gli attributi privati
        self._original_image = None  # Immagine originale caricata
        self._current_image = None  # Immagine corrente (può essere modificata)
        self._filepath = None  # Percorso del file caricato

    # ----------------------------------------------------
    # 2.2. Caricamento immagine da file
    def load_image_from_file(self, filepath: str) -> bool:
        try:
            image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            if image is None:
                print(f"[ERRORE] Impossibile leggere il file: {filepath}")
                return False

            # Converti RGBA → BGR se necessario
            if image.shape[-1] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

            self._original_image = image.copy()
            self._current_image = image.copy()
            self._filepath = filepath
            print(f"[OK] Immagine caricata: {filepath}, shape={image.shape}")
            return True

        except Exception as e:
            print(f"[EXCEPTION] Errore durante il caricamento: {e}")
            return False

    # ----------------------------------------------------
    # 2.3. Ripristino immagine allo stato originale
    def reset_to_original(self):
        """
        Ripristina l'immagine corrente allo stato originale.
        Input: nessuno
        Output: nessuno (aggiorna lo stato interno della classe)
        Comportamento atteso: _current_image = copia di _original_image
        """
        # Se è presente l'immagine originale, la copia nello stato corrente
        if self._original_image is not None:
            self._current_image = self._original_image.copy()

    # ----------------------------------------------------
    # 2.4. Ottieni la risoluzione dell'immagine corrente
    def get_resolution(self):
        """
        Restituisce la risoluzione dell'immagine corrente come (larghezza, altezza).
        Input: nessuno
        Output: tuple (width, height) oppure None se nessuna immagine caricata
        Comportamento atteso: restituisce dimensioni dell'immagine
        """
        # Controllo che l'immagine sia stata caricata
        if self._current_image is None:
            return None
        # Estrae altezza e larghezza dai primi due assi dell'array
        height, width = self._current_image.shape[:2]
        return width, height

    # ----------------------------------------------------
    # 2.5. Ottieni il numero di canali dell'immagine corrente
    def get_num_channels(self):
        """
        Restituisce il numero di canali dell'immagine corrente.
        Input: nessuno
        Output: int (numero canali) oppure None se nessuna immagine caricata
        Comportamento atteso: restituisce canali (1 per grayscale, 3 per RGB/BGR)
        """
        # Controllo che l'immagine sia stata caricata
        if self._current_image is None:
            return None
        # Se l'immagine è 3D, restituisce il terzo asse (canali), altrimenti 1 (grayscale)
        return self._current_image.shape[2] if len(self._current_image.shape) == 3 else 1

    # ----------------------------------------------------
    # 2.6. Ottieni lo spazio colore dell'immagine corrente
    def get_color_space(self):
        """
        Restituisce lo spazio colore associato all'immagine corrente.
        Input: nessuno
        Output: str ("sRGB" oppure None se nessuna immagine caricata)
        Comportamento atteso: restituisce "sRGB" per immagini a colori (assunto BGR/standard OpenCV)
        """
        # Controllo che l'immagine sia stata caricata
        if self._current_image is None:
            return None
        # Nota: in OpenCV le immagini sono caricate come BGR, ma si assume sRGB come standard
        return "sRGB"

    # ----------------------------------------------------
    # 2.7. Ottieni l'immagine corrente
    def get_current_image(self):
        """
        Restituisce l'immagine corrente come array NumPy.
        Input: nessuno
        Output: array NumPy, oppure None se non caricata
        Comportamento atteso: restituisce lo stato attuale dell'immagine
        """
        # Restituisce semplicemente la variabile interna
        return self._current_image

    # ----------------------------------------------------
    # 2.8. Ottieni l'immagine originale
    def get_original_image(self):
        """
        Restituisce l'immagine originale.
        Input: nessuno
        Output: array NumPy, oppure None se non caricata
        Comportamento atteso: restituisce la copia originale dell'immagine
        """
        # Restituisce semplicemente la variabile interna
        return self._original_image

    # ----------------------------------------------------
    # 2.9. Imposta una nuova immagine corrente
    def set_current_image(self, image: np.ndarray):
        """
        Sostituisce l'immagine corrente con una nuova versione modificata.
        Input: image (np.ndarray) - nuova immagine da impostare
        Output: nessuno (aggiorna lo stato interno della classe)
        Comportamento atteso: aggiorna _current_image
        """
        # Aggiorna lo stato interno con una nuova immagine
        self._current_image = image

    # ----------------------------------------------------
    # 2.10. Verifica se un'immagine è stata caricata
    def is_image_loaded(self):
        """
        Verifica se un'immagine è stata caricata.
        Input: nessuno
        Output: bool - True se caricata, False altrimenti
        Comportamento atteso: restituisce True se _current_image è presente
        """
        # Controlla la presenza di una immagine corrente caricata
        return self._current_image is not None

    # ----------------------------------------------------
    # 2.11. Ottieni il percorso del file caricato
    def get_filepath(self):
        """
        Restituisce il percorso del file caricato.
        Input: nessuno
        Output: str - percorso del file, oppure None se non presente
        Comportamento atteso: restituisce il percorso come stringa
        """
        # Restituisce la variabile interna con il percorso
        return self._filepath

    # ----------------------------------------------------
    # 2.12. Ottieni i canali Y, Cb, Cr dell'immagine corrente
    def get_ycbcr_channels(self):
        """
        Restituisce i canali Y, Cb, Cr dell'immagine corrente.
        Input: nessuno
        Output: tuple di array (Y, Cb, Cr)
        Comportamento atteso: converte l'immagine in RGB, poi in YCbCr, poi estrae i canali
        """
        # Controlla che un'immagine sia stata caricata
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        # Converte da BGR (OpenCV) a RGB (richiesto dalla funzione)
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        # Converte l'immagine RGB in YCbCr
        ycbcr = model.color_tools.convert_rgb_to_ycbcr(rgb_image)
        # Estrae i canali Y, Cb, Cr
        return model.color_tools.split_ycbcr_channels(ycbcr)

    # ----------------------------------------------------
    # 2.13. Ottieni i canali H, S, V dell'immagine corrente
    def get_hsv_channels(self):
        """
        Restituisce i canali H, S, V dell'immagine corrente.
        Input: nessuno
        Output: tuple di array (H, S, V)
        Comportamento atteso: converte l'immagine in RGB, poi in HSV, poi estrae i canali
        """
        # Controlla che un'immagine sia stata caricata
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        # Converte da BGR (OpenCV) a RGB
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        # Converte l'immagine RGB in HSV
        hsv = model.color_tools.convert_rgb_to_hsv_manual(rgb_image)
        # Estrae i canali H, S, V
        return model.color_tools.split_hsv_channels(hsv)

    # ----------------------------------------------------
    # 2.14. Ottieni i canali R, G, B dell'immagine corrente
    def get_rgb_channels(self):
        """
        Restituisce i canali R, G, B dell'immagine corrente.
        Input: nessuno
        Output: tuple di array (R, G, B)
        Comportamento atteso: converte l'immagine da BGR a RGB, poi estrae i canali
        """
        # Controlla che un'immagine sia stata caricata
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")
        # Converte da BGR (OpenCV) a RGB
        rgb_image = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        # Estrae i canali R, G, B
        return model.color_tools.split_rgb_channels(rgb_image)

        # ----------------------------------------------------

    # 2.15. Estrai dati per figura di confronto subsampling YCbCr
    def get_ycbcr_subsampling_data(self) -> dict:
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        import model.subsampling_tools as tools

        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        ycbcr = model.color_tools.convert_rgb_to_ycbcr(image_rgb)
        ycbcr_422 = tools.subsample_422(ycbcr)
        ycbcr_420 = tools.subsample_420(ycbcr)

        image_422 = model.color_tools.convert_ycbcr_to_rgb(ycbcr_422)
        image_420 = model.color_tools.convert_ycbcr_to_rgb(ycbcr_420)

        def estrai_matrici(ycbcr_img):
            mat = tools.extract_center_matrix(ycbcr_img, size=4)
            return mat[:, :, 0], mat[:, :, 1], mat[:, :, 2]

        y4, cb4, cr4 = estrai_matrici(ycbcr)
        y4_422, cb4_422, cr4_422 = estrai_matrici(ycbcr_422)
        y4_420, cb4_420, cr4_420 = estrai_matrici(ycbcr_420)

        def memoria_totale(ycbcr_img, mode):
            Y_bytes = ycbcr_img.shape[0] * ycbcr_img.shape[1]
            C_bytes = tools.compute_chroma_memory_usage(ycbcr_img, mode)
            return (Y_bytes + C_bytes) / 1024

        mem_orig = memoria_totale(ycbcr, "444")
        mem_422 = memoria_totale(ycbcr_422, "422")
        mem_420 = memoria_totale(ycbcr_420, "420")

        return {
            "image_rgb": image_rgb,
            "image_422": image_422,
            "image_420": image_420,
            "mem_orig": mem_orig,
            "mem_422": mem_422,
            "mem_420": mem_420,
            "y4": y4, "cb4": cb4, "cr4": cr4,
            "y4_422": y4_422, "cb4_422": cb4_422, "cr4_422": cr4_422,
            "y4_420": y4_420, "cb4_420": cb4_420, "cr4_420": cr4_420,
        }

    # ----------------------------------------------------
    # 2.16. Estrai dati per figura scatter HSV
    def get_hsv_scatter_comparison_data(self) -> dict:
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)
        image_balanced_rgb = model.color_tools.gray_world_white_balance(image_rgb)

        scatter_data = create_hsv_scatter_comparison_figure(
            image_rgb=image_rgb,
            image_balanced_rgb=image_balanced_rgb,
            convert_rgb_to_hsv=model.color_tools.convert_rgb_to_hsv_manual,
            stride=8
        )

        return scatter_data
    # ========================================================

# NOTA: alcuni getters e setters non sono stati usati, ma lasciati per completezza