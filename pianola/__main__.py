import sys

from pianola import Pianola


def main():
    pianola = Pianola()
    pianola.cli(*sys.argv[1:])

if __name__ == "__main__":
    main()
