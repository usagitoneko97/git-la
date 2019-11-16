#!/bin/env python3
import contextlib
import subprocess
import json
import pathlib
import os
import sys
import argparse


JSON_RECORD_FILE = ".gitla.json"


class GitLa:
    def __init__(self, record_path: pathlib.Path):
        self.record_path = record_path
        if record_path.exists():
            self.json_records = self.read_json_record()
        else:
            self.json_records = {}

    def read_json_record(self):
        f_record = self.record_path
        json_record = json.loads(f_record.read_text())
        return json_record

    def write_json_record(self):
        if not self.record_path.exists():
            self.record_path.touch()
        self.record_path.write_text(json.dumps(self.json_records))

    def add_new_project(self, project_name: str, path: pathlib.Path):
        if project_name in self.json_records:
            raise ValueError("{} already exists.".format(project_name))
        self.json_records[project_name] = str(path)
        self.write_json_record()
        subprocess.check_output(["git", "init"], cwd=str(path))

    def get_project(self, project_name):
        path = self.json_records.get(project_name)
        if not path:
            raise ValueError("{} does not exist in the record: {}".format(project_name, str(self.record_path)))
        return path


def handle_new(args):
    base_dir = pathlib.Path(args.path) / args.project_name
    base_dir.mkdir(parents=True, exist_ok=True)
    json_record_file = pathlib.Path(str(args.json)) if args.json else pathlib.Path(os.environ["HOME"]) / JSON_RECORD_FILE
    git_la = GitLa(json_record_file)
    git_la.add_new_project(args.project_name, base_dir)


def git_add_sym(project_path: str, *args):
    project_path = pathlib.Path(project_path)
    new_links = []
    for f in args:
        f = pathlib.Path(f).resolve()
        new_link = project_path / f.name
        if new_link.exists():
            new_link.unlink()
        os.link(str(f), str(new_link))
        print("linked {} ---> {}".format(str(new_link), str(f)))
        new_links.append(str(new_link))
    output = subprocess.check_output(["git", "add"] + new_links, cwd=str(project_path))
    print(output.decode("utf-8"))


GIT_EXTENSION = {"add-sym": git_add_sym}


@contextlib.contextmanager
def _temp_chdir(path):
    backup = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(backup)


def handle_cmd(args):
    json_record_file = pathlib.Path(str(args.json)) if args.json else pathlib.Path(os.environ["HOME"]) / JSON_RECORD_FILE
    git_la = GitLa(json_record_file)
    project_name = args.commands
    path = git_la.get_project(project_name)
    try:
        extension_func = GIT_EXTENSION[sys.argv[3]]
        extension_func(path, *sys.argv[4:])
    except KeyError:
        commands = sys.argv[3:]
        commands.insert(0, "git")
        with _temp_chdir(str(path)):
            os.system(" ".join("'{}'".format(str(r)) for r in commands))
    except IndexError:
        raise ValueError("issued git commands is not complete!")


def _parse_optional(parser):
    parser.add_argument("--json", type=argparse.FileType("w"), help="specify the project mapping file")


def _parse_new(parser):
    parser.add_argument("project_name", type=str, help="Create new project")
    parser.add_argument("-p", "--path", type=str, default="{}/.git_la".format(os.environ["HOME"]),
                        help="Specify the path to store this projects")


def _parse_cmd(parser):
    parser.add_argument("commands", type=str, help="issue git command to the project specified")


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
    args, _ = parser.parse_known_args(sys.argv[1:])
    args.func(args)
