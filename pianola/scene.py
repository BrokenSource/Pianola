import functools
from pathlib import Path
from typing import Annotated, Optional

from attr import define
from pydantic import Field
from shaderflow.message import ShaderMessage
from shaderflow.modules.audio import ShaderAudio
from shaderflow.modules.piano import ShaderPiano
from shaderflow.scene import ShaderScene
from typer import Option

from broken import BrokenModel, BrokenPath, StaticClass, log
from pianola import PIANOLA, PIANOLA_ABOUT

# ------------------------------------------------------------------------------------------------ #

PIANOLA_SHADER: Path = (PIANOLA.RESOURCES.SHADERS/"pianola.frag")

class SoundFonts(StaticClass):

    @staticmethod
    @functools.lru_cache
    def Salamander() -> Path:
        """Salamander Grand Piano, Licensed under CC-BY-3.0, by Alexander Holm"""
        URL = "https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz"
        return next(BrokenPath.get_external(URL).rglob("*.sf2"))

class Songs(StaticClass):

    @staticmethod
    @functools.lru_cache
    def TheEntertainer() -> Path:
        """The Entertainer, Public Domain, by Scott Joplin"""
        return BrokenPath.get_external("https://bitmidi.com/uploads/28765.mid")

# ------------------------------------------------------------------------------------------------ #

@define
class PianolaScene(ShaderScene):

    class Config(ShaderScene.Config):

        # --------------------------------------|

        class Midi(BrokenModel):
            """Input and configure a midi file to be played"""

            file: Annotated[Path, Option("--input", "-i")] = Songs.TheEntertainer()
            """The midi file to play, automatically downloaded if URL"""

            audio: Annotated[Optional[Path], Option("--audio", "-a")] = None
            """The optional pre-rendered final video audio"""

            minimum_velocity: Annotated[int, Option(
                "--min-velocity", "--min", min=0, max=127)] = 40
            """Normalize velocities to this minimum value"""

            maximum_velocity: Annotated[int, Option(
                "--max-velocity", "--max", min=0, max=127)] = 127
            """Normalize velocities to this maximum value"""

        midi: Midi = Field(default_factory=Midi)

        # --------------------------------------|

        class Piano(BrokenModel):
            """Configure the piano roll display"""

            roll_time: Annotated[float, Option(
                "--roll-time", "-r", min=0)] = 2.0
            """How long the notes are visible"""

            height: Annotated[float, Option(
                "--height", "-h", min=0, max=1)] = 0.275
            """Height of the piano in the shader (0-1)"""

            black_ratio: Annotated[float, Option(
                "--black-ratio", "-b", min=0, max=1)] = 0.6
            """How long are black keys compared to white keys"""

            extra_keys: Annotated[int, Option(
                "--extra-keys", "-e", min=0)] = 6
            """Display the dynamic range plus this many keys on each side"""

        piano: Piano = Field(default_factory=Piano)

        # --------------------------------------|

        class SoundFont(BrokenModel):
            """Input and configure a soundfont to be used"""

            file: Annotated[Path, Option("--input", "-i")] = SoundFonts.Salamander()
            """The soundfont to use for the piano, automatically downloaded if URL"""

        soundfont: SoundFont = Field(default_factory=SoundFont)

    # -------------------------------------------------------------------------------------------- #
    # Command line interface

    def commands(self):
        self.cli.description = PIANOLA_ABOUT

        with self.cli.panel(self.scene_panel):
            self.cli.command(self.config.midi)
            self.cli.command(self.config.piano)
            self.cli.command(self.config.soundfont)

    # -------------------------------------------------------------------------------------------- #
    # Module implementation

    def build(self):
        self.audio = ShaderAudio(scene=self, name="iAudio")
        self.piano = ShaderPiano(scene=self)
        self.shader.fragment = PIANOLA_SHADER

    def handle(self, message: ShaderMessage) -> None:
        ShaderScene.handle(self, message)

        if isinstance(message, ShaderMessage.Window.FileDrop):
            file = BrokenPath.get(message.files[0])

            if (file.suffix == ".mid"):
                self.config.midi.file = file
                self.load_midi(file)

            elif (file.suffix == ".sf2"):
                self.config.soundfont.file = file
                self.piano.fluid_load(file)

            elif (file.suffix in {".png", ".jpg", ".jpeg"}):
                log.warn("No background image support yet")

    def setup(self) -> None:
        self.load_soundfont(self.config.soundfont.file)
        self.load_midi(self.config.midi.file)

        # Mirror common settings
        self.piano.height = self.config.piano.height
        self.piano.roll_time = self.config.piano.roll_time
        self.piano.black_ratio = self.config.piano.black_ratio
        self.piano.extra_keys = self.config.piano.extra_keys

        # Midi -> Audio if exporting and input audio doesn't exist
        if (self.exporting) and not BrokenPath.get(self.config.midi.audio):
            self.audio.file = self.piano.fluid_render(
                soundfont=self.config.soundfont.file,
                midi=self.config.midi.file
            )

    def update(self) -> None:

        # Mouse drag time scroll to match piano roll size
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))*self.camera.zoom.value

    # -------------------------------------------------------------------------------------------- #
    # Internals

    def load_soundfont(self, soundfont: Path) -> None:
        self.piano.fluid_load(soundfont)

    def load_midi(self, midi: Path) -> None:
        self.piano.fluid_all_notes_off()
        self.piano.clear()
        self.piano.load_midi(midi)
        self.piano.normalize_velocities(
            minimum=self.config.midi.minimum_velocity,
            maximum=self.config.midi.maximum_velocity
        )
