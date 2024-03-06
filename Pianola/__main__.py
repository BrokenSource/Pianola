from . import *


def main():
    with BrokenProfiler("PIANOLA"):
        PIANOLA.welcome()
        pianola = PianolaScene()
        pianola.cli(sys.argv[1:])

if __name__ == "__main__":
    main()
