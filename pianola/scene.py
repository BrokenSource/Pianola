import functools
from pathlib import Path
from typing import Annotated, Optional

from attrs import Factory, define
from pydantic import BaseModel, ConfigDict, Field
from shaderflow.audio import ShaderAudio
from shaderflow.message import ShaderMessage
from shaderflow.piano import ShaderPiano
from shaderflow.scene import ShaderScene
from typer import Option

from broken.path import BrokenPath
from pianola import RESOURCES, __about__, logger

# ---------------------------------------------------------------------------- #

class SoundFonts:

    @staticmethod
    @functools.lru_cache
    def Salamander() -> Path:
        """Salamander Grand Piano, Licensed under CC-BY-3.0, by Alexander Holm"""
        URL = "https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz"
        return next(BrokenPath.get_external(URL).rglob("*.sf2"))

# ---------------------------------------------------------------------------- #

class PianolaConfig(BaseModel):

    class Piano(BaseModel):
        """Configure the piano roll display"""
        model_config = ConfigDict(use_attribute_docstrings=True)

        roll_time: Annotated[float, Option("--roll-time", "-r")] = 2.0
        """How long the notes are visible"""

        height: Annotated[float, Option("--height", "-h")] = 0.275
        """Height of the piano in the shader"""

        black_ratio: Annotated[float, Option("--black-ratio", "-b")] = 0.6
        """How long are black keys compared to white keys"""

        extra_keys: Annotated[int, Option("--extra-keys", "-e")] = 6
        """Display the dynamic range plus this many keys on each side"""

    piano: Piano = Field(default_factory=Piano)

    # --------------------------------------|

    class Midi(BaseModel):
        """Input and configure a midi file to be played"""
        model_config = ConfigDict(use_attribute_docstrings=True)

        # Public Domain https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=263
        file: Annotated[Path, Option("--input", "-i")] = RESOURCES/"entertainer.mid"
        """The midi file to play"""

        audio: Annotated[Optional[Path], Option("--audio", "-a")] = None
        """The optional pre-rendered final video audio"""

        minimum_velocity: Annotated[int, Option("--min", min=0, max=127)] = 40
        """Normalize velocities to this minimum value"""

        maximum_velocity: Annotated[int, Option("--max", min=0, max=127)] = 100
        """Normalize velocities to this maximum value"""

    midi: Midi = Field(default_factory=Midi)

    # --------------------------------------|

    class SoundFont(BaseModel):
        """Input and configure a soundfont to be used"""
        model_config = ConfigDict(use_attribute_docstrings=True)

        file: Annotated[Path, Option("--input", "-i")] = SoundFonts.Salamander()
        """The soundfont to use for the piano"""

    soundfont: SoundFont = Field(default_factory=SoundFont)

# ---------------------------------------------------------------------------- #

@define
class PianolaScene(ShaderScene):
    config: PianolaConfig = Factory(PianolaConfig)

    def commands(self):
        self.cli.description = __about__

        with self.cli.panel(self.scene_panel):
            self.cli.command(self.config.midi)
            self.cli.command(self.config.piano)
            self.cli.command(self.config.soundfont)

    def load_midi(self, midi: Path) -> None:
        self.piano.fluid_all_notes_off()
        self.piano.clear()
        self.piano.load_midi(midi)
        self.piano.normalize_velocities(
            minimum=self.config.midi.minimum_velocity,
            maximum=self.config.midi.maximum_velocity
        )

    def build(self):
        self.shader.fragment = (RESOURCES/"pianola.glsl")
        self.audio = ShaderAudio(scene=self, name="iAudio")
        self.piano = ShaderPiano(scene=self)

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
                logger.warn("No background image support yet")

    def setup(self) -> None:
        self.piano.fluid_load(self.config.soundfont.file)
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

    # Mouse drag time scroll to match piano roll size
    def update(self) -> None:
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))*self.camera.zoom.value
