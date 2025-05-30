import sys

from pianola import PianolaScene


def main():
    pianola = PianolaScene()
    pianola.cli(sys.argv[1:])

if __name__ == "__main__":
    main()
