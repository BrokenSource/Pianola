import subprocess
from pathlib import Path
from typing import Annotated, Optional

import pooch
from attrs import Factory, define
from pydantic import BaseModel, ConfigDict
from shaderflow.audio import ShaderAudio
from shaderflow.message import ShaderMessage
from shaderflow.piano import ShaderPiano
from shaderflow.scene import ShaderScene
from typer import Option

from broken.path import BrokenPath
from pianola import RESOURCES, __about__, logger

# ---------------------------------------------------------------------------- #

class PianolaConfig(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    # --------------------------------------|
    # Piano

    roll_time: Annotated[float, Option("--roll", "-r")] = 2.0
    """How long the notes are visible"""

    height: Annotated[float, Option("--height", "-h")] = 0.275
    """Height of the piano in the shader"""

    black_ratio: Annotated[float, Option("--black-ratio", "-b")] = 0.6
    """How long are black keys compared to white keys"""

    extra_keys: Annotated[int, Option("--extra-keys", "-e")] = 6
    """Display the dynamic range plus this many keys on each side"""

    # --------------------------------------|
    # Midi

    # Public Domain https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=263
    midi: Annotated[Path, Option("--input", "-i")] = (RESOURCES/"entertainer.mid")
    """Midi file for realtime or rendering input"""

    audio: Annotated[Optional[Path], Option("--audio", "-a")] = None
    """The optional pre-rendered final video audio"""

    # --------------------------------------|
    # SoundFont

    # Courtesy http://www.schristiancollins.com/generaluser.php
    soundfont: Annotated[Path, Option("--soundfont", "-s")] = pooch.retrieve(
        url="https://github.com/x42/gmsynth.lv2/raw/b899b78640e0b99ec84d939c51dea2058673a73a/sf2/GeneralUser_LV2.sf2",
        known_hash="sha256:c278464b823daf9c52106c0957f752817da0e52964817ff682fe3a8d2f8446ce",
        fname="GeneralUser_LV2.sf2")
    """SoundFont for realtime or rendering audio"""

# ---------------------------------------------------------------------------- #

@define
class Pianola(ShaderScene):
    config: PianolaConfig = Factory(PianolaConfig)

    def commands(self):
        self.cli.description = __about__

        with self.cli.panel(self.scene_panel):
            self.cli.command(self.config, name="config")

    def load_midi(self, midi: Path) -> None:
        self.piano.fluid_all_notes_off()
        self.piano.clear()
        self.piano.load_midi(midi)
        # self.piano.normalize_velocities(
        #     minimum=80,
        #     maximum=120,
        # )

    def build(self):
        self.shader.fragment = (RESOURCES/"pianola.glsl")
        self.audio = ShaderAudio(scene=self, name="iAudio")
        self.piano = ShaderPiano(scene=self)

    def handle(self, message: ShaderMessage) -> None:
        ShaderScene.handle(self, message)

        if isinstance(message, ShaderMessage.Window.FileDrop):
            file = BrokenPath.get(message.files[0])

            if (file.suffix == ".mid"):
                self.config.midi = file
            elif (file.suffix == ".sf2"):
                self.config.soundfont = file

            self.setup()

    def setup(self) -> None:
        self.piano.fluid_load(self.config.soundfont)
        self.load_midi(self.config.midi)

        # Mirror common settings
        self.piano.height = self.config.height
        self.piano.roll_time = self.config.roll_time
        self.piano.black_ratio = self.config.black_ratio
        self.piano.extra_keys = self.config.extra_keys

        # Render midi to audio when no audio is provided
        if (self.exporting) and (self.config.audio is None):
            from tempfile import NamedTemporaryFile
            self._audio = NamedTemporaryFile(suffix=".wav")
            subprocess.check_call((
                "fluidsynth", "-qni",
                "-F", self._audio.name,
                "-r", "44100",
                "-g", "1.8",
                self.config.soundfont,
                self.config.midi,
            ))
            self.audio.file = self._audio.name

    # Mouse drag time scroll to match piano roll size
    def update(self) -> None:
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))*self.camera.zoom.value
