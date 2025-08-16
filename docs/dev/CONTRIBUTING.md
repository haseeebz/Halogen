

### What Sapphire is about

I want Sapphire to be a modular platform that integrates with any LLM and can be enhanced with modules. 

## How to Contribute


### Installation

You should probably install first if you want to contribute...

#### First clone the repo

Using HTTPS:
```bash
git clone https://github.com/haseeebz/Sapphire.git
```
Using SSH:
```bash
git clone git@github.com:haseeebz/Sapphire.git
```

#### Then run the install script

For Linux, Windows and MacOS:

```bash
cd Sapphire
python3 install.py
```
What this script would do:
+ Create a virtual python environment.
+ Install all dependancies currently needed.
+ Install the 'sapphire' python package.
+ Creates OS-specific config directories/folders for Sapphire.

> [!TIP]
> For Windows users, I'd recomend using WSL if you encounter any issue.

### Running Sapphire

You can run the sapphire (daemon) by using the command.
```bash
sapphire
```
But while working on sapphire, you should run.
```bash
sapphire --dev --configdir config
```
+ `--dev` enables some dev features like error raising instead of suppressing when handling events.
+ `--configdir` is used to specify the config directory to load. The above example uses the **config** directory present in the repo.

### What is even going on?

The `sapphire` package consists of 4 main sub-modules which are:

+ `sapphire.core` which contains the core class of Sapphire. It starts sapphire, loads modules, handles and passes events.
+ `sapphire.base` contains the base definitions. Stuff like events, config, decos, base module class etc.
+ `sapphire.ctl` contains the client side code, a CLI for command passing and a TUI for actually using Sapphire.
+ `sapphire.modules` contains the core sapphire modules.

### Actually contributing 

> WIP