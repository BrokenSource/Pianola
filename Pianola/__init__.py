import Broken
import Pianola.Resources as PianolaResources
from Broken import *

PIANOLA = PROJECT = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    APP_AUTHOR="BrokenSource",
    RESOURCES=PianolaResources,
)

Broken.set_project(PIANOLA)

from .Pianola import *
