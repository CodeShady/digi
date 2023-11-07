import argparse
import os
import json
import subprocess
import hashlib

# Globals
HOME_DIR_PATH = os.path.expanduser('~')
DATA_FILE_DIR_PATH = os.path.join(HOME_DIR_PATH, ".local/share/")
DATA_FILE = "data.json"

# Colors
class Color:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

# Functions
def info(text):
    print(f"INFO: {text}")

def ok():
    return Color.GREEN + "✅ OK!" + Color.RESET

def fail():
    return Color.RED + "🟥 FAIL" + Color.RESET

def warn():
    return Color.YELLOW + "🤔 WARN" + Color.RESET

def done():
    return Color.CYAN + "👍 DONE" + Color.RESET

def is_file(path):
    # Check if the path exists
    if not os.path.exists(path):
        return False
    
    # Check if the path is a file (not a directory)
    return os.path.isfile(path)

def download_latest_data():
    print("Getting latest data... ", end="")
    os.system("cp ~/Documents/Tools/data.json ~/.local/share")
    print(ok())

def md5sum(filename):
    return hashlib.md5(open(os.path.join(os.getcwd(), filename), "rb").read()).hexdigest()

def delete_file(filename):
    if is_file(filename):
        os.system("rm " + filename)

def cleanup():
    delete_file(".tmp_user_output")
    delete_file(".tmp_user_code.c")
    delete_file(".tmp_test_code")
    delete_file("a.out")

def run_command(command=[], show_output=False):
    console_command = subprocess.run(command, stdout=subprocess.PIPE)
    command_output  = console_command.stdout#.decode("utf-8")

    if show_output:
        print(command_output)

    return {
        "output": command_output,
        "returncode": console_command.returncode
    }


# Running different code files (c, bash, python, etc)
def run_program(filename, expectations):
    # Find what code type this file is
    
    # C Program
    if filename.endswith(".c"):
        # Compile & run
        if run_command(["norminette", filename])["returncode"] != 0:
            print("Norminette " + fail())
            return
        
        print("Norminette " + ok())
        run_command(["cp", filename, ".tmp_user_code.c"])
        os.system("echo \"" + expectations["test_code_b64"] + "\" | base64 -d >> .tmp_test_code")
        os.system("cat .tmp_test_code >> .tmp_user_code.c")
        
        info("Using test code:")
        os.system("bat .tmp_test_code --style=grid -l c --theme=\"TwoDark\"")
        
        # Compling & Running
        if run_command(["cc", "-Wall", "-Wextra", "-Werror", ".tmp_user_code.c"])["statuscode"] != 0:
            print("Compiling " + fail())
            return

        print("Compiling " + ok())
        os.system("./a.out > .tmp_user_output")
        
        # Comparing checksums
        print("Expected:\t" + Color.GREEN + expectations["expected"]["hash"] + Color.RESET)
    
        if md5sum(".tmp_user_output") == expectations["expected"]["hash"]:
            print("Returned:\t" + Color.GREEN + md5sum(".tmp_user_output") + Color.RESET)
            print("\n" + ok())
        else:
            print("Returned:\t" + Color.RED + md5sum(".tmp_user_output") + Color.RESET)
            print("\n" + fail())

# Main
if __name__ == "__main__":
    # Set up arguments
    parser = argparse.ArgumentParser()

    # CLI Arguments
    parser.add_argument("file", help="Your code file")

    # Parse arguments
    args = parser.parse_args()

    # Download latest data pack
    download_latest_data()

    # Open data file
    with open(os.path.join(DATA_FILE_DIR_PATH, DATA_FILE), "r") as data_file:
        # Parse the json data file
        json_data = json.load(data_file)

        # Find the argument file passed in in the data file
        if args.file in json_data["projects"]:
            run_program(args.file, json_data["projects"][args.file])
            cleanup()
        else:
            print("No projects found with that file name!")

