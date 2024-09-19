"""Asynchrous File Copier

This program allows the user to specify an origin folder and a destination
folder. If the folders are valid by the program (not the same folder, not a
reserved folder, etc) then the program will attempt an asynchronous file copy
from the origin folder to the destination folder.

The program will prompt for if the destination folder is not empty and will
prompt about any duplications it finds. The program only checks if the
filename is the same.

USAGE: async_copy.py <origin folder> <destination folder>
"""

import asyncio
from pathlib import Path

import aiofiles

from error_checker import validate

def iterate_directory(directory, file_list=()):
    """
    This recursive function will iterate through a directory and return a
    list of files. If it encounters a deeper directory, it will recurse until
    it can proceed no longer.
    
    Keyword arguments:
    file_list -- list of files for checks for if they exist. (default ())
    """

    files = list(file_list)
    for file in Path(directory).iterdir():
        if file.is_file():
            files.append(file)
        elif file.is_dir():
            new_files = iterate_directory(file, file_list)
            for new_file in new_files:
                if new_file not in files:
                    files.append(new_file)
    return files

def _create_destination_filepath(destination_folder, file):
    dest = Path(destination_folder)
    filepath = Path(file)

    # Slice out the origin folder name
    relative_filepath = dest / _path_minus_parent(filepath)
    return relative_filepath.absolute()

def _path_minus_parent(filepath):
    return Path(filepath).with_segments(*Path(filepath).parts[1:])

async def async_copy(file_to_copy, destination_folder):
    """
    Given a string filepath file_to_copy, asynchronously copy it to the
    string destination_folder.
    """

    destination_filename = _create_destination_filepath(destination_folder, file_to_copy)
    filemode = destination_filename.parent.stat().st_mode
    destination_filename.parent.mkdir(mode=filemode, parents=True, exist_ok=True)

    contents = ""

    async with aiofiles.open(file_to_copy, mode="rb") as f:
        contents = await f.read()
    async with aiofiles.open(destination_filename, mode="w+b") as f:
        filename = Path(destination_filename).name
        print(f"Copying file {filename}... ")
        await f.write(contents)
        print(f"Finished copying file {filename}.")

def _ask_overwrite(existing_file):
    return input(f"Destination file {_path_minus_parent(existing_file)} exists, overwrite?"
                 + "([y]es/[n]o/[a]ll/[c]ancel): ")

def _get_file_copy_list(origin_file_list, destination_file_list):

    files_to_copy = [file for file in origin_file_list]
    _copy_all = False
    for file in origin_file_list:
        _cancel_copy = False
        for existing_file in destination_file_list:
            if Path(file).name == Path(existing_file).name:
                if not _copy_all:
                    while True:
                        try:
                            answer = _ask_overwrite(existing_file)
                            match answer.lower():
                                case "y":
                                    break
                                case "n":
                                    files_to_copy.remove(file)
                                    break
                                case "a":
                                    _copy_all = True
                                    break
                                case "c":
                                    _cancel_copy = True
                                    break
                        except KeyboardInterrupt:
                            _cancel_copy = True
                            break
        # Break out of the outer loop here.
        if _cancel_copy:
            print("Canceled copy operation.")
            files_to_copy = []
            break

    return files_to_copy

async def _copy_files(origin_file_list, destination_folder, destination_file_list):

    files_to_copy = _get_file_copy_list(origin_file_list, destination_file_list)
    if len(files_to_copy) > 0:

        async with asyncio.TaskGroup() as tg:
            for file in files_to_copy:
                tg.create_task(async_copy(file, destination_folder))

        print("Copy operation completed.")

def main():
    """
    Validate the origin and destination arguments, generate a list of files,
    and then run the copy operation.
    """

    # Validation and error checking from error_checker.validate()
    origin, destination = validate()

    # Create the lists of files.
    origin_files = iterate_directory(origin)
    destination_files = iterate_directory(destination)

    # Run the copy operation!
    asyncio.run(_copy_files(origin_files, destination, destination_files))

if __name__ == "__main__":
    main()
