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

import pianola
from broken.path import BrokenPath


class PianolaConfig(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    # --------------------------------------|
    # Piano

    roll_time: Annotated[float, Option("--roll", "-r")] = 2.0
    """How long falling notes are visible"""

    piano_ratio: Annotated[float, Option("--height", "-h")] = 0.275
    """Ratio of the screen used for the piano"""

    black_ratio: Annotated[float, Option("--black-ratio", "-b")] = 0.6
    """How long are black keys compared to white keys"""

    extra_keys: Annotated[int, Option("--extra-keys", "-e")] = 6
    """Extends the dynamic focus on playing notes"""

    # --------------------------------------|
    # Midi

    # Public Domain https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=263
    midi: Annotated[Path, Option("--midi", "-i")] = (pianola.resources/"entertainer.mid")
    """Midi file for realtime or rendering"""

    midi_audio_gain: Annotated[float, Option("--midi-audio-gain", "-g")] = 1.5
    """Master gain for rendered midi files"""

    midi_audio_rate: Annotated[int, Option("--midi-audio-rate", "-r")] = 44100
    """Sample rate for rendered midi files"""

    audio: Annotated[Optional[Path], Option("--audio", "-a")] = None
    """Optional pre-rendered final video audio"""

    # --------------------------------------|
    # SoundFont

    # Courtesy http://www.schristiancollins.com/generaluser.php
    soundfont: Annotated[Path, Option("--soundfont", "-s")] = pooch.retrieve(
        url="https://github.com/x42/gmsynth.lv2/raw/b899b78640e0b99ec84d939c51dea2058673a73a/sf2/GeneralUser_LV2.sf2",
        known_hash="xxh128:25586f570092806dccbf834d2c3517b9",
        path=pianola.directories.user_data_path,
        fname="GeneralUser_LV2.sf2",
        progressbar=True,
    )
    """SoundFont for realtime or rendering audio"""

# ---------------------------------------------------------------------------- #

@define
class Pianola(ShaderScene):
    config: PianolaConfig = Factory(PianolaConfig)

    def commands(self):
        self.cli.description = pianola.__about__

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
        self.shader.fragment = (pianola.resources/"pianola.glsl")
        self.audio = ShaderAudio(scene=self, name="iAudio")
        self.piano = ShaderPiano(scene=self)
        self.piano.fluid_install()
        self.piano.fluid_start()

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
        self.load_midi(self.config.midi)
        self.piano.fluid_load(self.config.soundfont)

        # Mirror common settings
        self.piano.height = self.config.piano_ratio
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
                "-r", str(self.config.midi_audio_rate),
                "-g", str(self.config.midi_audio_gain),
                self.config.soundfont,
                self.config.midi,
            ))
            self.audio.file = self._audio.name

    # Mouse drag time scroll to match piano roll size
    def update(self) -> None:
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))*self.camera.zoom.value
