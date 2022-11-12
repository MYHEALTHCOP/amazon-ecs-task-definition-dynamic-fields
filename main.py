import os

family = os.environ.get('INPUT_FAMILY-NAME')
output = os.environ.get("GITHUB_OUTPUT")

print(f'::setOutput name=task-definition::${family}')



def main():
    print(f"\n\nHello GitHub actions: ${output}\n\n")
    

if __name__ == "__main__":
    main()