from dearlog import logger  # isort: split

from importlib.metadata import metadata

__meta__:   dict = metadata(__package__)
__about__:   str = __meta__["Summary"]
__author__:  str = __meta__["Author"]
__version__: str = __meta__["Version"]

from pathlib import Path

RESOURCES: Path = Path(__file__).parent/"resources"

from pianola.scene import PianolaScene
