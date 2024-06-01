from .app import create_app
from pathlib import Path
ROOT_DIR = Path().parent.resolve()
LOG_DIR = Path(ROOT_DIR,'logs')
# LOG_DIR = Path('/var','log','adservicepp')