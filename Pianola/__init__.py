import Pianola.Resources as PianolaResources
from ShaderFlow import *

import Broken
from Broken import *

PIANOLA = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    APP_AUTHOR="BrokenSource",
    RESOURCES=PianolaResources,
)

Broken.PROJECT = PIANOLA

from .Pianola import *
