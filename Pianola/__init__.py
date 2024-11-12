import Pianola.Resources as PianolaResources
from Broken import BrokenProject, __version__

__version__ = __version__

PIANOLA = PROJECT = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    APP_AUTHOR="BrokenSource",
    RESOURCES=PianolaResources,
)
