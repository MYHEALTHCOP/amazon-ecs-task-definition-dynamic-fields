import os

family = os.environ.get('INPUT_FAMILY-NAME')


def main():
    print(f"\n\nHello GitHub actions: ${family}\n\n")

if __name__ == "__main__":
    main()