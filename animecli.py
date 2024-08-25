from functions import *
import argparse
from simple_term_menu import TerminalMenu
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--download', action='store_true')
parser.add_argument('-a', '--autoplay', action='store_true')
parser.add_argument('--server', default='stream')
parser.add_argument('--site', default='animeflv')
parser.add_argument('--overwrite', action='store_true')
parser.add_argument('-st', '--start-time', type=str, default="00:00:00")
args = parser.parse_args()

#1
clear()
keywords = input('search anime: ')
session = Session(args.site.split(","))
session.Search_keywords(keywords)
servers = {"mega":"mega.nz", "stape":"streamtape.com", "stream":"streamwish.to", "mediafire":"www.mediafire"}
downloader = servers[args.server]


terminal_menu = TerminalMenu(session.search_results, show_search_hint=True)
menu_entry_index = terminal_menu.show()
if menu_entry_index==None:
	clear()
	exit()
anime = session.Select(menu_entry_index)


#2
episodes = [f"Episode {i}" for i in range(anime.min, anime.max)]

if args.autoplay:
	number = int(input('from: '))
	end = int(input('to: '))
	end = min(int(anime.max), end)
else:
	terminal_menu = TerminalMenu(episodes, show_search_hint=True, preview_title=anime.title)
	menu_entry_index = terminal_menu.show()
	if menu_entry_index==None:
		clear()
		exit()
	number = menu_entry_index+1
	end = int(anime.max)
#3 

while number<=end:

	episode = Episode(anime.title, anime.tag, number, anime.site)
	if args.download:
		episode.Download(downloader, args.overwrite)
	else:
		episode.Play(time=args.start_time)


	if args.autoplay:
		number = number+1
		continue
	clear()
	#print('episode:', number)
	terminal_menu = TerminalMenu([f"Next (Episode {number+1})", "Select Episode", "Quit"])
	state = terminal_menu.show()
	if state==0:
		number = number+1
	elif state==1:
			terminal_menu = TerminalMenu(episodes, show_search_hint=True, preview_title=anime.title)
			menu_entry_index = terminal_menu.show()
			if menu_entry_index==None:
				clear()
				exit()
			number = menu_entry_index+1
	else:
		clear()
		exit()
		
