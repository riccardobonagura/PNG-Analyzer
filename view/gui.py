import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

class AppView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("PNG Analyzer - GUI")
        self.root.geometry("1000x700")

        self.image_panel = None
        self.metadata_label = None

        # Bottone per caricare immagine
        self.load_button = tk.Button(self.root, text="📂 Carica immagine PNG", command=self.load_image)
        self.load_button.pack(pady=10)

        # Bottone per convertire in YCbCr
        self.ycbcr_button = tk.Button(self.root, text="🎨 Converti in YCbCr", command=self.convert_to_ycbcr)
        self.ycbcr_button.pack(pady=5)

        # Area per metadati
        self.metadata_label = tk.Label(self.root, text="", font=("Arial", 11), justify="left")
        self.metadata_label.pack(pady=5)

        # Area immagine
        self.image_panel = tk.Label(self.root)
        self.image_panel.pack(pady=10)

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not filepath:
            return

        success = self.controller.load_image(filepath)
        if not success:
            messagebox.showerror("Errore", "Impossibile caricare l'immagine.")
            return

        # Visualizza immagine e metadati
        self.update_image_display()
        self.update_metadata_display()

    def update_image_display(self):
        image = self.controller.get_current_image()
        if image is None:
            return

        # Converti BGR (OpenCV) → RGB (PIL)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)

        # Ridimensionamento per la GUI
        image_pil.thumbnail((800, 500))

        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_panel.configure(image=image_tk)
        self.image_panel.image = image_tk

    def update_metadata_display(self):
        resolution = self.controller.get_image_resolution()
        channels = self.controller.get_image_channels()
        color_space = self.controller.get_color_space()
        filepath = self.controller.get_filepath()

        text = f"📁 File: {filepath}\n" \
               f"📐 Risoluzione: {resolution[0]} × {resolution[1]}\n" \
               f"🌈 Canali: {channels}\n" \
               f"🎨 Spazio colore: {color_space}"

        self.metadata_label.config(text=text)

    def convert_to_ycbcr(self):
        """
        Esegue la conversione a YCbCr tramite il controller e aggiorna l'immagine visualizzata.
        """
        try:
            self.controller.convert_to_ycbcr()
            self.update_image_display()
            self.update_metadata_display()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Errore", str(e))
