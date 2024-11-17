import sys
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.resolve()
sys.path.append(str(project_root))

load_dotenv(dotenv_path="./env.local")
