import re
import sys
import base64
import json
import os
import hashlib

# List of C libraries included in the test base64 code
C_LIBS = [
    "stdio.h",
    "unistd.h",
    "string.h"
]
DATA_FILE_PATH = os.path.join("/Users/finnt-p/Workspace/Documents/GitHub/digi/", "data.json")

# Functions
def delete(filename):
    if os.path.isfile(filename):
        os.system(f"rm {filename}")

# Arguments
if len(sys.argv) < 2:
    print("Usage: python script.py <filename.c>")
    sys.exit(1)

# Get filename argument
filename = sys.argv[1]

# Open the file
with open(filename, "r") as file:
    c_code = file.read()

# Find the main function
match = re.search(r'(int\s+main\s*\([^)]*\)\s*{[^}]*})', c_code, re.DOTALL)

# Check if there was a match
if match:
    # Successful match!
    main_function_code = match.group(1)

    # Add all libraries possibly used
    for library_name in C_LIBS:
        main_function_code = "#include <" + library_name + ">\n" + main_function_code
    
    # Convert the main function to a base64 string
    base64_string = base64.b64encode(main_function_code.encode()).decode()

    # Compile the original code to find the expected hash output
    os.system(f"cc -Wall -Wextra -Werror {filename}")
    os.system("./a.out > .tmp_user_a.out")

    print(main_function_code)

    # Open data.json
    with open(DATA_FILE_PATH, "r") as data_file:
        # Load json
        json_data = json.load(data_file)

        # Edit data in the object
        json_data["projects"][filename] = {
            "test_code_b64": base64_string,
            "verified": "No",
            "expected": {
                "hash": hashlib.md5(open(".tmp_user_a.out", "rb").read()).hexdigest()
            }
        }

        # Close this file
        data_file.close()

        # Open this file in write mode
        with open(DATA_FILE_PATH, "w") as write_file:
            # Save the new json data
            json.dump(json_data, write_file, indent=4)

    # Cleanup
    delete("a.out")
    delete(".tmp_user_a.out")

else:
    print("Main function not found! (Required)")