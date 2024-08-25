from urllib.request import urlopen, Request, urlretrieve
import re, subprocess, base64, json
import time, progressbar, os
import streamtape as api
import mediafire_dl

hdr = {"User-Agent": "Mozilla/5.0"}
serverList = ['streamwish.to','mp4upload','ok.ru' ]
btoa = lambda x:base64.b64decode(x)

def clear():
	subprocess.run(['clear'])
class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

class Episode:
	def __init__(self, title:str, tag:str, number:int, site:str):
		self.tag = tag
		self.number = number
		self.site = site
		if bool(re.search('Season \d', title)):
			self.title = re.sub(' Season \d','', title)
			self.season = int(re.search('\d', title).group(0))
		else:
			self.title = title
			self.season = 1

		if site=="animeflv":
			self.url = f"https://www3.animeflv.net/ver/{tag}-{number}"
			request_url = Request(self.url, headers=hdr)
			self.code = urlopen(request_url).read().decode("utf-8")
			server = re.findall('"code":"(.*?)"', self.code)
			server = [url.replace('\\/', '/') for url in server]
			key = []
			for i in range(len(server)):
				key.append(re.findall('https:\/\/(.*?)\/', server[i])[0])
			self.serverlist = dict(zip(key, server))
		if site=="latanime":
			self.url = f"https://latanime.org/ver/{tag}-episodio-{number}"
			request_url = Request(self.url, headers=hdr)
			self.code = urlopen(request_url).read().decode("utf-8")
			server = re.findall('"(https://(www.mediafire|mega.nz).*?)"', self.code)
			#server = [url.replace('\\/', '/') for url in server]
			key = []
			players = {}
			for p in re.findall('player=(.*?)<', self.code):
				url, player = p.split('>')
				url = url.replace('"', '')
				url = btoa(url).decode('utf-8')
				players.update({player:url})
			for p in server:
				players.update({p[1]:p[0]}) 
			self.serverlist = players


	def Download(self, server,overwrite):
		os.chdir("{os.environ['HOME']}/Media/Anime")
		path = f'{self.title}/Season {self.season:02d}/Episode S{self.season:02d}E{self.number:02d}.mp4'
		print(path)
		if not os.path.isdir(f'{self.title}/Season {self.season:02d}'):
			os.makedirs(f'{self.title}/Season {self.season:02d}')
		if not os.path.isfile(path) or overwrite:
			if server=='mega.nz':
				link = self.serverlist['mega.nz'].replace('embed/!', 'file/').replace("!","#")
				Mega_dl(link, path)
			elif server=='streamwish.to':
				link = self.serverlist['streamwish.to']
				Streamwish_dl(link, path)
			elif server=='www.mediafire':
				link = self.serverlist['www.mediafire']
				Mediafire_dl(link, path)
			elif server=='streamtape.com':
				link = self.serverlist['streamtape.com']
				Streamtape_dl(link, path)
	   
	def Play(self, server=None, time=None):
		arg_cmd = ['mpv']
		arg_cmd.append(f'--title="Episode S{self.season:02d}E{self.number:02d}"')
		if time!=None:
			arg_cmd.append(f'--start={time}')
		for server in self.serverlist:
			if server in serverList:
				arg_cmd.append(self.serverlist[server])
				print(" ".join(arg_cmd))  
				os.system(" ".join(arg_cmd))
				break

class TVShow:
	def __init__(self, tag:str, site:str):
		self.tag = tag
		self.site = site
		if site=="animeflv":
			url = f"https://www3.animeflv.net/anime/{tag}"
			request_url = Request(url, headers=hdr)
			source_code = urlopen(request_url).read().decode("utf-8")
			search_chapters = re.findall('episodes = \[(.*?)\];', source_code)[0]
			search_chapters = search_chapters.replace('[', '').split(',')
			self.cover = re.findall("cover.*?jpg", source_code)[0]
			self.title = re.findall('Ver (.*?) Online —', source_code)[0]
			self.min = int(search_chapters[-2])
			self.max = int(search_chapters[0])
		if site=="latanime":
			url = f"https://latanime.org/anime/{tag}"
			request_url = Request(url, headers=hdr)
			source_code = urlopen(request_url).read().decode("utf-8")
			url2chapter = re.findall('"(.*?episodio-\d*)"', source_code)
			self.title = re.findall('<h2>(.*?)</h2>', source_code)[0]
			self.min = 1
			self.max = len(url2chapter)


class Search:
	def __init__(self, keywords:str, site:str):
		self.site = site
		if site=="animeflv":
			url = f"https://www3.animeflv.net/browse?q={keywords.replace(' ','+')}"
			request_url = Request(url, headers=hdr)
			source_code = urlopen(request_url).read().decode("utf-8")
			search_res = re.findall('"\/anime\/(.*?)">VER', source_code)
			self.search_res = search_res
		if 	site=="latanime":	
			url = f"https://latanime.org/buscar?q={keywords.replace(' ','+')}"
			request_url = Request(url, headers=hdr)
			source_code = urlopen(request_url).read().decode("utf-8")
			search_res = re.findall('"https://latanime.org/anime/(.*?)"', source_code)
			self.search_res = search_res


class Session:
	def __init__(self, sites:list, user:str="default"):
		self.sites = sites
		self.user = user
	
	def Search_keywords(self, keywords):
		self.search_results = []
		self.search_sites = []
		for site in self.sites:
			searchlist = Search(keywords, site)
			for res in searchlist.search_res:
				self.search_results.append(res)
				self.search_sites.append(site)

	def Select(self, res:int):
		return TVShow(self.search_results[res], self.search_sites[res])

def Mega_dl(link,path):
	arg_cmd = ['megadl',f'--path="{path}"', f'{link}']
	print(' '.join(arg_cmd))
	os.system(" ".join(arg_cmd))

def Streamwish_dl(link, path):
	print(link)
	os.system(f'yt-dlp -o "{path}" "{link}"')

def Mediafire_dl(link, path):
	print(link)
	mediafire_dl.download(link, path, quiet=False)

def Streamtape_dl(link,path):
	file_id=link.split('/')[4]
	login, key = open("key.csv","r").read().splitlines()
	ticket_data = api.get_download_ticket(file_id, login, key)
	ticket_data=ticket_data['result']
	time.sleep(ticket_data['wait_time'])
	download_ticket=ticket_data['ticket']
	data = api.get_download_link(file_id, download_ticket)
	if data['result']==None:
		return 0
	url_download = data['result']['url']
	print('Descargando '+link)
	urlretrieve(url_download, path, MyProgressBar())
	

