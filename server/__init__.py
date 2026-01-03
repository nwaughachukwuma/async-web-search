from dotenv import load_dotenv

load_dotenv()

from .server import app

__all__ = ["app"]
