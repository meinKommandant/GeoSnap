import sys
from pathlib import Path

# Add src to path to ensure geosnap package is found
sys.path.append(str(Path(__file__).parent / "src"))

from geosnap.gui import main

if __name__ == "__main__":
    main()
