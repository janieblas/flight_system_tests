import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))