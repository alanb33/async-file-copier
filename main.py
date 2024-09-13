import asyncio
from pathlib import Path
from error_checker import validate

import aiofiles

def iterate_directory(file_list, directory):
    
    files = file_list.copy()
    
    for file in Path(directory).iterdir():
        if file.is_file():
            files.append(file)
        elif file.is_dir():
            new_files = iterate_directory(file_list, file)
            for new_file in new_files:
                if new_file not in files:
                    files.append(new_file)
    
    return files

def _create_destination_filepath(destination_folder, file):
    
    # Convert to Path objects
    dest = Path(destination_folder)
    filepath = Path(file)

    # Slice out the origin folder name
    relative_filepath = dest / _path_minus_parent(filepath)
    
    # Return the absolute path for completeness in file operations
    return relative_filepath.absolute()

def _path_minus_parent(filepath):
    return Path(filepath).with_segments(*Path(filepath).parts[1:])

async def async_copy(file_to_copy, destination_folder):

    destination_filename = _create_destination_filepath(destination_folder, file_to_copy)
    
    # TODO: Research modes; 0o777 may be too permissive. Can I get the original permissions?
    destination_filename.parent.mkdir(mode=0o777, parents=True, exist_ok=True)

    contents = ""

    async with aiofiles.open(file_to_copy, mode="rb") as f:
        contents = await f.read()
    
    async with aiofiles.open(destination_filename, mode="w+b") as f:
        filename = Path(destination_filename).name
        print(f"Copying file {filename}... ")
        await f.write(contents)
        print(f"Finished copying file {filename}.")

def _get_file_copy_list(origin_file_list, destination_file_list):

    files_to_copy = origin_file_list.copy()
    _copy_all = False

    for file in origin_file_list:

        _cancel_copy = False
        
        for existing_file in destination_file_list:
            if Path(file).name == Path(existing_file).name:
                if not _copy_all:
                    while True:
                        try:
                            answer = input(f"Destination folder already has the file {_path_minus_parent(existing_file)}, overwrite? ([y]es/[n]o/[a]ll/[c]ancel): ")
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
                if _copy_all:
                    files_to_copy.append(file)
        
        # Break out of the outer loop here.
        if _cancel_copy:
            print("Canceled copy operation.")
            files_to_copy = []
            break

    return files_to_copy

async def copy_files(origin_file_list, destination_folder, destination_file_list):

    print("Copy files: Origin file list is " + str(origin_file_list))

    files_to_copy = _get_file_copy_list(origin_file_list, destination_file_list)

    print("Files to copy are: " + str(files_to_copy))
    
    if len(files_to_copy) > 0:

        async with asyncio.TaskGroup() as tg:
            for file in files_to_copy:
                tg.create_task(async_copy(file, destination_folder))

        print("Copy operation completed.")

def main():
    origin, destination = validate()

    origin_files = iterate_directory([], origin)
    print("Origin files: " + str(origin_files))
    destination_files = iterate_directory([], destination)

    asyncio.run(copy_files(origin_files, destination, destination_files))

if __name__ == "__main__":
    main()