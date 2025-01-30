import Pianola.Resources as PianolaResources
from Broken import BrokenProject, __version__

PIANOLA_ABOUT = """
🎹 World's finest piano roll visualizer, where elegance meets motion.\n\n
→ See the [blue link=https://brokensrc.dev/pianola/]Website[/] for examples and more information!\n
"""

PIANOLA = PROJECT = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    APP_AUTHOR="BrokenSource",
    RESOURCES=PianolaResources,
    ABOUT=PIANOLA_ABOUT,
)
