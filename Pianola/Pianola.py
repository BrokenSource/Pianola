from pathlib import Path
from typing import Annotated

from attr import define
from ShaderFlow.Message import Message
from ShaderFlow.Modules.Audio import ShaderAudio
from ShaderFlow.Modules.Piano import ShaderPiano
from ShaderFlow.Scene import ShaderScene
from typer import Option

from Broken.Base import BrokenPath
from Broken.BrokenEnum import BrokenEnum
from Broken.Logging import log
from Pianola import PIANOLA


class PianolaSoundFont(BrokenEnum):
    Salamander = "https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz"
    """# Note: Salamander Grand Piano, Licensed under CC BY 3.0, by Alexander Holm"""

@define
class PianolaConfig:
    soundfont: PianolaSoundFont = PianolaSoundFont.Salamander.field()

@define
class PianolaScene(ShaderScene):
    """Basic piano roll"""
    __name__ = "Pianola"

    # Todo: Think better ways of presetting Scenes in general
    def input(self,
        midi:      Annotated[str,  Option("--midi",      "-m", help="Midi file to load")],
        audio:     Annotated[str,  Option("--audio",     "-a", help="Pre-rendered Audio File of the Input Midi")]=None,
        normalize: Annotated[bool, Option("--normalize", "-n", help="Normalize the velocities of the Midi")]=False,
    ):
        ...

    def build(self):
        ShaderScene.build(self)
        self.soundfont_file = next(BrokenPath.get_external(PianolaSoundFont.Salamander).rglob("*.sf2"))

        # Define scene inputs
        self.midi_file  = PIANOLA.RESOURCES/"Midis"/"Hopeless Sparkle.mid"
        self.audio_file = "/path/to/your/midis/audio.ogg"

        # Make modules
        self.audio = ShaderAudio(scene=self, name="Audio")
        self.piano = ShaderPiano(scene=self)
        self.piano.load_midi(self.midi_file)
        self.piano.normalize_velocities(100, 100)
        self.piano.fluid_load(self.soundfont_file)
        self.shader.fragment = (PIANOLA.RESOURCES.SHADERS/"Pianola.frag")

    def handle(self, message: Message):
        ShaderScene.handle(self, message)

        if isinstance(message, Message.Window.FileDrop):
            file = BrokenPath(message.files[0])

            if (file.suffix == ".mid"):
                self.piano.fluid_all_notes_off()
                self.piano.clear()
                self.piano.load_midi(file)
                self.time = 0

            elif (file.suffix == ".sf2"):
                self.piano.fluid_load(file)

            elif (file.suffix in (".png", ".jpg", ".jpeg")):
                log.warning("No background image support yet")

    def setup(self):

        # Midi -> Audio if rendering or input audio doesn't exist
        if (self.rendering and not self.benchmark) and not Path(self.audio.file).exists():
            self.audio.file = self.piano.fluid_render(soundfont=self.soundfont_file, midi=self.midi_file)

    def update(self):

        # Mouse drag time scroll to match piano roll size
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))/self.camera.zoom.value

