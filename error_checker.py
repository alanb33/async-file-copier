"""Error Checker Utility

This is a utility script invoked by the primary async_copy.py program.
This script only checks that incoming arguments for folder destinations are
valid before being used by the main program.
"""

from pathlib import Path
import sys

def _check_for_errors(origin, destination):
    _check_for_source_match(origin, destination)
    _check_for_reserved_directories(origin, destination)
    _check_for_empty_directory(destination)

def _check_for_empty_directory(destination):
    path = Path(destination)
    obj_count = 0
    for _ in path.iterdir():
        obj_count += 1

    if obj_count > 0:
        while True:
            try:
                answer = input(f"Destination path [{destination}] is not empty. Continue? (y/n): ")
                match str(answer.lower()):
                    case "y":
                        break
                    case "n":
                        sys.exit("Aborting.")
            except KeyboardInterrupt:
                sys.exit("\nAborting.")

def _check_for_reserved_directories(*args):

    for directory in args:
        if Path(directory).is_dir() and Path(directory).is_reserved():
            sys.exit(f"Unable to operate on reserved directory [{Path(directory).absolute()}].")

def _check_for_source_match(origin, destination):
    if origin == destination:
        sys.exit("Origin and destination cannot be the same directory.")

def _validate_sources(*args):
    for directory in args:
        _dir = Path(directory)
        if _dir.exists():
            if not _dir.is_dir():
                sys.exit(f"Did not receive a valid directory path: {_dir}")
        else:
            sys.exit(f"Directory provided but does not exist: {_dir}")

def _get_sources():
    if len(sys.argv) == 3:
        origin = sys.argv[1]
        destination = sys.argv[2]
        return (origin, destination)
    sys.exit("Expected 3 arguments but received " + str(len(sys.argv)) + "."
             + "\nUSAGE: main.py <origin directory> <destination directory>")

def validate():
    """
    Validate the incoming keyword strings in the program invocation.
    
    The program expects an origin folder and a destination folder. If either
    are not valid, the program will exit.
    """
    origin, destination = _get_sources()
    _validate_sources(origin, destination)
    _check_for_errors(origin, destination)
    return (origin, destination)
