import sys

from Broken import BrokenProfiler
from Pianola import PIANOLA
from Pianola.Pianola import PianolaScene


def main():
    with BrokenProfiler("PIANOLA"):
        PIANOLA.welcome()
        pianola = PianolaScene()
        pianola.cli(sys.argv[1:])

if __name__ == "__main__":
    main()
