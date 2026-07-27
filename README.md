This script/bot automates the task of booking training sessions.
It only works for an specific web, crossfit box & preferences of training class, date and time.

requirements.txt specifies the libraries that are used in order for the script to work and its versions.
It will be updated every time a change or update is made.

.env.example shows the content of the .env file and its structure.
This file should contain the values you want the script to use.

main.py, config.py, classes_management.py & booking.py contain the code for the automatization of the task.

To run the script autonomously, simply open a CMD(for Windows), navigate to the folder using the 'cd' command and execute 'python main.py'.
Once this is done, as long as the task is not stoped and the computer is not turned off, it will continue to run on the specified hour forever.

*If the libaries have been installed in an enviroment, before running the python main.py command activate the enviroment: venv\Scripts\activate.bat*

