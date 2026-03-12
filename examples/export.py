import pianola
from pianola import PianolaScene

scene = PianolaScene()
scene.config.midi = pianola.resources/"entertainer.mid"

# Export a video
scene.main(
    output="piano-roll.mp4",
    width=1920,
    height=1080,
    ssaa=2,
    fps=60,
)

