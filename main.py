from error_checker import validate

def main():
    origin, destination = validate()
    print("Origin: " + str(origin))
    print("Destination: " + str(destination))

if __name__ == "__main__":
    main()