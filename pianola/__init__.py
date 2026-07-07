from dearlog import logger  # isort: split

from importlib.metadata import metadata

__meta__    = metadata(str(__package__))
__about__   = __meta__.get("Summary")
__version__ = __meta__.get("Version")

from pathlib import Path

from platformdirs import PlatformDirs

resources = Path(__file__).parent/"resources"

directories = PlatformDirs(
    appname=__package__,
    ensure_exists=True,
    opinion=True,
)

from pianola.scene import PianolaScene
