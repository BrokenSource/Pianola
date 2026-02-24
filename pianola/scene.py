import subprocess
from pathlib import Path
from typing import Annotated, Any, Optional

import pooch
from attrs import Factory, define
from cyclopts import Parameter
from shaderflow.audio import ShaderAudio
from shaderflow.message import ShaderMessage
from shaderflow.piano import ShaderPiano
from shaderflow.scene import ShaderScene

import pianola


@define(kw_only=True)
class PianolaConfig:
    """Pianola style and inputs configuration"""

    # --------------------------------------|
    # Piano

    rolltime: Annotated[float, Parameter(group="Piano")] = 2.0
    """How long falling notes are visible"""

    height: Annotated[float, Parameter(group="Piano")] = 0.275
    """Ratio of the screen used for the piano"""

    black: Annotated[float, Parameter(group="Piano")] = 0.6
    """How long are black keys compared to white keys"""

    sidekeys: Annotated[int, Parameter(group="Piano")] = 6
    """Extends the dynamic focus on playing notes"""

    # --------------------------------------|
    # Midi

    audio: Annotated[Optional[Path], Parameter(group="Midi")] = None
    """Optional pre-rendered final video audio"""

    # Public Domain https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=263
    midi: Annotated[Path, Parameter(group="Midi")] = (pianola.resources/"entertainer.mid")
    """Midi file for realtime or rendering"""

    midi_gain: Annotated[float, Parameter(group="Midi")] = 1.5
    """Master gain for rendered midi files"""

    samplerate: Annotated[int, Parameter(group="Midi")] = 44100
    """Sample rate for rendered midi files"""

    # --------------------------------------|
    # SoundFont

    # Courtesy http://www.schristiancollins.com/generaluser.php
    soundfont: Annotated[Path, Parameter(group="SoundFont")] = pooch.retrieve(
        url="https://github.com/x42/gmsynth.lv2/raw/b899b78640e0b99ec84d939c51dea2058673a73a/sf2/GeneralUser_LV2.sf2",
        known_hash="xxh128:25586f570092806dccbf834d2c3517b9",
        path=pianola.directories.user_data_path,
        fname="GeneralUser_LV2.sf2",
        progressbar=True,
    )
    """SoundFont for realtime or rendering audio"""

# ---------------------------------------------------------------------------- #

@define
class PianolaScene(ShaderScene):
    config: PianolaConfig = Factory(PianolaConfig)

    def smartset(self, object: Any) -> Any:
        if isinstance(object, PianolaConfig):
            self.config = object
        return object

    def commands(self):
        self.cli.help = pianola.__about__
        self.cli.version = pianola.__version__
        self.cli.command(
            PianolaConfig, name="config",
            result_action=self.smartset
        )

    def build(self):
        self.shader.fragment = (pianola.resources/"pianola.glsl")
        self.audio = ShaderAudio(scene=self, name="iAudio")
        self.piano = ShaderPiano(scene=self)
        self.piano.fluid_install()
        self.piano.fluid_start()

    def handle(self, message: ShaderMessage) -> None:
        ShaderScene.handle(self, message)

        if isinstance(message, ShaderMessage.Window.FileDrop):
            file = Path(message.files[0])

            if (file.suffix == ".mid"):
                self.config.midi = file
            elif (file.suffix == ".sf2"):
                self.config.soundfont = file

            self.setup()

    def setup(self) -> None:
        self.piano.clear()
        self.piano.fluid_all_notes_off()
        self.piano.load_midi(self.config. midi)
        self.piano.fluid_load(self.config.soundfont)

        # Mirror common settings
        self.piano.height = self.config.height
        self.piano.roll_time = self.config.rolltime
        self.piano.black_ratio = self.config.black
        self.piano.extra_keys = self.config.sidekeys

        # Render midi to audio when no audio is provided
        if (self.exporting) and (self.config.audio is None):
            from tempfile import NamedTemporaryFile
            self._audio = NamedTemporaryFile(suffix=".wav")
            subprocess.check_call((
                "fluidsynth", "-qni",
                "-F", self._audio.name,
                "-r", str(self.config.samplerate),
                "-g", str(self.config.midi_gain),
                self.config.soundfont,
                self.config.midi,
            ))
            self.audio.file = self._audio.name

    # Mouse drag time scroll to match piano roll size
    def update(self) -> None:
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))*self.camera.zoom.value
