# ========================================================
# 1. IMPORT NECESSARI
import tkinter as tk
from controller.app_controller import AppController
from view.gui import AppView
# ========================================================

# ========================================================
# 2. ENTRY POINT PRINCIPALE
def main():
    """
    Entry point dell'applicazione.
    - Crea la finestra principale Tkinter.
    - Inizializza il controller dell'applicazione.
    - Inizializza la view (GUI) e collega il controller.
    - Avvia il mainloop di Tkinter.
    """
    root = tk.Tk()
    controller = AppController()
    app = AppView(root, controller)
    root.mainloop()
# ========================================================

# ========================================================
# 3. AVVIO DELL'APPLICAZIONE
if __name__ == "__main__":
    main()
# ========================================================