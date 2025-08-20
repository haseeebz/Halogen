

## Quickstart

This is a guide on how to install and run halogen.

## Installation


#### First clone the repo

Using HTTPS:
```bash
git clone https://github.com/haseeebz/Halogen.git
```
Using SSH:
```bash
git clone git@github.com:haseeebz/Halogen.git
```

#### Then run the install script

For Linux, Windows and MacOS:

```bash
cd Halogen
python3 install.py
```
What this script would do:
+ Create a virtual python environment.
+ Install all dependancies currently needed.
+ Install the 'halogen' python package.
+ Creates OS-specific config directories/folders for Halogen.

> [!TIP]
> For Windows users, I'd recomend using WSL if you encounter any issue.

### Running Halogen

You can run the halogen (daemon) by using the command.
```bash
halogen
```
You can also use a specfic config directory.
```bash
halogen --configdir config
```

`--configdir` is used to specify the config directory to load. The above example uses the **config** directory present in the repo, if you're still in the same working directory.

### But...

This won't really be useful since you probably have no model connected.

