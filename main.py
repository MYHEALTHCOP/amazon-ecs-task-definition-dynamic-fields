import os

family = os.environ.get('family-name')


def main():
    print(f"\n\nHello GitHub actions: ${family}\n\n")

if __name__ == "__main__":
    main()