A list of all planned features (will add more to this list!)

### Core Stuff

+ Hot reloading modules.
+ Loading them dynamically from a directory instead of the current python module hack.
+ Also pass the "user" field in config along with the scoped field to a module.


### Functionality

+ Add a proper task manager and task execution.
+ Routines which remind the AI to do some task or to remind the user.
+ Maybe add the option for indicating whether a task should be threaded, multiprocessed or maybe just ran in the main loop.

### Prompts

+ Add more modular prompt formation, i.e have a proper memory system, tasks list.
+ Add persistent memory
+ Add different types of modes? like normal mode, command mode, inspection mode etc
+ Maybe keep track of all the chat contexts in case of multiple clients, each having their own chat?

### Clients

+ Make it so that each new client generates a new "chat" or make it so that the chat is universal among all the clients aka a singular chat through out all clients.
+ Maybe add chat restore option?


### Models

+ Make the Gemini model more error prone.
+ Add other model providers like OpenAI, Deepseek etc. Also a local model provider like Ollama.
+ Hot reloading and switching providers.
+ Add a command to change the actual model of a provider? We can do this easily by asking each model provider to return a list/set of all the models they provide. Very useful for local providers.

### Task Modules

+ Filesystem
+ Applications (opening apps etc)
+ System control (brightness, sound etc.), easy on linux but might need more effort on windows

### IPC

+ Server/Client fails to parse json when repeated events are sent at the same time.
+ The above is likely due to the fact that the current ctl follows the "One output for a single input" philosphy which means that other events are just stuck in the queue. This includes other AI response events which causes the crash.
+ (**ONGOING**) So fix the ctl to either be a tui which can display events without blocking for user input. This is easy because the client side already receives events in a non-blocking way.
+ Maybe make a GUI one day.

### Development

+ Add --dev.
+ Add dev.modules which will be used to load modules.