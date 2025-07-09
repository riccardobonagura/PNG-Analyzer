import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np

class ImageLoaderApp:
    def __init__(self, root):
        # Imposta la dimensione della finestra a un quarto dello schermo
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = screen_width // 2
        height = screen_height // 2
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

        self.root = root
        self.root.title("Carica e Visualizza PNG")

        self.img_label = tk.Label(root)
        self.img_label.pack()

        self.info_label = tk.Label(root, text="", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.load_btn = tk.Button(root, text="Carica PNG", command=self.load_image)
        self.load_btn.pack(pady=10)

        self.image = None
        self.img_path = None

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine PNG",
            filetypes=[("PNG files", "*.png")]
        )
        if not file_path:
            return

        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            messagebox.showerror("Errore", "Impossibile caricare l'immagine selezionata.")
            return

        self.image = img
        self.img_path = file_path

        height, width = img.shape[:2]

        if len(img.shape) == 2:
            color_space = "Grayscale"
        elif img.shape[2] == 3:
            color_space = "BGR"
        elif img.shape[2] == 4:
            color_space = "BGRA"
        else:
            color_space = f"Canali: {img.shape[2]}"

        self.info_label.config(
            text=f"Risoluzione: {width} x {height}\nSpazio colore: {color_space}"
        )

        if color_space == "BGR":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif color_space == "BGRA":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        elif color_space == "Grayscale":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = img

        # Ridimensiona l'immagine per stare dentro la finestra, lasciando margine
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        max_w = int(root_width * 0.9)
        max_h = int(root_height * 0.6)
        scale = min(max_w / width, max_h / height, 1)
        new_w, new_h = int(width * scale), int(height * scale)
        img_disp = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt

        fig = plt.Figure(figsize=(new_w/100, new_h/100), dpi=100)
        ax = fig.add_subplot(111)
        ax.imshow(img_disp)
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        # Rimuovi vecchi canvas se presenti
        if hasattr(self, 'current_canvas'):
            self.current_canvas.pack_forget()
        self.current_canvas = canvas_widget

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLoaderApp(root)
    root.mainloop()