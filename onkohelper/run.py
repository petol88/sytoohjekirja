import sys
import os

# Ensure the current directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from oncology_helper.main import MainApp

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
