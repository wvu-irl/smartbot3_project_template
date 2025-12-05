# Smartbot3
See [mobilerobotics.wvirl.com](https://mobilerobotics.wvirl.com) for
installation and usage instructions

## Getting This Repo
```bash
git clone --recurse-submodules https://github.com/wvu-irl/smartbot3_project_template
```

## Where to Add Your Code
It is recommended to make new python files (e.g. by copying the ones in `src/`)
and avoid editing existing files. This will make pulling updates later easier.

## Getting Updates
To update **both** the template repo (where this README.md is) and the
`smartbot_irl` package run the following in the template repo

```bash
git pull --all --recurse-submodules
```

If the above fails and you see an error about **merge conflicts** then you have changes
which would be **erased** by the git pull. If you want to force the update
(**THIS WILL DELETE YOUR CHANGES!**) run the following:

```bash
git fetch --recurse-submodules && git reset --hard origin/main && git submodule update --init --recursive
```