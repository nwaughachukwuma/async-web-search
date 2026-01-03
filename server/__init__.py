from dotenv import load_dotenv

load_dotenv()

from .index import app

__all__ = ["app"]
