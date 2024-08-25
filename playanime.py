import os
from simple_term_menu import TerminalMenu
os.system("clear")
def quit(index):
	if index==None:
		exit()
directory = f"{os.environ['HOME']}/Media/Anime"
list_files = os.listdir(directory)

terminal_menu = TerminalMenu(list_files)
index = terminal_menu.show()
quit(index)

directory = f"{directory}/{list_files[index]}"
list_files = sorted(os.listdir(directory))

terminal_menu = TerminalMenu(list_files)
index = terminal_menu.show()
quit(index)

directory = f"{directory}/{list_files[index]}"
list_files = sorted(os.listdir(directory))

terminal_menu = TerminalMenu(list_files)
index = terminal_menu.show()
quit(index)

while index<len(list_files):
	os.system(f'mpv --quiet "{directory}/{list_files[index]}"')
	os.system("clear")
	menu = TerminalMenu([f"Next (Episode {index+2})", "Quit"])
	state = menu.show()
	quit(state)
	index+=1
	if state==1:
		exit()