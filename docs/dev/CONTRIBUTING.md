
## How to Contribute


### Installation

You should probably install first if you want to contribute. See [quickstart.md](/docs/quickstart.md).


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