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

def copy_files(origin_file_list, destination_folder, destination_file_list):

    copy_all = False

    for file in origin_file_list:
        print("File to copy: " + str(file))
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
            destination_filename = (Path(destination_folder) / Path(file).with_segments(*Path(file).parts[1:])).absolute()
            #destination_filename = (Path(destination_folder) / Path(file)).absolute()
            print(f"Program would attempt to write {str(destination_filename)}, pulled from {file.name}")
            file_data = ""
            with open(file, "rb") as f:
                file_data = f.read()
            destination_filename.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
            with open(destination_filename, "w+b") as df:
                df.write(file_data)

    print("Copy operation completed.")

def main():
    origin, destination = validate()

    origin_files = iterate_directory([], origin)
    destination_files = iterate_directory([], destination)

    print("Origin: " + str(origin_files))
    print("Destination: " + str(destination_files))

    copy_files(origin_files, destination, destination_files)

if __name__ == "__main__":
    main()