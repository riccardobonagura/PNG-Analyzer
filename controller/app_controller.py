import cv2
from model.image_model import ImageModel

class AppController:
    """
    Gestisce la logica di coordinamento tra View (GUI) e Model (ImageModel).
    """

    def __init__(self):
        self.model = ImageModel()

    def load_image(self, filepath: str) -> bool:
        """
        Carica un'immagine PNG. Ritorna True se ha successo, False altrimenti.
        """
        try:
            self.model.load_image_from_file(filepath)
            return True
        except Exception as e:
            print(f"[Errore] {e}")
            return False

    def reset_image(self):
        """
        Ripristina l'immagine allo stato originale.
        """
        self.model.reset_to_original()

    def get_current_image(self):
        """
        Restituisce l'immagine corrente (in formato BGR per OpenCV).
        """
        return self.model.get_current_image()

    def get_original_image(self):
        """
        Restituisce l'immagine originale.
        """
        return self.model.get_original_image()

    def get_image_resolution(self):
        """
        Restituisce la risoluzione corrente dell'immagine (width, height).
        """
        return self.model.get_resolution()

    def get_image_channels(self):
        """
        Restituisce il numero di canali dell'immagine corrente.
        """
        return self.model.get_num_channels()

    def get_color_space(self):
        """
        Restituisce il nome dello spazio colore attuale.
        """
        return self.model.get_color_space()

    def is_image_loaded(self):
        """
        Verifica se è stata caricata un'immagine.
        """
        return self.model.is_image_loaded()

    def get_filepath(self):
        """
        Restituisce il percorso del file caricato.
        """
        return self.model.get_filepath()

    def update_image(self, new_image):
        """
        Aggiorna l'immagine corrente con una nuova versione modificata.
        """
        self.model.set_current_image(new_image)


    def convert_to_ycbcr(self):
        """
        Richiama il model per convertire l'immagine in YCbCr.
        """
        self.model.convert_to_ycbcr()

