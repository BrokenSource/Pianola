from Broken.Mkdocs import BrokenMkdocs

make = BrokenMkdocs(makefile=__file__)
make.symlink_readme()
