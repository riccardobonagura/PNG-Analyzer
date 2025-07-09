import tkinter as tk
from controller.app_controller import AppController
from view.gui import AppView

if __name__ == "__main__":
    root = tk.Tk()
    controller = AppController()
    app = AppView(root, controller)
    root.mainloop()