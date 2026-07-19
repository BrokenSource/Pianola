from dearlog import logger  # isort: split

__about__   = "🎹 Smoothest piano roll visualizer"
__package__ = "pianola"
__version__ = "0.10.0"
__license__ = "AGPL-3.0"

from pathlib import Path

from platformdirs import PlatformDirs

resources = Path(__file__).parent/"resources"

directories = PlatformDirs(
    appname=__package__,
    ensure_exists=True,
    opinion=True,
)

from pianola.scene import PianolaScene
