import sys

import pianola
from pianola import PianolaScene


def main():
    scene = PianolaScene()
    scene.cli.help = pianola.__about__
    scene.cli.version = pianola.__version__
    scene.cli.meta(sys.argv[1:])

if __name__ == "__main__":
    main()
