## git la!

[![demo](https://asciinema.org/a/281692.svg)](https://asciinema.org/a/281692)

git-la can help to pick files from a large directory that you don't want to run `git init`, and organized them as *project based*.
git-la will create hard link for any file that you want to add in a specified directory and able to run 
all available git command for the specific project.

### Running git-la
```bash
# create new project called `sample-project`
git-la new sample-project
# use `add-sym` for creating hard link.
git-la cmd sample-project add-sym sample.md
# all other git commands can be issue
git-la cmd sample-project status
git-la cmd sample-project log
```

Git-la achieve this by creating a hard-link file to the project directory, and redirect all git command to git itself.
Git-la store the project specification file by default in `~/.gitla.json`, which is a simple json to map the project name 
to it's git directory. It will also create project git repository in `~/.git_la/` by default.

### To be implement
[] deleting project
[] symlink to folder (by specifying root)
[] check link status (can't check with hardlink right now)