# CME495 Capstone
GPS Frequency Reference Recovery with Long Term Holdover

## Table of Contents
1. [Repo Setup](#Repo-Setup)
2. [Project Workflow](#Project-Workflow)
    1. [Branching](#Branching)
    2. [Repo Commits](#Repo-Commits)
    3. [Merge Conflicts](#Merge-Conflicts)
3. [Get Remote Repo Info](#Get-Remote-Repo-Info)

## Repo Setup
1. Configure your git name and email.
    1. ```git config --global user.name "<your name>"```
    2. ```git config --global user.email "<your email>"```
2. Add your ssh key to GitHub
    1. Run ```ssh-keygen``` and procede with defaults to generate an SSH key
    2. Copy your SSH key with ```cat ~/.ssh/id_rsa.pub```
    3. Paste into GitHub in ```Settings -> SSH and GPG Keys```
3. Clone Repo
    1. ```cd``` to where you want the repo to be
    2. Run ```git clone https://github.com/mpbtruong/CME495.git```
    3. ```cd CME495```

## Project Workflow

### Branching
1. Create a checkout a branch with ```git checkout -b <branch name>```
2. Upload branch to remote repo with ```git push -u origin```
3. See all branches with ```git branch -a```

### Repo Commits
1. Pull from remote repo with ```git pull```
2. Stage all changes with ```git add .``` or some files with ```git add <file_1> <file_2> <file_n>```
3. Check files were staged with ```git status```
4. Commit with ```git commit -m "<commit message>"```
5. Push to remote with ```git push```

### Merge Conflicts
1. It is recommended to use an editor like VS Code. In the event of a merge conflict:
    1. Sometimes a merge conflict will happen on ```git pull```
    2. A vim editor will appear, type ```i``` to enter insert mode and then type a message such as ```Merge fix``` where the        blue # lines are.
    3. Save and exit with ```esc -> :wq -> return```
    4. If git cannot resolve conflicts, a side-by-side view (VS Code) will appear. Manually merge the code files by                following the prompts.
    5. Push to remote with ```git push```

### Get Remote Repo Info
1. ```git remote show origin```

