from broken import BrokenProject, __version__

PIANOLA_ABOUT = """
🎹 World's finest piano roll visualizer, where elegance meets motion.\n\n
→ See the [blue link=https://brokensrc.dev/pianola/]Website[/] for examples and more information!\n
"""

PIANOLA = PROJECT = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Pianola",
    ABOUT=PIANOLA_ABOUT,
)

from pianola.scene import PianolaScene
