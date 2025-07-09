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

    def get_rgb_histogram_figure(self, screen_width: int, screen_height: int):
        """
        Genera una figura matplotlib che mostra 4 istogrammi:
        R, G, B e composito RGB con curve sovrapposte.
        """
        image = self.model.get_current_image()
        if image is None:
            raise RuntimeError("Nessuna immagine caricata.")

        # Converti da BGR (OpenCV) a RGB
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return create_rgb_histogram_figure(rgb_image, screen_width, screen_height)





    # GESTIONE SETTORE SUBSAMPLING

    def get_ycbcr_subsampling_figure(self, screen_width: int, screen_height: int) -> 'Figure':
        """
        Genera la figura matplotlib per visualizzare:
        - Immagine originale YCbCr
        - Subsampling 4:2:2 e 4:2:0
        - Info: risoluzione cromatica, memoria, matrici 4x4 con Y, Cb, Cr
        """
        from model.subsampling_tools import (
            convert_rgb_to_ycbcr,
            subsample_422,
            subsample_420,
            extract_center_matrix,
            compute_chroma_memory_usage
        )
        from model.subsampling_figure import create_subsampling_figure
        import cv2

        image_bgr = self.model.get_current_image()
        if image_bgr is None:
            raise RuntimeError("Nessuna immagine caricata.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        ycbcr_image = convert_rgb_to_ycbcr(image_rgb)

        # Subsampling
        image_422 = subsample_422(ycbcr_image)
        image_420 = subsample_420(ycbcr_image)

        # Risoluzioni e memoria
        h, w = ycbcr_image.shape[:2]
        y_res = (w, h)
        cbcr_res_422 = (w // 2, h)
        cbcr_res_420 = (w // 2, h // 2)

        mem_orig = compute_chroma_memory_usage(ycbcr_image, "444")
        mem_422 = compute_chroma_memory_usage(ycbcr_image, "422")
        mem_420 = compute_chroma_memory_usage(ycbcr_image, "420")

        # Matrici 4x4 dal centro
        center_block = extract_center_matrix(ycbcr_image, size=4)
        y4 = center_block[:, :, 0]
        cb4 = center_block[:, :, 1]
        cr4 = center_block[:, :, 2]

        center_422 = extract_center_matrix(image_422, size=4)
        y4_422 = center_422[:, :, 0]
        cb4_422 = center_422[:, :, 1]
        cr4_422 = center_422[:, :, 2]

        center_420 = extract_center_matrix(image_420, size=4)
        y4_420 = center_420[:, :, 0]
        cb4_420 = center_420[:, :, 1]
        cr4_420 = center_420[:, :, 2]

        # Genera figura
        fig = create_subsampling_figure(
            image_rgb,
            image_422,
            image_420,
            mem_orig,
            mem_422,
            mem_420,
            y4, cb4, cr4,
            y4_422, cb4_422, cr4_422,
            y4_420, cb4_420, cr4_420,
            screen_width,
            screen_height
        )

        return fig




