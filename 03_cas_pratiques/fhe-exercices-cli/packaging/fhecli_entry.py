"""Point d'entrée de l'exécutable autonome (PyInstaller)."""

import sys

from fhecli.cli import main

if __name__ == "__main__":
    sys.exit(main())
