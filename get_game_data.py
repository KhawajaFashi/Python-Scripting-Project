import os
import shutil
import json
import sys
from subprocess import PIPE, run

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "run"] # can use build instead of run to build the .exe without running it


def find_all_game_paths(source):
    game_path = []

    for roots, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_path.append(path)
        break
    return game_path


def get_name_from_path(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
    return new_names


def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)

    shutil.copytree(source, dest)


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def make_json_metadata(path, game_dirs):
    data = {"gameNames": game_dirs, "NumberofGames": len(game_dirs)}
    with open(path, "w") as file:
        json.dump(data, file)


def compile_game(path):
    code_file_Name = None
    for roots, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_Name = file
                break
        break

    if code_file_Name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_Name]
    run_command(path, command)


def run_command(path, command):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
        print(f"Result:\n{result.stdout}")
    except Exception as e:
        print("Error: ", e)
    os.chdir(cwd)


def main(source, target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source)
    new_game_dirs = get_name_from_path(game_paths, f"_{GAME_DIR_PATTERN}")
    # print(new_game_dirs)
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata(json_path, new_game_dirs)
    # print( game_paths)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass a source and target directory only")

    source, target = args[1:]
    main(source, target)
