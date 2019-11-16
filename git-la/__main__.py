import configparser
import subprocess
import json
import pathlib
import os
import sys
import argparse


JSON_RECORD_FILE = ".gitla.json"


def handle_new(args):
    base_dir = pathlib.Path(args.path) / args.project_name
    base_dir.mkdir(parents=True, exist_ok=True)
    json_record_file = pathlib.Path(str(args.json)) if args.json else pathlib.Path(os.environ["HOME"]) / JSON_RECORD_FILE
    git_la = GitLa(json_record_file)
    git_la.add_new_project(args.project_name, base_dir)


def git_add(project_path: str, *args):
    project_path = pathlib.Path(project_path)
    new_links = []
    for f in args:
        f = pathlib.Path(f).resolve()
        new_link = project_path / f.name
        if new_link.exists():
            new_link.unlink()
        os.link(str(f), str(new_link))
        new_links.append(str(new_link))
    subprocess.check_output(["git", "add"] + new_links, cwd=str(project_path))


GIT_EXTENSION = {"add": git_add}


def handle_cmd(args):
    json_record_file = pathlib.Path(str(args.json)) if args.json else pathlib.Path(os.environ["HOME"]) / JSON_RECORD_FILE
    git_la = GitLa(json_record_file)
    project_name = args.commands[0]
    if len(args.commands) >= 2:
        commands = args.commands[1:]
    else:
        raise ValueError("please specify the git commands after the project name!")
    path = git_la.json_records.get(project_name)
    try:
        extension_func = GIT_EXTENSION[commands[0]]
        extension_func(path, *commands[1:])
    except KeyError:
        commands.insert(0, "git")
        status = subprocess.check_output(commands, cwd=str(path))
        print(status.decode("utf-8"))


def _parse_optional(parser):
    parser.add_argument("--json", type=argparse.FileType("w"), help="specify the json database file")


def _parse_new(parser):
    parser.add_argument("project_name", type=str, help="Create new project")
    parser.add_argument("-p", "--path", type=str, default="{}/.git_la".format(os.environ["HOME"]),
                        help="Specify the path to store this projects")


def _parse_cmd(parser):
    parser.add_argument("commands", type=str, nargs="*", help="issue git command to the project specified")


class GitLa:
    def __init__(self, record_path: pathlib.Path):
        self.record_path = record_path
        if record_path.exists():
            self.json_records = self.read_json_record()
        else:
            self.json_records = {}
            record_path.touch()

    def read_json_record(self):
        f_record = self.record_path
        json_record = json.loads(f_record.read_text())
        return json_record

    def write_json_record(self):
        self.record_path.write_text(json.dumps(self.json_records))

    def add_new_project(self, project_name: str, path: pathlib.Path):
        if project_name in self.json_records:
            raise ValueError("{} already exists.".format(project_name))
        self.json_records[project_name] = str(path)
        self.write_json_record()
        subprocess.check_output(["git", "init"], cwd=str(path))
        # set core.symlink = False in .git/config
        git_config_path = str(path / ".git" / "config")
        config = configparser.ConfigParser()
        config.read(git_config_path)
        config["core"]["symlink"] = "false"
        with open(git_config_path, "w") as f:
            config.write(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    _parse_optional(parser)
    sub_parser = parser.add_subparsers()
    parser_new = sub_parser.add_parser("new")
    parser_new.set_defaults(func=handle_new)
    _parse_new(parser_new)
    parser_cmd = sub_parser.add_parser("cmd")
    parser_cmd.set_defaults(func=handle_cmd)
    _parse_cmd(parser_cmd)
    args = parser.parse_args(sys.argv[1:])
    args.func(args)
