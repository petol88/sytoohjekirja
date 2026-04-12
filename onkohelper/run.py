import sys
from pathlib import Path

# Ensure the current directory is in the path
sys.path.append(str(Path(__file__).resolve().parent))

from oncology_helper.main import MainApp

def main():
    try:
        app = MainApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nSovellus suljettiin käyttäjän toimesta.")
    except Exception as e:
        print(f"Odottamaton virhe sovelluksen suorituksessa: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
