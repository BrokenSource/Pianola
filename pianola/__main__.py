import sys

from broken import BrokenProfiler
from pianola import PianolaScene


def main():
    with BrokenProfiler("PIANOLA"):
        pianola = PianolaScene()
        pianola.cli(sys.argv[1:])

if __name__ == "__main__":
    main()
