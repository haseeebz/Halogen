
## How to Contribute


### Installation

You should probably install first if you want to contribute...

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
But while working on halogen, you should run.
```bash
halogen --dev --configdir config
```
+ `--dev` enables some dev features like error raising instead of suppressing when handling events.
+ `--configdir` is used to specify the config directory to load. The above example uses the **config** directory present in the repo.


### Actually contributing 

To contribute on the project, you can make changes to your local repo, and then make a pull request.

Here are some guidelines:

+ Before making any kind of changes, please open an issue and explain what you plan to add/improve. 
+ Make sure that your changes only affect a certain part of halogen and DO NOT have multiple changes through out the code.
+ Contributing need not be to Halogen alone, you can contribute by making custom HalogenModules and HalogenModelProvider classes to increase functionality.


### Basic Halogen Structure

The `halogen` package consists of 4 main sub-modules which are:

+ `halogen.core` which contains the core class of Halogen. It starts halogen, loads modules, handles and passes events.
+ `halogen.base` contains the base definitions. Stuff like events, config, decos, base module class etc.
+ `halogen.ctl` contains a CLI for command passing and a TUI for actually using Halogen.
+ `halogen.modules` contains the core halogen modules.