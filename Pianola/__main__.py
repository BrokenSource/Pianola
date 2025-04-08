import sys

from Broken import BrokenProfiler
from Pianola.Pianola import PianolaScene


def main():
    with BrokenProfiler("PIANOLA"):
        pianola = PianolaScene()
        pianola.cli(sys.argv[1:])

if __name__ == "__main__":
    main()
