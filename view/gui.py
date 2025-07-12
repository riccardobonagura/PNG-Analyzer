# ========================================================
# TABELLA DELLE FIRME DEI METODI DI AppView
#
#
# __init__(self, root: tk.Tk, controller):
#     Inizializza la finestra principale, imposta il layout e collega il controller.
#
# _setup_layout(self):
#     Imposta la struttura base della finestra e crea i widget principali.
#
# clear_all_canvases(self):
#     Rimuove e distrugge tutti i canvas di visualizzazione esistenti, resettando i riferimenti.
#
# reset_session(self):
#     Ripristina lo stato iniziale della GUI: cancella canvas, resetta pulsanti, immagine e metadati.
#
# _hide_all_buttons(self):
#     Nasconde tutti i pulsanti della toolbar.
#
# _pack_buttons(self, mode: str):
#     Organizza la visualizzazione dei pulsanti in base alla modalità corrente.
#
# load_image(self):
#     Apre una finestra di dialogo per caricare un file PNG, aggiorna vista e metadati.
#
# show_full_image(self):
#     Ripristina e mostra l’immagine originale a pieno schermo, aggiorna metadati e pulsanti.
#
# update_image_display(self):
#     Aggiorna l’immagine corrente nella GUI ridimensionandola e convertendola in PhotoImage.
#
# update_metadata_display(self):
#     Legge e mostra filepath, risoluzione, canali e spazio colore nei metadati.
#
# show_metadata_hover(self, _):
#     Mostra un popup flottante con i metadati quando si passa il mouse sul pulsante “Dettagli”.
#
# hide_metadata_hover(self, _):
#     Nasconde il popup dei metadati se presente.
#
# _toggle_canvas(self, canvas_attr: str, fig_builder, mode_on: str,
#                    mode_off: str = None, buttons_mode: str = None, error_msg: str = None):
#     Logica comune per mostrare/nascondere un canvas matplotlib (RGB, YCbCr, HSV).
#
# toggle_rgb(self):
#     Attiva o disattiva la visualizzazione dei canali RGB.
#
# toggle_ycbcr(self):
#     Attiva o disattiva la visualizzazione dei canali YCbCr.
#
# toggle_hsv(self):
#     Attiva o disattiva la visualizzazione dei canali HSV.
#
# toggle_custom_view(self):
#     Attiva la vista avanzata (istogrammi o scatter) per il canale attivo.
#
# on_jpeg_clicked(self):
#     Handler per “Converti in JPEG”: apre popup compressione, converte e salva.
#
# show_jpeg_ready_popup(self, filepath: str):
#     Mostra un popup che conferma l’avvenuto salvataggio del JPEG.
#
# on_directionality_clicked(self):
#     Handler per “Direzionalità Tamura”: calcola e mostra istogramma polare e valore scalare.
#
# on_contrast_clicked(self):
#     Handler per “Contrasto Tamura”: calcola e mostra mappa di contrasto e valore scalare.
#
# on_granularity_clicked(self):
#     Handler per “Granularità Tamura”: calcola e mostra overlay dei granuli e valore scalare.
# ========================================================

# ========================================================
# 1. IMPORT NECESSARI
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
# ========================================================

# ========================================================
# 2. DEFINIZIONE DELLA CLASSE AppView
class AppView:
    TITLE = "PNG Analyzer - GUI"
    BUTTON_LOAD_TEXT = "Carica immagine PNG"
    BUTTON_RESET_TEXT = "Azzera"
    BUTTON_DETAILS_TEXT = "Dettagli"
    BUTTON_RGB_TEXT = "Mostra canali R, G, B"
    BUTTON_YCBCR_TEXT = "Mostra canali Y, Cb, Cr"
    BUTTON_HSV_TEXT = "Mostra canali H, S, V"
    BUTTON_CUSTOM_TEXT = "Vista avanzata"
    BUTTON_JPEG_TEXT = "Converti in JPEG"
    BUTTON_DIRECTIONALITY_TEXT = "Direzionalità"
    BUTTON_CONTRAST_TEXT = "Contrasto"
    BUTTON_GRANULARITY_TEXT = "Granularità"

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

    def __init__(self, root: tk.Tk, controller):
        """
        Inizializza la finestra principale, imposta layout e collega il controller.
        Args:
            root (tk.Tk): istanza principale di Tkinter.
            controller (AppController): controller dell'applicazione.
        """
        self.root = root
        self.controller = controller
        self.root.title(self.TITLE)

        # Gestione finestra cross-platform
        if sys.platform.startswith('win'):
            self.root.state("zoomed")
        else:
            try:
                self.root.attributes("-zoomed", True)
            except Exception: # catch-all
                self.root.attributes("-fullscreen", True)

        self.current_color_mode = None  # 'rgb', 'ycbcr', 'hsv'
        self.custom_mode_active = False
        self.metadata_popup = None

        self.rgb_canvas = None
        self.ycbcr_canvas = None
        self.hsv_canvas = None

        self.directionality_canvas = None
        self.contrast_canvas = None
        self.granularity_canvas = None
        self.hsv_custom_canvas = None

        self._setup_layout()

    def _setup_layout(self):
        """Imposta la struttura base della finestra e i widget principali."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="top", fill="x", pady=5)

        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(expand=True, fill='both')

        self.image_panel = tk.Label(self.display_frame)
        self.image_panel.pack(expand=True, fill="both")

        self.metadata_label = tk.Label(self.root, font=self.METADATA_FONT, justify="left")
        self.metadata_label.pack_forget()

        # Pulsanti principali
        self.jpeg_button = tk.Button(self.button_frame, text=self.BUTTON_JPEG_TEXT, command=self.on_jpeg_clicked)
        self.directionality_button = tk.Button(self.button_frame, text=self.BUTTON_DIRECTIONALITY_TEXT, command=self.on_directionality_clicked)
        self.contrast_button = tk.Button(self.button_frame, text="Contrasto", command=self.on_contrast_clicked)
        self.granularity_button = tk.Button(self.button_frame, text="Granularità", command=self.on_granularity_clicked)
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
        self.jpeg_button.pack_forget()
        self.directionality_button.pack_forget()
        self.contrast_button.pack_forget()
        self.granularity_button.pack_forget()

        self.details_button.bind("<Enter>", self.show_metadata_hover)
        self.details_button.bind("<Leave>", self.hide_metadata_hover)
    # ========================================================
    # 3. METODI DI CONTROLLO DELLA VISUALIZZAZIONE E SESSIONE

    def clear_all_canvases(self):
        """
        Rimuove e distrugge tutte le canvas di visualizzazione attualmente presenti.
        Reset delle variabili di riferimento.
        """
        for canvas in [self.rgb_canvas, self.ycbcr_canvas, self.hsv_canvas,
                       getattr(self, "hsv_custom_canvas", None),
                       getattr(self, "directionality_canvas", None),
                       getattr(self, "contrast_canvas", None),
                       getattr(self, "granularity_canvas", None)]:
            if canvas:
                canvas.get_tk_widget().destroy()

        self.rgb_canvas = self.ycbcr_canvas = self.hsv_canvas = None
        self.directionality_canvas = self.contrast_canvas = self.granularity_canvas = None
        if hasattr(self, "hsv_custom_canvas"):
            self.hsv_custom_canvas = None

    def reset_session(self):
        """
        Ripristina la sessione grafica e lo stato ai valori iniziali.
        Reset dell'immagine, dei canvas, dei metadati e dei pulsanti.
        """
        self.controller.reset_image()

        # Rimuove canvas matplotlib e widget dinamici
        self.clear_all_canvases()

        # Rimuove tutti i figli dal frame di visualizzazione
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Ripristina sfondo originale
        self.display_frame.configure(bg="white")  # oppure il colore di default originale

        # Ricrea image_panel con sfondo bianco
        self.image_panel = tk.Label(self.display_frame, bg="white")
        self.image_panel.pack(expand=True, fill="both")
        self.image_panel.config(image="")
        self.image_panel.image = None

        # Reset metadati
        self.metadata_label.config(text="")

        # Reset pulsanti e stato
        self._hide_all_buttons()
        self._pack_buttons(mode='initial')
        self.custom_mode_active = False
        self.current_color_mode = None

        # Chiude popup metadati se aperto
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None

    def _hide_all_buttons(self):
        """
        Nasconde tutti i pulsanti della toolbar.
        """
        for button in [
            self.jpeg_button, self.directionality_button, self.contrast_button, self.granularity_button,
            self.load_button, self.reset_button, self.details_button,
            self.rgb_split_button, self.ycbcr_split_button,
            self.hsv_split_button, self.custom_button
        ]:
            button.pack_forget()

    def _pack_buttons(self, mode: str):
        """
        Gestisce la visualizzazione dei pulsanti in base allo stato/modalità corrente.
        Args:
            mode (str): Modalità di visualizzazione, determina quali pulsanti sono visibili.
        """
        self._hide_all_buttons()
        if mode == 'initial':
            self.load_button.pack(side="left", padx=10)
        elif mode in ('image_loaded', 'ycbcr', 'rgb', 'hsv', 'custom_rgb', 'custom_ycbcr'):
            self.details_button.pack(side="left", padx=10)
            self.rgb_split_button.pack(side="left", padx=10)
            self.ycbcr_split_button.pack(side="left", padx=10)
            self.hsv_split_button.pack(side="left", padx=10)
            if mode not in ('image_loaded',):
                self.custom_button.pack(side="left", padx=10)
            self.reset_button.pack(side="right", padx=10)
            self.jpeg_button.pack(side="right", padx=10)
            self.directionality_button.pack(side="right", padx=10)
            self.contrast_button.pack(side="right", padx=10)
            self.granularity_button.pack(side="right", padx=10)
    # ========================================================
    # 4. METODI DI GESTIONE IMMAGINE E METADATI

    def load_image(self):
        """
        Gestisce il caricamento dell'immagine PNG tramite file dialog.
        Aggiorna la visualizzazione e i metadati dopo il caricamento.
        """
        #debug
        print("== load_image chiamato ==")


        filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])

        #debug
        print(f"[DEBUG] Filepath selezionato: {filepath}")

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
        """
        Visualizza l'immagine completa e aggiorna la visualizzazione e i metadati.
        Funziona anche dopo l'uso di Direzionalità / Contrasto / Granularità.
        """
        if not self.controller.is_image_loaded():
            return

        # Pulisce tutti i grafici (inclusi quelli da contrasto, granularità, ecc.)
        self.clear_all_canvases()

        # Rimuove eventuali frame aggiuntivi nella display_frame
        for widget in self.display_frame.winfo_children():
            if widget != self.image_panel:
                widget.destroy()

        # Mostra nuovamente l'image_panel con l'immagine aggiornata
        self.image_panel.pack(expand=True, fill="both")
        self.update_image_display()
        self.update_metadata_display()

        self.current_color_mode = None
        self.custom_mode_active = False
        self._pack_buttons(mode='image_loaded')

    def update_image_display(self):
        """
        Aggiorna la visualizzazione dell'immagine corrente nella GUI.
        """
        image = self.controller.get_current_image()
        if image is None:
            return
        image_rgb = self.controller.bgr_to_rgb(image)
        image_pil = Image.fromarray(image_rgb)
        frame_width = int(self.display_frame.winfo_width() * self.IMAGE_MARGIN_FACTOR)
        frame_height = int(self.display_frame.winfo_height() * self.IMAGE_MARGIN_FACTOR)
        if frame_width < 100 or frame_height < 100:
            frame_width, frame_height = int(self.DEFAULT_IMAGE_SIZE[0] * self.IMAGE_MARGIN_FACTOR), int(
                self.DEFAULT_IMAGE_SIZE[1] * self.IMAGE_MARGIN_FACTOR)
        image_pil.thumbnail((frame_width, frame_height))
        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_panel.configure(image=image_tk)
        self.image_panel.image = image_tk

    def update_metadata_display(self):
        """
        Aggiorna la visualizzazione dei metadati dell'immagine (filepath, risoluzione, canali, spazio colore).
        """
        resolution = self.controller.get_image_resolution()
        channels = self.controller.get_image_channels()
        color_space = self.controller.get_color_space()
        filepath = self.controller.get_filepath()
        text = (
            f"File: {filepath}\n"
            f"Risoluzione: {resolution[0]} × {resolution[1]}\n"
            f"Canali: {channels}\n"
            f"Spazio colore: {color_space}"
        )
        self.metadata_label.config(text=text)

    def show_metadata_hover(self, _):
        """
        Visualizza un popup con i metadati dell'immagine quando si passa sopra il pulsante dettagli.
        """
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
        label = tk.Label(
            self.metadata_popup,
            text=self.metadata_label.cget("text"),
            bg="white",
            justify="left",
            font=self.METADATA_HOVER_FONT,
            anchor="nw"
        )
        label.pack(fill="both", expand=True, padx=10, pady=10)

    def hide_metadata_hover(self, _):
        """
        Nasconde il popup dei metadati se presente.
        """
        if self.metadata_popup:
            self.metadata_popup.destroy()
            self.metadata_popup = None
    # ========================================================
    # 5. METODI DI VISUALIZZAZIONE DEI CANALI E VISTE CUSTOM

    def _toggle_canvas(self, canvas_attr: str, fig_builder, mode_on: str, mode_off: str = None,
                       buttons_mode: str = None, error_msg: str = None):
        """
        Gestisce la logica di visualizzazione e scomparsa di una canvas associata a uno specifico canale o vista.
        Args:
            canvas_attr (str): nome dell'attributo canvas da gestire.
            fig_builder (callable): funzione che costruisce la figura matplotlib.
            mode_on (str): modalità attiva dopo visualizzazione.
            mode_off (str, opzionale): modalità dopo chiusura canvas.
            buttons_mode (str, opzionale): modalità per i pulsanti.
            error_msg (str, opzionale): messaggio di errore da mostrare.
        """
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
        """
        Visualizza o nasconde la canvas dei canali RGB.
        """
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
        """
        Visualizza o nasconde la canvas dei canali YCbCr.
        """
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
        """
        Visualizza o nasconde la canvas dei canali HSV.
        """
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
        """
        Visualizza la vista avanzata (custom) a seconda della modalità corrente.
        """
        if self.custom_mode_active or not self.controller.is_image_loaded():
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()
        self.custom_mode_active = True

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        try:
            if self.current_color_mode == 'rgb':
                fig = self.controller.get_rgb_histogram_figure(screen_width, screen_height)
                self.rgb_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.rgb_canvas.draw()
                self.rgb_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self._pack_buttons(mode='custom_rgb')

            elif self.current_color_mode == 'ycbcr':
                fig = self.controller.get_ycbcr_subsampling_figure(screen_width, screen_height)
                self.ycbcr_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.ycbcr_canvas.draw()
                self.ycbcr_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self._pack_buttons(mode='custom_ycbcr')

            elif self.current_color_mode == 'hsv':
                fig = self.controller.get_hsv_scatter_comparison_figure(screen_width, screen_height)
                self.hsv_custom_canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
                self.hsv_custom_canvas.draw()
                self.hsv_custom_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self._pack_buttons(mode='hsv')

            else:
                # Se nessun canale attivo, torna alla vista principale
                self.custom_mode_active = False
                if self.current_color_mode == 'rgb':
                    self.toggle_rgb()
                elif self.current_color_mode == 'ycbcr':
                    self.toggle_ycbcr()
                elif self.current_color_mode == 'hsv':
                    self.toggle_hsv()

        except Exception as e:
            self.custom_mode_active = False
            messagebox.showerror(self.MSGBOX_LOAD_ERROR, self.MSGBOX_CUSTOM_ERROR_TEXT.format(str(e)))

    def on_jpeg_clicked(self):
        """
        Handler per il bottone 'Converti in JPEG'.
        Mostra popup per selezione livello di compressione, converte e salva il file JPEG.
        """
        if not self.controller.is_image_loaded():
            messagebox.showerror("Errore", "Carica prima un'immagine PNG.")
            return

        # 1. Finestra popup per selezione compressione
        popup = Toplevel(self.root)
        popup.title("Livello di compressione JPEG")
        popup.geometry("+%d+%d" % (
            self.root.winfo_rootx() + int(self.root.winfo_width() / 2) - 150,
            self.root.winfo_rooty() + int(self.root.winfo_height() / 2) - 75
        ))
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)

        label = tk.Label(popup, text="Scegli livello di compressione JPEG:", font=("Arial", 12))
        label.pack(pady=(15, 5))

        compression_var = tk.StringVar(value="med")
        options = [
            ("Bassa (alta qualità)", "low"),
            ("Media (standard)", "med"),
            ("Alta (molto choppy)", "high"),
        ]
        for text, val in options:
            tk.Radiobutton(popup, text=text, variable=compression_var, value=val, font=("Arial", 11)).pack(
                anchor="w", padx=40)

        def conferma():
            popup.destroy()

            image = self.controller.get_current_image()
            if image is None:
                messagebox.showerror("Errore", "Nessuna immagine caricata.")
                return

            # Conversione BGR → RGB
            import cv2
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            jpeg_bytes = self.controller.convert_image_to_jpeg(
                compression_level=compression_var.get()
            )
            if jpeg_bytes is None:
                messagebox.showerror("Errore", "Errore durante la conversione JPEG.")
                return

            # Dialog salvataggio
            filepath = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if not filepath:
                return

            try:
                with open(filepath, "wb") as f:
                    f.write(jpeg_bytes)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio JPEG:\n{e}")
                return

            self.show_jpeg_ready_popup(filepath)

        ok_btn = tk.Button(popup, text="Converti", command=conferma, font=("Arial", 11), width=12)
        ok_btn.pack(pady=(10, 20))

        popup.update_idletasks()
        popup.lift()
        popup.focus_force()
    def show_jpeg_ready_popup(self, filepath: str):
        """
        Mostra un popup centrato che conferma il salvataggio del file JPEG.
        """
        popup = Toplevel(self.root)
        popup.title("JPEG pronto")
        popup.geometry("+%d+%d" % (
            self.root.winfo_rootx() + int(self.root.winfo_width() / 2) - 150,
            self.root.winfo_rooty() + int(self.root.winfo_height() / 2) - 75
        ))
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)

        msg = tk.Label(
            popup,
            text="La conversione in formato JPEG\nè stata salvata correttamente.",
            font=("Arial", 13)
        )
        msg.pack(pady=(20, 10))

        ok_button = tk.Button(popup, text="OK", font=("Arial", 11), width=10, command=popup.destroy)
        ok_button.pack(pady=(0, 20))

        popup.update_idletasks()
        popup.lift()
        popup.focus_force()

    def on_directionality_clicked(self):
        """
        Handler per il bottone 'Direzionalità Tamura'.
        Visualizza immagine originale, istogramma polare e valore scalare.
        """
        if not self.controller.is_image_loaded():
            messagebox.showerror("Errore", "Carica prima un'immagine PNG.")
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        directionality_value, polar_fig = self.controller.process_image_directionality(
            screen_width, screen_height
        )

        # Mostra immagine nella image_panel standard
        self.update_image_display()
        self.image_panel.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        # Mostra istogramma polare a destra
        right_frame = tk.Frame(self.display_frame)
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        self.directionality_canvas = FigureCanvasTkAgg(polar_fig, master=right_frame)
        self.directionality_canvas.draw()
        self.directionality_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.current_color_mode = None
        self.custom_mode_active = False
        self._pack_buttons(mode='image_loaded')

    def on_contrast_clicked(self):
        """
        Handler per il bottone 'Contrasto Tamura'.
        Mostra l'immagine originale a sinistra tramite self.image_panel,
        mappa di contrasto a destra, valore scalare sotto.
        """
        if not self.controller.is_image_loaded():
            messagebox.showerror("Errore", "Carica prima un'immagine PNG.")
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()

        img = self.controller.get_current_image()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        contrast_value, fig_contrast = self.controller.process_image_contrast(screen_width, screen_height)

        # Aggiorna immagine nel pannello esistente
        image_rgb = self.controller.bgr_to_rgb(img)
        image_pil = Image.fromarray(image_rgb)
        frame_width = int(self.display_frame.winfo_width() * self.IMAGE_MARGIN_FACTOR)
        frame_height = int(self.display_frame.winfo_height() * self.IMAGE_MARGIN_FACTOR)
        image_pil.thumbnail((frame_width, frame_height))
        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_panel.configure(image=image_tk)
        self.image_panel.image = image_tk
        self.image_panel.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        # Mappa contrasto a destra
        right_frame = tk.Frame(self.display_frame)
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        self.contrast_canvas = FigureCanvasTkAgg(fig_contrast, master=right_frame)
        self.contrast_canvas.draw()
        self.contrast_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.current_color_mode = None
        self.custom_mode_active = False
        self._pack_buttons(mode='image_loaded')

    def on_granularity_clicked(self):
        """
        Handler per il bottone 'Granularità Tamura'.
        Mostra immagine originale con overlay dei granuli e valore scalare.
        """
        if not self.controller.is_image_loaded():
            messagebox.showerror("Errore", "Carica prima un'immagine PNG.")
            return

        self.clear_all_canvases()
        self.image_panel.pack_forget()

        img = self.controller.get_current_image()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        granularity_value, fig_granules = self.controller.process_image_granularity(screen_width, screen_height)

        # Aggiorna immagine nel pannello esistente
        img_rgb = self.controller.bgr_to_rgb(img)
        img_pil = Image.fromarray(img_rgb)
        frame_width = int(self.display_frame.winfo_width() * self.IMAGE_MARGIN_FACTOR)
        frame_height = int(self.display_frame.winfo_height() * self.IMAGE_MARGIN_FACTOR)
        img_pil.thumbnail((frame_width, frame_height))
        img_tk = ImageTk.PhotoImage(img_pil)
        self.image_panel.configure(image=img_tk)
        self.image_panel.image = img_tk
        self.image_panel.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        # Canvas con mappa granularità
        right_frame = tk.Frame(self.display_frame)
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        self.granularity_canvas = FigureCanvasTkAgg(fig_granules, master=right_frame)
        self.granularity_canvas.draw()
        self.granularity_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.current_color_mode = None
        self.custom_mode_active = False
        self._pack_buttons(mode='image_loaded')
