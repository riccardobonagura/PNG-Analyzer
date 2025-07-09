import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class AppView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("PNG Analyzer - GUI")
        self.root.state("zoomed")  # avvia a tutto schermo

        self.image_panel = None
        self.metadata_label = None
        self.rgb_canvas = None
        self.ycbcr_canvas = None
        self.hsv_canvas = None
        self.metadata_popup = None
        self.current_color_mode = None  # può valere 'rgb', 'ycbcr', 'hsv'
        self.custom_mode_active = False


        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="top", fill="x", pady=5)


        self.load_button = tk.Button(self.button_frame, text="📂 Carica immagine PNG", command=self.load_image)
        self.load_button.pack(side="left", padx=10)

        self.reset_button = tk.Button(self.button_frame, text="🔄 Nuova immagine", command=self.reset_session)
        self.reset_button.pack_forget()


        self.metadata_label = tk.Label(self.root, text="", font=("Arial", 11), justify="left")
        self.metadata_label.pack_forget()

        self.details_button = tk.Button(self.button_frame, text="ℹ️ Dettagli")
        self.details_button.pack_forget()
        self.details_button.bind("<Enter>", self.show_metadata_hover)
        self.details_button.bind("<Leave>", self.hide_metadata_hover)

        self.rgb_split_button = tk.Button(self.button_frame, text="🔴 Mostra R, G, B", command=self.toggle_rgb)
        self.rgb_split_button.pack_forget()

        self.ycbcr_split_button = tk.Button(self.button_frame, text="🔍 Mostra Y, Cb, Cr", command=self.show_ycbcr_channels)
        self.ycbcr_split_button.pack_forget()

        self.hsv_split_button = tk.Button(self.button_frame, text="🌈 Mostra H, S, V", command=self.toggle_hsv)
        self.hsv_split_button.pack_forget()

        self.custom_button = tk.Button(self.button_frame, text="📊 Custom", command=self.toggle_custom_view)
        self.custom_button.pack_forget()

        self.separate_var = tk.BooleanVar(value=False)




        self.image_panel = tk.Label(self.root)
        self.image_panel.pack(pady=10)

        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(expand=True, fill='both')

    def reset_session(self):
        self.controller.reset_image()
        self.image_panel.config(image="")
        self.image_panel.image = None
        self.metadata_label.config(text="")

        self.clear_all_canvases()

        self.reset_button.pack_forget()
        self.load_button.pack(side="left", padx=10)

        self.rgb_split_button.pack_forget()
        self.ycbcr_split_button.pack_forget()
        self.hsv_split_button.pack_forget()
        self.details_button.pack_forget()
        self.metadata_label.pack_forget()
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not filepath:
            return

        success = self.controller.load_image(filepath)
        if not success:
            messagebox.showerror("Errore", "Impossibile caricare l'immagine.")
            return

        self.update_image_display()
        self.update_metadata_display()

        # Riporta in primo piano l'immagine principale se era stata nascosta
        self.image_panel.pack(pady=10)

        self.load_button.pack_forget()
        self.reset_button.pack(side="right", padx=10)
        self.details_button.pack(side="left", padx=10)
        self.rgb_split_button.pack(side="left", padx=10)
        self.ycbcr_split_button.pack(side="left", padx=10)
        self.hsv_split_button.pack(side="left", padx=10)

        self.current_color_mode = None
        self.custom_button.place_forget()
        self.custom_mode_active = False




    def update_image_display(self):
        image = self.controller.get_current_image()
        if image is None:
            return
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
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

    def show_metadata_hover(self, event):
        if not self.controller.is_image_loaded():
            return

        if self.metadata_popup:
            self.metadata_popup.destroy()

        self.metadata_popup = tk.Toplevel(self.root)
        self.metadata_popup.wm_overrideredirect(True)
        self.metadata_popup.configure(bg="white")

        x = self.details_button.winfo_rootx() + 50
        y = self.details_button.winfo_rooty() + 30
        self.metadata_popup.wm_geometry(f"300x100+{x}+{y}")

        label = tk.Label(self.metadata_popup, text=self.metadata_label.cget("text"), bg="white",
                         justify="left", font=("Arial", 10), anchor="nw")
        label.pack(fill="both", expand=True, padx=10, pady=10)

    def hide_metadata_hover(self, event):
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None

    def clear_all_canvases(self):
        if self.ycbcr_canvas:
            self.ycbcr_canvas.get_tk_widget().destroy()
            self.ycbcr_canvas = None
        if self.hsv_canvas:
            self.hsv_canvas.get_tk_widget().destroy()
            self.hsv_canvas = None
        if self.rgb_canvas:
            self.rgb_canvas.get_tk_widget().destroy()
            self.rgb_canvas = None

    def show_ycbcr_channels(self):
        try:
            self.clear_all_canvases()
            from matplotlib.figure import Figure

            image = self.controller.get_current_image()
            ycbcr = self.controller.model.get_ycbcr_channels()
            Y, Cb, Cr = ycbcr[:, :, 0], ycbcr[:, :, 1], ycbcr[:, :, 2]

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.image_panel.config(image="")
            self.image_panel.image = None

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            dpi = 100
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

            axs[0].imshow(image_rgb)
            axs[0].set_title("Immagine RGB originale")
            axs[0].axis("off")

            axs[1].imshow(Y, cmap='gray')
            axs[1].set_title("Y (Luminanza)")

            axs[2].imshow(Cb, cmap='gray')
            axs[2].set_title("Cb vs Y (Blu‑diff)")

            axs[3].imshow(Cr, cmap='gray')
            axs[3].set_title("Cr vs Y (Rosso‑diff)")

            for ax in axs[1:]:
                ax.axis("off")

            fig.tight_layout()

            self.ycbcr_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
            self.ycbcr_canvas.draw()
            self.ycbcr_canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)

            self.current_color_mode = 'ycbcr'
            self.custom_mode_active = False
            self.custom_button.pack(side="left", padx=10)



        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def toggle_hsv(self):
        if not self.controller.is_image_loaded():
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()

        if self.hsv_canvas:
            self.hsv_canvas.get_tk_widget().destroy()
            self.hsv_canvas = None
            self.image_panel.pack(pady=10)
            return

        fig = self.controller.get_hsv_figure(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.hsv_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
        self.hsv_canvas.draw()
        self.hsv_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_rgb(self):
        if not self.controller.is_image_loaded():
            return

        # Pulisce qualsiasi visualizzazione attiva
        self.clear_all_canvases()
        self.image_panel.pack_forget()

        # BLOCCO 1 – Se è attiva la visualizzazione RGB, la disattiva
        if self.rgb_canvas:
            self.rgb_canvas.get_tk_widget().destroy()
            self.rgb_canvas = None
            self.image_panel.pack(pady=10)
            self.custom_button.pack_forget()
            self.current_color_mode = None
            return

        # BLOCCO 2 – Attiva la visualizzazione RGB
        fig = self.controller.get_rgb_figure(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.rgb_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
        self.rgb_canvas.draw()
        self.rgb_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Mostra i controlli custom (visibili solo per RGB)
        self.custom_button.pack(side="left", padx=10)

        # Aggiorna stato interno
        self.current_color_mode = 'rgb'
        self.custom_mode_active = False

    def toggle_custom_view(self):
        if not self.controller.is_image_loaded():
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()

        # Caso: RGB
        if self.current_color_mode == 'rgb':
            fig = self.controller.get_rgb_histogram_figure(
                self.root.winfo_screenwidth(),
                self.root.winfo_screenheight()
            )
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.rgb_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
            self.rgb_canvas.draw()
            self.rgb_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.custom_mode_active = True

        # Caso: YCbCr
        elif self.current_color_mode == 'ycbcr':
            fig = self.controller.get_ycbcr_subsampling_figure(
                self.root.winfo_screenwidth(),
                self.root.winfo_screenheight()
            )
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.ycbcr_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
            self.ycbcr_canvas.draw()
            self.ycbcr_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.custom_mode_active = True

        # Se cliccato di nuovo, ripristina la vista base del colore attivo
        else:
            self.custom_mode_active = False
            if self.current_color_mode == 'rgb':
                self.toggle_rgb()
            elif self.current_color_mode == 'ycbcr':
                self.show_ycbcr_channels()


