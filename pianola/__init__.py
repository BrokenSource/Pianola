from dearlog import logger  # isort: split

from importlib.metadata import metadata

__meta__:   dict = metadata(__package__)
__about__:   str = __meta__.get("Summary")
__author__:  str = __meta__.get("Author")
__version__: str = __meta__.get("Version")

from pathlib import Path

from platformdirs import PlatformDirs

resources = Path(__file__).parent/"resources"

directories = PlatformDirs(
    appname=__package__,
    ensure_exists=True,
    opinion=True,
)

from pianola.scene import Pianola
