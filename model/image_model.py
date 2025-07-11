# ========================================================
# 0. TABELLA DELLE FIRME DEI METODI DELLA CLASSE IMAGEMODEL
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
# Import di funzioni ausiliarie
import model.scatter_hsv_figures as scatter_figs
from model.color_tools import (
    convert_rgb_to_ycbcr,
    convert_rgb_to_hsv_manual,
    split_ycbcr_channels,
    split_hsv_channels,
    split_rgb_channels,
    gray_world_white_balance,
)


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
    def load_image_from_file(self, filepath: str):
        """
        Carica un'immagine PNG dal percorso specificato.
        Se l'immagine ha 4 canali (RGBA), la converte in BGR (standard OpenCV).
        Input: filepath (str) - percorso del file PNG
        Output: nessuno (aggiorna lo stato interno della classe)
        Comportamento atteso: aggiorna _original_image, _current_image, _filepath
        """
        # Caricamento dell'immagine dal file
        image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        # Controllo caricamento riuscito
        if image is None:
            raise ValueError("Impossibile caricare l'immagine.")
        # Rimozione canale alpha se presente (RGBA → BGR)
        if len(image.shape) == 3 and image.shape[-1] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        # Aggiorna lo stato interno della classe
        self._original_image = image.copy()
        self._current_image = image.copy()
        self._filepath = filepath

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
        ycbcr = convert_rgb_to_ycbcr(rgb_image)
        # Estrae i canali Y, Cb, Cr
        return split_ycbcr_channels(ycbcr)

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
        hsv = convert_rgb_to_hsv_manual(rgb_image)
        # Estrae i canali H, S, V
        return split_hsv_channels(hsv)

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
        return split_rgb_channels(rgb_image)

    # ----------------------------------------------------
    # 2.15. Genera figura di confronto subsampling YCbCr
    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int, dpi: int = 100):
        """
        Restituisce una figura che confronta l'immagine originale con le versioni subsampled (4:2:2, 4:2:0)
        mostrando: immagine, risoluzioni, spazio occupato (Y+Cb+Cr), matrici 4x4 centrali dei canali Y, Cb, Cr.
        Input:
            screen_width (int): larghezza schermo in pixel
            screen_height (int): altezza schermo in pixel
            dpi (int): DPI della figura
        Output:
            matplotlib.figure.Figure (figura matplotlib)
        Comportamento atteso:
            - Se non c'è immagine caricata, solleva RuntimeError
            - Prepara tutti i dati necessari e chiama la funzione di creazione figura
        """
        # 1. Controlla che un'immagine sia stata caricata
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # 2. Import dei moduli necessari per subsampling e visualizzazione
        import model.subsampling_tools as tools  # Funzioni di subsampling e conversione
        import model.subsampling_figure as figs  # Funzione di creazione figura

        # 3. Conversione da BGR (OpenCV) a RGB per la visualizzazione
        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)

        # 4. Conversione in YCbCr dell'immagine RGB
        ycbcr = convert_rgb_to_ycbcr(image_rgb)
        # 5. Subsampling 4:2:2 e 4:2:0 sull'immagine YCbCr
        ycbcr_422 = tools.subsample_422(ycbcr)  # Ingresso: YCbCr, Uscita: YCbCr subsampled 4:2:2
        ycbcr_420 = tools.subsample_420(ycbcr)  # Ingresso: YCbCr, Uscita: YCbCr subsampled 4:2:0

        # 6. Conversione delle immagini subsampled in RGB per la visualizzazione
        image_422 = tools.convert_ycbcr_to_rgb(ycbcr_422)  # Ingresso: YCbCr subsampled, Uscita: RGB
        image_420 = tools.convert_ycbcr_to_rgb(ycbcr_420)  # Ingresso: YCbCr subsampled, Uscita: RGB

        # 7. Estrazione delle matrici 4x4 centrali dei canali Y, Cb, Cr (per ogni versione)
        def estrai_matrici(ycbcr_img):
            # Ingresso: immagine YCbCr, Uscita: tuple di matrici (Y, Cb, Cr) 4x4 centrali
            mat = tools.extract_center_matrix(ycbcr_img, size=4)
            return mat[:, :, 0], mat[:, :, 1], mat[:, :, 2]

        y4, cb4, cr4 = estrai_matrici(ycbcr)
        y4_422, cb4_422, cr4_422 = estrai_matrici(ycbcr_422)
        y4_420, cb4_420, cr4_420 = estrai_matrici(ycbcr_420)

        # 8. Calcolo delle risoluzioni (altezza, larghezza) per ogni versione
        h, w = ycbcr.shape[:2]
        h_422, w_422 = ycbcr_422.shape[:2]
        h_420, w_420 = ycbcr_420.shape[:2]

        # 9. Calcolo dello spazio memoria occupato da Y, Cb, Cr per ogni versione (in KB)
        def memoria_totale(ycbcr_img, mode):
            # Ingresso: immagine YCbCr, modalità subsampling ("444","422","420")
            # Uscita: memoria totale in KB
            Y_bytes = ycbcr_img.shape[0] * ycbcr_img.shape[1]
            C_bytes = tools.compute_chroma_memory_usage(ycbcr_img, mode)
            return (Y_bytes + C_bytes) / 1024  # in KB

        mem_orig = memoria_totale(ycbcr, "444")
        mem_422 = memoria_totale(ycbcr_422, "422")
        mem_420 = memoria_totale(ycbcr_420, "420")

        # 10. Chiamata alla funzione di creazione figura subsampling
        # Ingresso: tutte le immagini, matrici, dimensioni, memoria
        # Uscita: figura matplotlib
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

    # ----------------------------------------------------
    # 2.16. Genera figura di confronto scatter HSV
    def get_hsv_scatter_comparison_figure(self, screen_width: int, screen_height: int, dpi: int = 100):
        """
        Restituisce una figura 2x2 con:
        - Immagine RGB originale (in alto a sinistra)
        - Scatter plot HSV originale (in alto a destra)
        - Immagine RGB bilanciata gray world (in basso a sinistra)
        - Scatter plot HSV bilanciata (in basso a destra)
        Input:
            screen_width (int): larghezza schermo in pixel
            screen_height (int): altezza schermo in pixel
            dpi (int): DPI della figura
        Output:
            matplotlib.figure.Figure (figura matplotlib)
        Comportamento atteso:
            - Se non c'è immagine caricata, solleva RuntimeError
            - Prepara tutti i dati necessari e chiama la funzione di creazione figura
        """
        # 1. Controlla che un'immagine sia stata caricata
        if self._current_image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # 2. Conversione da BGR (OpenCV) a RGB per la visualizzazione
        image_rgb = cv2.cvtColor(self._current_image, cv2.COLOR_BGR2RGB)

        # 3. Bilanciamento del bianco gray world sull'immagine RGB
        image_balanced_rgb = gray_world_white_balance(image_rgb)

        # 4. Chiamata alla funzione di creazione figura scatter HSV
        # Ingresso: immagini RGB, funzione di conversione HSV, parametri di visualizzazione
        # Uscita: figura matplotlib
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
    # ----------------------------------------------------

# ========================================================


