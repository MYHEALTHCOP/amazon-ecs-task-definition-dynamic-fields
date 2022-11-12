import os

family = os.environ.get('INPUT_FAMILY-NAME')
output = os.environ.get("GITHUB_OUTPUT")

print(f'::set-output name=task-definition::${family}')



def main():
    print(f"\n\nHello GitHub actions: ${family}\n\n")
    print(f'::set-output name=task-definition::${family}')
    print(output)

if __name__ == "__main__":
    main()