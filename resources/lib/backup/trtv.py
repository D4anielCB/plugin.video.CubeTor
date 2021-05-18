# -*- coding: utf-8 -*-
import xbmc
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, json, hashlib, re, unicodedata, math, xbmcvfs
import shutil
from urllib.parse import urlparse, quote_plus, unquote
from urllib.request import urlopen, Request
import urllib.request, urllib.parse, urllib.error
import urllib.parse

from metadatautils import MetadataUtils
mg = MetadataUtils()
mg.tmdb.api_key = 'bd6af17904b638d482df1a924f1eabb4'

AddonID = 'plugin.video.CubeTor'
Addon = xbmcaddon.Addon(AddonID)
AddonName = Addon.getAddonInfo("name")
addonDir = Addon.getAddonInfo('path')
icon = os.path.join(addonDir,"icon.png")
iconsDir = os.path.join(addonDir, "resources", "images")

libDir = os.path.join(addonDir, 'resources', 'lib')
sys.path.insert(0, libDir)
import xx, download

MUlang = "pt-BR" if Addon.getSetting("MUlang") == "1" else "en"
MUcache = True if Addon.getSetting("MUcache") == "true" else False
MUcacheEpi = True if Addon.getSetting("MUcacheEpi") == "true" else False
MUfanArt = True if Addon.getSetting("MUfanArt") == "true" else False
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else None
cDirtrtv = Addon.getSetting("cDirtrtv") if Addon.getSetting("cDirtrtv") != "" else ""
cDirtrtvDown = Addon.getSetting("cDirtrtvDown") if Addon.getSetting("cDirtrtvDown") != "" else ""

addon_data_dir = xbmcvfs.translatePath(Addon.getAddonInfo("profile"))
cacheDir = os.path.join(addon_data_dir, "cache")
#-----------------------------------------
params = urllib.parse.parse_qs(sys.argv[2][1:])
name = params.get('name',[None])[0]
url = params.get('url',[None])[0]
mode = params.get('mode',[None])[0]
iconimage = params.get('iconimage',[None])[0]
logos = params.get('logos',[None])[0]
info = params.get('info',[None])[0]
dados = params.get('dados',[{}])[0]
#-----------------------------------------
def Categories():
	#xx.AddDir("Episodes", "", "trtv.Episodes", isFolder=True)
	xx.AddDir("Series", "", "trtv.SeriesFolder", isFolder=True)
	xx.AddDir("Filmes", "", "trtv.MoviesFolder", isFolder=True)
	xx.AddDir("Stop", "", "download.StopDownload", isFolder=False)
	xx.AddDir("Busca", "", "trtv.Busca", isFolder=True)
def SeriesFolder():
	xx.AddDir("Reload", "", "Reload", isFolder=False, IsPlayable=False)
	trak = xx.traktS()
	entries = os.listdir(cDirtrtvDown)
	joined = "\n".join(entries)
	tmdb = re.findall('T(\d+).+?.mp4', joined)
	entries = list(dict.fromkeys(tmdb))
	for entry in entries:
		meta = mg.get_tvshow_details(title="", tmdb_id=entry, ignore_cache=MUcache, lang=MUlang)
		xx.AddDir(meta[-1]["TVShowTitle"], entry, "trtv.EpisodesFolder", isFolder=True, dados={'meta': meta[-1]})

def EpisodesFolder():
	xx.AddDir("Reload", "", "Reload", isFolder=False, IsPlayable=False)
	trak = xx.traktS()
	entries = os.listdir(cDirtrtvDown)
	for entry in entries:
		if url in entry and ".mp4" in entry:
			file = unquote(entry)
			tmdb = re.compile("\d+").findall(file)
			SeaEpi = re.compile(" S.*?.?(\d+).*?E.*?(\d+)").findall(file)
			meta = mg.get_tvshow_details(title="", tmdb_id=tmdb[0], ignore_cache=MUcache, lang=MUlang)
			meta['mediatype'] = "episode"
			pc = 1 if tmdb[0]+SeaEpi[0][0]+SeaEpi[0][1] in trak else None
			try:
				#play = cDirtrtvDown+"//"+entry
				play = os.path.join( cDirtrtvDown, entry)
				#play = "https://s0.blogspotting.art/web-sources/8C49366FDF6C9762/1575177/file|referer=http://trailers.to"
				xx.AddDir(meta[-1]["TVShowTitle"], play, "PlayUrlLeg", isFolder=False, IsPlayable=True, dados={'meta': meta[-1], 'season': SeaEpi[0][0], 'episode': SeaEpi[0][1], 'pc': pc})
			except:
				pass
def MoviesFolder():
	xx.AddDir("Reload", "", "Reload", isFolder=False, IsPlayable=False)
	entries = os.listdir(cDirtrtvDown)
	joined = "\n".join(entries)
	tmdb = re.findall('(M(\d+).+?.mp4)', joined)
	for entry in tmdb:
		file = entry[0]
		if ".mp4" in file:
			play = os.path.join( cDirtrtvDown, file)
			try:
				mm = mg.get_tmdb_details(tmdb_id=entry[1], imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False)
				xx.AddDir(file, play, "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			except:
				pass
			#xx.AddDir(mm['title'], "plugin://plugin.video.elementum/play?uri="+entry['magnet']+"&doresume=true&type=movie"+entry['imdb'], "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
def Busca():
	q = xbmcgui.Dialog().input("O que busca?")
	link = OpenURL("https://trailers.to/en/popular/movies-tvshows-collections?q="+quote_plus(q))
	#link ='</span></a>\n<a href="/en/tvshow/19158/the-resident-2018">\nThe Resident\n</a>\n<div><span class="small-text font-weight-sbold"></span></div>\n</h5>\n<div>\n<span class="icon mdi mdi-calendar-blank"></span><span class="small-text font-weight-sbold">Jan 21, 2018</span>\n</div>\n<div>\n<span class="icon mdi mdi-star-outline"></span><span class="small-text font-weight-sbold">8.5 / 10</span>\n-\n<span class="small-text">\n<a href="https://imdb.com/title/tt6483832/reviews?spoiler=hide&sort=helpful'
	entries = re.compile("figure\" href=\".en\/(movie|tvshow)\/(\d+).+?(tt\d+)").findall(link[0].replace('\n','').replace('\r',''))
	for entry in entries:
		if entry[0] == "movie":
			try:
				mm = mg.get_tmdb_details(tmdb_id="", imdb_id=entry[2], tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False)
				titulo = "M"+str(mm["tmdb_id"])+" "+mm["title"]
				xx.AddDir(mm["title"], entry[1], "trtv.DownloadMovie", isFolder=False, IsPlayable=False, dados={'mmeta': mm, 'titulo': titulo})
			except:
				pass
		elif entry[0] == "tvshow":
			try:
				external = xx.OpenURL("http://api.themoviedb.org/3/find/"+entry[2]+"?api_key=bd6af17904b638d482df1a924f1eabb4&external_source=imdb_id&append_to_response=external_ids,images,alternative_titles,seasons")
				externalj = json.loads(external)
				meta = mg.get_tvshow_details(title="", tmdb_id=str(externalj["tv_results"][0]["id"]), ignore_cache=MUcache, lang=MUlang)
				xx.AddDir(meta[-1]["TVShowTitle"], entry[1], "trtv.Episodes", isFolder=True, dados={'meta': meta[-1]})
			except:
				pass
			#break
	#entries = re.compile("(\".en\/(movie|tvshow).{500})").findall(link[0].replace('\n','').replace('\r',''))
	#entries =  re.match("en\/.{5,6}", link)
	#ST(entries)
def Episodes():
	xx.AddDir("Series", "", "trtv.SeriesFolder", isFolder=True)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	trak = xx.traktS()
	link = xx.OpenURL("https://trailers.to/en/tvshow/"+url+"/tvshow")
	entries = re.compile("\/en\/episode\/(\d+).{1,155}Season (\d+).{1,5}Episode (\d+)").findall(link.replace('\n','').replace('\r',''))
	prog = 1
	meta = eval(dados)
	meta[-1] = meta["meta"]
	meta[-1]['mediatype'] = "episode"
	for entry in entries:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			pc = 1 if meta[-1]["tmdb_id"]+entry[1]+entry[2] in trak else None
			titulo = "T"+meta[-1]["tmdb_id"]+" "+meta[-1]["TVShowTitle"]+" - S"+entry[1]+"E"+entry[2]
			#play = cDirtrtv+"/Shows/"+entry
			#play = "https://s0.blogspotting.art/web-sources/8C49366FDF6C9762/1575177/file|referer=http://trailers.to"
			xx.AddDir(meta[-1]["TVShowTitle"], entry[0], "trtv.DownloadEpi", isFolder=False, IsPlayable=False, dados={'meta': meta[-1], 'season': entry[1], 'episode': entry[2], 'pc': pc, 'titulo': titulo})
		except:
			pass
	progress.close()
def DownloadEpi():
	titulo = re.sub(r'[\\/*?:"<>|]',"",eval(dados)['titulo'])
	#ST(titulo)
	link = OpenURL("https://trailers.to/en/episode/"+url+"/link")
	key = re.compile("[0-9a-fA-F]{15,16}").findall(link[0])
	u = 'https://s0.blogspotting.art/web-sources/'+key[0]+'/'+url+'/file'
	file = os.path.join( cDirtrtvDown, titulo)
	download.StartDownload(u,file,"http://trailers.to")
	#ST(key)
def DownloadMovie():
	titulo = re.sub(r'[\\/*?:"<>|]',"",eval(dados)['titulo'])
	link = OpenURL("https://trailers.to/en/episode/"+url+"/link")
	key = re.compile("[0-9a-fA-F]{15,16}").findall(link[0])
	u = 'https://s0.blogspotting.art/web-sources/'+key[0]+'/'+url+'/file'
	file = os.path.join( cDirtrtvDown, titulo)
	download.StartDownload(u,file,"http://trailers.to")
#----------------------------------------
def OpenURL(url, headers={}, user_data={}, cookieJar=None, justCookie=False):
	from random import randrange
	req = Request(url)
	UA = 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/'+str(randrange(1, 999))+'.'+str(randrange(1, 999))
	req.add_header('User-Agent', UA)
	return [urlopen(req).read().decode("utf-8").replace("\r", ""), UA]
#----------------------------------------
def ST(x="", o="w"):
	if o == "1":
		o = "a+"
	if type(x) == type({}) or type(x) == type([]) or type(x) == type(set([''])):
		y = json.dumps(x, indent=4, ensure_ascii=True)
	else:
		y = str(str(x).encode("utf-8"))
	Path = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('path') )
	py = os.path.join( Path, "study.txt")
	#file = open(py, "a+")
	file = open(py, o)
	file.write(y+"\n"+str(type(x)))
	file.close()
#-----------------------------------------