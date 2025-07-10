import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppView:
    TITLE = "PNG Analyzer - GUI"
    BUTTON_LOAD_TEXT = "📂 Carica immagine PNG"
    BUTTON_RESET_TEXT = "🔄 Nuova immagine"
    BUTTON_DETAILS_TEXT = "ℹ️ Dettagli"
    BUTTON_RGB_TEXT = "🔴 Mostra R, G, B"
    BUTTON_YCBCR_TEXT = "🔍 Mostra Y, Cb, Cr"
    BUTTON_HSV_TEXT = "🌈 Mostra H, S, V"
    BUTTON_CUSTOM_TEXT = "📊 Custom"

    MSGBOX_LOAD_ERROR = "Errore"
    MSGBOX_LOAD_ERROR_TEXT = "Impossibile caricare l'immagine."
    MSGBOX_YCBCR_ERROR_TEXT = "Errore nella visualizzazione dei canali YCbCr:\n{}"
    MSGBOX_RGB_ERROR_TEXT = "Errore nella visualizzazione RGB:\n{}"
    MSGBOX_HSV_ERROR_TEXT = "Errore nella visualizzazione HSV:\n{}"
    MSGBOX_CUSTOM_ERROR_TEXT = "Errore nella visualizzazione custom:\n{}"

    METADATA_FONT = ("Arial", 11)
    METADATA_HOVER_FONT = ("Arial", 10)

    DEFAULT_IMAGE_SIZE = (800, 500)
    IMAGE_MARGIN_FACTOR = 0.9

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title(self.TITLE)
        self.root.state("zoomed")

        self.current_color_mode = None  # 'rgb', 'ycbcr', 'hsv'
        self.custom_mode_active = False
        self.metadata_popup = None

        self.rgb_canvas = None
        self.ycbcr_canvas = None
        self.hsv_canvas = None

        self._setup_layout()

    def _setup_layout(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="top", fill="x", pady=5)

        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(expand=True, fill='both')

        self.image_panel = tk.Label(self.display_frame)
        self.image_panel.pack(expand=True, fill="both")

        self.metadata_label = tk.Label(self.root, font=self.METADATA_FONT, justify="left")
        self.metadata_label.pack_forget()

        self.load_button = tk.Button(self.button_frame, text=self.BUTTON_LOAD_TEXT, command=self.load_image)
        self.reset_button = tk.Button(self.button_frame, text=self.BUTTON_RESET_TEXT, command=self.reset_session)
        self.details_button = tk.Button(self.button_frame, text=self.BUTTON_DETAILS_TEXT, command=self.show_full_image)
        self.rgb_split_button = tk.Button(self.button_frame, text=self.BUTTON_RGB_TEXT, command=self.toggle_rgb)
        self.ycbcr_split_button = tk.Button(self.button_frame, text=self.BUTTON_YCBCR_TEXT, command=self.toggle_ycbcr)
        self.hsv_split_button = tk.Button(self.button_frame, text=self.BUTTON_HSV_TEXT, command=self.toggle_hsv)
        self.custom_button = tk.Button(self.button_frame, text=self.BUTTON_CUSTOM_TEXT, command=self.toggle_custom_view)

        self.load_button.pack(side="left", padx=10)
        self.reset_button.pack_forget()
        self.details_button.pack_forget()
        self.rgb_split_button.pack_forget()
        self.ycbcr_split_button.pack_forget()
        self.hsv_split_button.pack_forget()
        self.custom_button.pack_forget()

        self.details_button.bind("<Enter>", self.show_metadata_hover)
        self.details_button.bind("<Leave>", self.hide_metadata_hover)

    def clear_all_canvases(self):
        for canvas in [self.rgb_canvas, self.ycbcr_canvas, self.hsv_canvas, getattr(self, "hsv_custom_canvas", None)]:
            if canvas:
                canvas.get_tk_widget().destroy()
        self.rgb_canvas = self.ycbcr_canvas = self.hsv_canvas = None
        if hasattr(self, "hsv_custom_canvas"):
            self.hsv_custom_canvas = None

    def reset_session(self):
        self.controller.reset_image()
        self.clear_all_canvases()
        self.image_panel.pack(expand=True, fill="both")
        self.image_panel.config(image="")
        self.image_panel.image = None
        self.metadata_label.config(text="")
        self._hide_all_buttons()
        self._pack_buttons(mode='initial')
        self.custom_mode_active = False
        self.current_color_mode = None
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None

    def _hide_all_buttons(self):
        for button in [self.load_button, self.reset_button, self.details_button,
                       self.rgb_split_button, self.ycbcr_split_button,
                       self.hsv_split_button, self.custom_button]:
            button.pack_forget()

    def _pack_buttons(self, mode):
        self._hide_all_buttons()
        if mode == 'initial':
            self.load_button.pack(side="left", padx=10)
        elif mode == 'image_loaded':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
        elif mode == 'ycbcr':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            self.custom_button.pack(side="left", padx=10)
        elif mode == 'rgb':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            self.custom_button.pack(side="left", padx=10)
        elif mode == 'hsv':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            self.custom_button.pack(side="left", padx=10)
        elif mode == 'custom_rgb':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            self.custom_button.pack(side="left", padx=10)
        elif mode == 'custom_ycbcr':
            self.reset_button.pack(side="right", padx=10)
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            self.custom_button.pack(side="left", padx=10)

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not filepath:
            return

        if not self.controller.load_image(filepath):
            messagebox.showerror(self.MSGBOX_LOAD_ERROR, self.MSGBOX_LOAD_ERROR_TEXT)
            return

        self.clear_all_canvases()
        self.image_panel.pack(expand=True, fill="both")
        self.update_image_display()
        self.update_metadata_display()

        self._pack_buttons(mode='image_loaded')

        self.current_color_mode = None
        self.custom_mode_active = False

    def show_full_image(self):
        if not self.controller.is_image_loaded():
            return
        if self.current_color_mode is None and not self.custom_mode_active:
            return
        self.clear_all_canvases()
        self.image_panel.pack(expand=True, fill="both")
        self.update_image_display()
        self.update_metadata_display()
        self.current_color_mode = None
        self.custom_mode_active = False
        self._pack_buttons(mode='image_loaded')

    def update_image_display(self):
        image = self.controller.get_current_image()
        if image is None:
            return
        image_rgb = self.controller.bgr_to_rgb(image)
        image_pil = Image.fromarray(image_rgb)
        frame_width = int(self.display_frame.winfo_width() * self.IMAGE_MARGIN_FACTOR)
        frame_height = int(self.display_frame.winfo_height() * self.IMAGE_MARGIN_FACTOR)
        if frame_width < 100 or frame_height < 100:
            frame_width, frame_height = int(self.DEFAULT_IMAGE_SIZE[0] * self.IMAGE_MARGIN_FACTOR), int(self.DEFAULT_IMAGE_SIZE[1] * self.IMAGE_MARGIN_FACTOR)
        image_pil.thumbnail((frame_width, frame_height))
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

    def show_metadata_hover(self, _):
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
                         justify="left", font=self.METADATA_HOVER_FONT, anchor="nw")
        label.pack(fill="both", expand=True, padx=10, pady=10)

    def hide_metadata_hover(self, _):
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None

    def _toggle_canvas(self, canvas_attr, fig_builder, mode_on, mode_off=None, buttons_mode=None, error_msg=None):
        if not self.controller.is_image_loaded():
            return
        self.clear_all_canvases()
        self.image_panel.pack_forget()
        canvas = getattr(self, canvas_attr)
        if canvas:
            canvas.get_tk_widget().destroy()
            setattr(self, canvas_attr, None)
            self.image_panel.pack(expand=True, fill="both")
            self._pack_buttons(mode=mode_off or 'image_loaded')
            self.current_color_mode = None
            return
        try:
            fig = fig_builder()
            new_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
            new_canvas.draw()
            new_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            setattr(self, canvas_attr, new_canvas)
            self.current_color_mode = mode_on
            self.custom_mode_active = False
            if buttons_mode:
                self._pack_buttons(mode=buttons_mode)
        except Exception as e:
            messagebox.showerror(self.MSGBOX_LOAD_ERROR, error_msg.format(str(e)) if error_msg else str(e))

    def toggle_rgb(self):
        if self.current_color_mode == 'rgb' and not self.custom_mode_active:
            return
        def fig_builder():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            return self.controller.get_rgb_figure(screen_width, screen_height)
        self._toggle_canvas(
            canvas_attr='rgb_canvas',
            fig_builder=fig_builder,
            mode_on='rgb',
            buttons_mode='rgb',
            error_msg=self.MSGBOX_RGB_ERROR_TEXT,
        )

    def toggle_ycbcr(self):
        if self.current_color_mode == 'ycbcr' and not self.custom_mode_active:
            return
        def fig_builder():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            return self.controller.get_ycbcr_figure(screen_width, screen_height)
        self._toggle_canvas(
            canvas_attr='ycbcr_canvas',
            fig_builder=fig_builder,
            mode_on='ycbcr',
            buttons_mode='ycbcr',
            error_msg=self.MSGBOX_YCBCR_ERROR_TEXT,
        )

    def toggle_hsv(self):
        if self.current_color_mode == 'hsv' and not self.custom_mode_active:
            return
        def fig_builder():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            return self.controller.get_hsv_figure(screen_width, screen_height)
        self._toggle_canvas(
            canvas_attr='hsv_canvas',
            fig_builder=fig_builder,
            mode_on='hsv',
            buttons_mode='hsv',
            error_msg=self.MSGBOX_HSV_ERROR_TEXT,
        )

    def toggle_custom_view(self):
        if self.custom_mode_active:
            return
        if not self.controller.is_image_loaded():
            return

        self.clear_all_canvases()  # Rimuove TUTTI i canvas (incluso hsv_custom_canvas!)
        self.image_panel.pack_forget()  # Nasconde l'immagine di default

        try:
            if self.current_color_mode == 'rgb':
                fig = self.controller.get_rgb_histogram_figure(
                    self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                self.rgb_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.rgb_canvas.draw()
                self.rgb_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.custom_mode_active = True
                self._pack_buttons(mode='custom_rgb')

            elif self.current_color_mode == 'ycbcr':
                fig = self.controller.get_ycbcr_subsampling_figure(
                    self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                self.ycbcr_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.ycbcr_canvas.draw()
                self.ycbcr_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.custom_mode_active = True
                self._pack_buttons(mode='custom_ycbcr')


            elif self.current_color_mode == 'hsv':
                print("custom su HSV: scatter plot")
                fig = self.controller.get_hsv_scatter_comparison_figure(
                    self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                self.hsv_custom_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.hsv_custom_canvas.draw()
                self.hsv_custom_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                print("Custom HSV canvas packed:", self.hsv_custom_canvas)
                self.display_frame.update_idletasks()  # Forza refresh
                self.custom_mode_active = True
                self._pack_buttons(mode='hsv')

            else:
                print("altro ramo")
                self.custom_mode_active = False
                if self.current_color_mode == 'rgb':
                    self.toggle_rgb()
                elif self.current_color_mode == 'ycbcr':
                    self.toggle_ycbcr()
                elif self.current_color_mode == 'hsv':
                    self.toggle_hsv()
        except Exception as e:
            messagebox.showerror(self.MSGBOX_LOAD_ERROR, self.MSGBOX_CUSTOM_ERROR_TEXT.format(str(e)))