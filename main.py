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
    relative_filepath = dest / filepath.with_segments(*filepath.parts[1:])
    
    # Return the absolute path for completeness in file operations
    return relative_filepath.absolute()

def copy_files(origin_file_list, destination_folder, destination_file_list):

    copy_all = False

    for file in origin_file_list:
        copy_file = True
        cancel_copy = False
        for existing_file in destination_file_list:
            if Path(file).name == Path(existing_file).name:
                if not copy_all:
                    while True:
                        answer = input(f"Destination folder already has the file {file.name}, overwrite? ([y]es/[n]o/[a]ll/[c]ancel): ")
                        match answer.lower():
                            case "y":
                                break
                            case "n":
                                copy_file = False
                                break
                            case "a":
                                copy_all = True
                                break
                            case "c":
                                cancel_copy = True
                                break
        
        if cancel_copy:
            print("Canceled copy operation.")
            break

        if copy_file:
            destination_filename = _create_destination_filepath(destination_folder, file)
            destination_filename.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
            destination_filename.write_bytes(file.read_bytes())

    print("Copy operation completed.")

def main():
    origin, destination = validate()

    origin_files = iterate_directory([], origin)
    destination_files = iterate_directory([], destination)

    copy_files(origin_files, destination, destination_files)

if __name__ == "__main__":
    main()