import time

from pathlib import Path
from error_checker import validate

def iterate_directory(file_list, directory):
    for file in Path(directory).iterdir():
        if file.is_file():
            file_list.append(file)
        elif file.is_dir():
            new_files = iterate_directory(file_list, file)
            for new_file in new_files:
                if new_file not in file_list:
                    file_list.append(new_file)
    return file_list

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

def copy_files(origin_file_list, destination_folder, destination_file_list):

    _copy_all = False
    _any_copy = False

    for file in origin_file_list:

        _copy_file = True
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
                                    _copy_file = False
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
            break

        # TODO: Research modes; 0o777 may be too permissive. Can I get the original permissions?
        if _copy_file:
            destination_filename = _create_destination_filepath(destination_folder, file)
            
            print(f"Copying file {Path(destination_filename).name}... ", end="")
            
            destination_filename.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
            destination_filename.write_bytes(file.read_bytes())
            if not _any_copy:
                _any_copy = True

            print("Done.")

    if _any_copy:
        print("Copy operation completed.")

def main():
    origin, destination = validate()

    origin_files = iterate_directory([], origin)
    destination_files = iterate_directory([], destination)

    copy_files(origin_files, destination, destination_files)

if __name__ == "__main__":
    main()