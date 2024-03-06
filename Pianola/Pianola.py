from . import *


@define
class PianolaScene(ShaderFlowScene):
    """Basic piano roll"""
    __name__ = "Pianola"

    def build(self):

        # Note: Salamander Grand Piano, Licensed under CC BY 3.0, by Alexander Holm
        SALAMANDER = "https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz"
        self.soundfont_file = next(BrokenPath.extract(BrokenPath.download(SALAMANDER), BROKEN.DIRECTORIES.EXTERNALS).glob("**/*.sf2"))

        # Define scene inputs
        self.midi_file  = PIANOLA.RESOURCES/"Midis"/"Hopeless Sparkle.mid"
        self.audio_file = "/path/to/your/midis/audio.ogg"

        # Make modules
        self.audio = self.add(ShaderFlowAudio(name="Audio", file=self.audio_file))
        self.piano = self.add(ShaderFlowPiano)
        self.piano.load_midi(self.midi_file)
        # self.piano.normalize_velocities()
        self.piano.fluid_load(self.soundfont_file)
        self.engine.fragment = (PIANOLA.RESOURCES.SHADERS/"Pianola.frag")

    def _handle_(self, message: ShaderFlowMessage):
        if isinstance(message, ShaderFlowMessage.Window.FileDrop):
            file = BrokenPath(message.files[0])

            if (file.suffix == ".mid"):
                self.piano.fluid_all_notes_off()
                self.piano.clear()
                self.time = 1e6
                def after():
                    # self.piano.normalize_velocities()
                    self.time = -1
                BrokenThread(self.piano.load_midi, file, callback=after)

            elif (file.suffix == ".sf2"):
                self.piano.fluid_load(file)

            elif (file.suffix in (".png", ".jpg", ".jpeg")):
                log.warning("No background image support yet")

    def _setup_(self):

        # Midi -> Audio if rendering or input audio doesn't exist
        if (self.rendering and not self.benchmark) and not Path(self.audio.file).exists():
            self.audio.file = self.piano.fluid_render(soundfont=self.soundfont_file, midi=self.midi_file)

    def _update_(self):

        # Mouse drag time scroll to match piano roll size
        self._mouse_drag_time_factor = (self.piano.roll_time/(self.piano.height - 1))/self.camera.zoom.value

