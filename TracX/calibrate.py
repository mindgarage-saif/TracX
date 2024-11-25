import tkinter as tk

from .calibration import MRTCalibrationToolbox

# 'en' or 'de'
language = "en"


def main():
    root = tk.Tk()
    root.wait_visibility()
    root.grab_set()
    app = MRTCalibrationToolbox(root, language)
    root.mainloop()


if __name__ == "__main__":
    main()
