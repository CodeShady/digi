#  __     __             __   ___ ___       ___ __
# |  \ | |  \     |     / _` |__   |      |  |   _|
# |__/ | |__/ ___ | ___ \__> |___  |  ___ |  |   .
# 
# By CodeShady (ftp)
# https://github.com/CodeShady/digi

import argparse
import os, sys
import json
import subprocess
import hashlib
import random

# Globals
HOME_DIR_PATH = os.path.expanduser('~')
DATA_FILE_DIR_PATH = os.path.join(HOME_DIR_PATH, ".local/share/")
DATA_FILE = "data.json"
CURRENT_VERSION = "1.0"

# Colors
class Color:
    # Text colors
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[0m'

    # Backgrounds
    BLACK_BACKGROUND = "\033[40m"  # BLACK
    RED_BACKGROUND = "\033[41m"    # RED
    GREEN_BACKGROUND = "\033[42m"  # GREEN
    YELLOW_BACKGROUND = "\033[43m" # YELLOW
    BLUE_BACKGROUND = "\033[44m"   # BLUE
    PURPLE_BACKGROUND = "\033[45m" # PURPLE
    CYAN_BACKGROUND = "\033[46m"   # CYAN
    WHITE_BACKGROUND = "\033[47m"  # WHITE


# Functions
def logo():
    print(Color.RED + """ __     __             __   ___ ___       ___ __ 
|  \ | |  \     |     / _` |__   |      |  |   _|
|__/ | |__/ ___ | ___ \__> |___  |  ___ |  |   .""" + Color.RESET + "  (by cs)\n")

def ok(message=None):
    if message != None:
        print(message, end=" ")
    print(Color.GREEN + "✅ OK!" + Color.RESET)

def fail(message=None):
    if message != None:
        print(message, end=" ")
    print(Color.RED + "🟥 FAIL" + Color.RESET)

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
    print("Getting latest data...", end="\r")
    os.system("cp /Users/finnt-p/Workspace/Documents/GitHub/digi/data.json ~/.local/share")
    ok("Getting latest data")

def friendly_message(json_data, has_failed=False):
    if has_failed:
        # You've failed, but keep going messages!
        return random.choice(json_data["encouragement_fail"])
    else:
        # Success messages!
        return random.choice(json_data["encouragement_ok"])

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
def run_program(filename, json_data):
    # Find what code type this file is
    
    # C Program
    if filename.endswith(".c"):
        # Compile & run
        if run_command(["norminette", filename])["returncode"] != 0:
            fail("Norminette")
            return
        
        ok("Norminette ")
        run_command(["cp", filename, ".tmp_user_code.c"])
        os.system("echo \"" + json_data["projects"][filename]["test_code_b64"] + "\" | base64 -d >> .tmp_test_code")
        os.system("cat .tmp_test_code >> .tmp_user_code.c")
        
        print("Using Test Code ⬇️")
        os.system("bat .tmp_test_code --style=grid -l c --theme=\"TwoDark\"")
        
        # Compling & Running
        if run_command(["cc", "-Wall", "-Wextra", "-Werror", ".tmp_user_code.c"])["returncode"] != 0:
            fail("Compiling")
            return

        ok("Compiling")
        os.system("./a.out > .tmp_user_output")
        
        # Comparing checksums
        print("Expected:\t" + Color.GREEN + json_data["projects"][filename]["expected"]["hash"] + Color.RESET, end=" ")
        
        # If the "verified" flag was set for this project, then somebody has used the same output to
        # pass the grader, so it's verified as the correct output.
        if json_data["projects"][filename]["verified"] == "Yes":
            print("(" + Color.GREEN + "Verified" + Color.RESET + ")")
        else:
            print("(" + Color.RED + "Not Verified" + Color.RESET + ")")
    
        if md5sum(".tmp_user_output") == json_data["projects"][filename]["expected"]["hash"]:
            print("Returned:\t" + Color.GREEN + md5sum(".tmp_user_output") + Color.RESET, end="\n\n")
            print(Color.GREEN + friendly_message(json_data, has_failed=False) + Color.RESET, end="\n\n")
            ok()
        else:
            print("Returned:\t" + Color.RED + md5sum(".tmp_user_output") + Color.RESET, end="\n\n")
            print(Color.YELLOW + friendly_message(json_data, has_failed=True) + Color.RESET, end="\n\n")
            fail()

# Main
if __name__ == "__main__":
    # Firstly, cleanup any files left by the script before
    cleanup()

    # Show the banner/logo
    logo()

    # Set up arguments
    parser = argparse.ArgumentParser()

    # CLI Arguments
    parser.add_argument("file", help="Your code file")

    # Parse arguments
    args = parser.parse_args()

    # Check if the passed in file exists
    if not is_file(args.file):
        print(args.file + " doesn't exist!")
        sys.exit(1)

    # Download latest data pack
    download_latest_data()

    # Open data file
    with open(os.path.join(DATA_FILE_DIR_PATH, DATA_FILE), "r") as data_file:
        # Parse the json data file
        json_data = json.load(data_file)

        # Check if this program is the latest version or
        # if there's an update avaliable
        if json_data["latest_version"] != CURRENT_VERSION:
            print("")
            print(Color.RED_BACKGROUND + "!!! A new update is available for this script !!!" + Color.RESET)
            print(Color.YELLOW + ">>> Get the latest script here >>> github.com/CodeShady/digi" + Color.RESET)
            print("")

        # Find the argument file passed in in the data file
        if args.file in json_data["projects"]:
            run_program(args.file, json_data)
            cleanup()
        else:
            print("No projects found with that file name!")
