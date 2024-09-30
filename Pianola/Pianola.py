from pathlib import Path
from typing import Annotated

from attr import Factory, define
from ShaderFlow.Message import ShaderMessage
from ShaderFlow.Modules.Audio import ShaderAudio
from ShaderFlow.Modules.Piano import ShaderPiano
from ShaderFlow.Scene import ShaderScene
from typer import Option

from Broken import BrokenEnum, BrokenPath, log
from Pianola import PIANOLA


@define
class PianolaConfig:
    class SoundFont(BrokenEnum):
        Salamander = "https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz"
        """# Note: Salamander Grand Piano, Licensed under CC BY 3.0, by Alexander Holm"""

    class Songs(BrokenEnum):
        TheEntertainer = "https://bitmidi.com/uploads/28765.mid"

    soundfont: SoundFont = SoundFont.Salamander.field()
    midi:      Songs     = Songs.TheEntertainer.field()

# ------------------------------------------------------------------------------------------------ #


@define
class PianolaScene(ShaderScene):
    """Basic piano roll"""
    __name__ = "Pianola"

    config: PianolaConfig = Factory(PianolaConfig)

    # Todo: Think better ways of presetting Scenes in general
    def input(self,
        midi:      Annotated[str,  Option("--midi",      "-m", help="Midi file to load")],
        audio:     Annotated[str,  Option("--audio",     "-a", help="Pre-rendered Audio File of the Input Midi")]=None,
        normalize: Annotated[bool, Option("--normalize", "-n", help="Normalize the velocities of the Midi")]=False,
    ):
        ...

    def build(self):
        self.soundfont_file = next(BrokenPath.get_external(self.config.soundfont).rglob("*.sf2"))

        # Define scene inputs
        self.midi_file  = BrokenPath.get_external(self.config.midi)
        self.audio_file = "/path/to/your/midis/audio.ogg"

        # Make modules
        self.audio = ShaderAudio(scene=self, name="Audio")
        self.piano = ShaderPiano(scene=self)
        self.piano.normalize_velocities(100, 100)
        self.piano.fluid_load(self.soundfont_file)
        self.shader.fragment = (PIANOLA.RESOURCES.SHADERS/"Pianola.frag")
        self.load_midi(self.midi_file)

    def load_midi(self, path: Path):
        self.piano.fluid_all_notes_off()
        self.piano.clear()
        self.piano.load_midi(path)
        self.time = (-1 * self.piano.roll_time)
        self.set_duration(self.piano.duration)

    def handle(self, message: ShaderMessage):
        ShaderScene.handle(self, message)

        if isinstance(message, ShaderMessage.Window.FileDrop):
            file = BrokenPath.get(message.files[0])

            if (file.suffix == ".mid"):
                self.load_midi(file)

            elif (file.suffix == ".sf2"):
                self.piano.fluid_load(file)

            elif (file.suffix in (".png", ".jpg", ".jpeg")):
                log.warning("No background image support yet")

    def setup(self):

        # Midi -> Audio if rendering or input audio doesn't exist
        if (self.exporting) and not BrokenPath.get(self.audio.file):
            self.audio.file = self.piano.fluid_render(soundfont=self.soundfont_file, midi=self.midi_file)

    def update(self):

        # Mouse drag time scroll to match piano roll size
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))/self.camera.zoom.value

