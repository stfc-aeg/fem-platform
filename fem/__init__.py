
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fem")
except PackageNotFoundError:
    __version__ = "0+unknown"
