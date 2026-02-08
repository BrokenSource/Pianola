from dearlog import logger  # isort: split

import importlib.metadata

from broken.project import BrokenProject

__version__: str = importlib.metadata.version(__package__)
__about__:   str = "🎹 World's finest piano roll visualizer, where elegance meets motion"

PIANOLA = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    ABOUT=__about__,
)

from pianola.scene import PianolaScene
