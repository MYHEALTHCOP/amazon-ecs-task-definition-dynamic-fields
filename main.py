import os

family = os.environ.get('INPUT_FAMILY-NAME')

print(f'::set-output name=task-definition::${family}')


def main():
    print(f"\n\nHello GitHub actions: ${family}\n\n")
    print(f'::set-output name=task-definition::${family}')

if __name__ == "__main__":
    main()