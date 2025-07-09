import cv2
from model.image_model import ImageModel
from model.color_tools import create_rgb_histogram_figure


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

    def get_ycbcr_figure(self):
        """
        Richiama il model per ottenere una figura matplotlib con i canali Y, Cb e Cr.
        """
        return self.model.get_ycbcr_figure()

    def get_hsv_figure(self, screen_width: int, screen_height: int):
        """
        Ottiene la figura matplotlib che mostra i canali HSV dal model.
        """
        return self.model.get_hsv_figure(screen_width, screen_height)

    def get_rgb_figure(self, screen_width: int, screen_height: int):
        return self.model.get_rgb_figure(screen_width, screen_height)


    def get_rgb_histogram_figure(self, screen_width: int, screen_height: int, separate: bool):
        """
        Genera una figura matplotlib degli istogrammi RGB (separati o compositi).
        """
        image = self.model.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # Converti da BGR (OpenCV) a RGB
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return create_rgb_histogram_figure(rgb_image, screen_width, screen_height, separate)

