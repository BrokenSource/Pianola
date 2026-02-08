from dearlog import logger  # isort: split

from importlib.metadata import metadata

__meta__:   dict = metadata(__package__)
__about__:   str = __meta__["Summary"]
__author__:  str = __meta__["Author"]
__version__: str = __meta__["Version"]

from broken.project import BrokenProject

PIANOLA = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    ABOUT=__about__,
)

from pianola.scene import PianolaScene
