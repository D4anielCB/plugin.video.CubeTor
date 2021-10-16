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
import xx

MUlang = "pt-BR" if Addon.getSetting("MUlang") == "1" else "en"
MUcache = True if Addon.getSetting("MUcache") == "true" else False
MUcacheEpi = True if Addon.getSetting("MUcacheEpi") == "true" else False
MUfanArt = True if Addon.getSetting("MUfanArt") == "true" else False
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else ""

Cproxy = "https://cbplay.000webhostapp.com/nc/nc.php?u=" if Addon.getSetting("Cproxy") else ""

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
def ListSeries(elo='https://api.trakt.tv/users/'+Ctrakt+'/watched/shows?extended=noseasons',typeload = "DialogProgress"):
	try:
		headers = {'Content-Type': 'application/json','trakt-api-version': '2','trakt-api-key': '888a9d79a643b0f4e9f58b5d4c2b13ee6d8bd584bc72bff8b263f184e9b5ed5d'}
		response_body = xx.OpenURL(elo,headers=headers)
		entries=json.loads(response_body)
		prog = 1
		progress = eval("xbmcgui."+typeload+"()")
		progress.create('Carregando...')
		progress.update(0, "Carregando...")
		for entry in entries:
			#ST(entry['seasons'])
			try:
				if (progress.iscanceled()): break
			except:
				pass
			progtotal = int( 100*prog/(len(entries)) )
			progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
			prog+=1
			#titley = re.findall('(.+) \((\d+)\)', entry)
			meta = mg.get_tvshow_details(title="", tmdb_id=str(entry['show']['ids']['tmdb']), ignore_cache=MUcache, lang=MUlang)
			try:
				xx.AddDir(entry['show']['title'], str(entry['show']['ids']['tmdb']), "trakt.Shows", isFolder=True, dados={'meta': meta[-1]})
			except:
				pass
		progress.close()
	except:
		xx.AddDir("Trakt não configurado", "", "t", isFolder=False)
def ListMovies(elo='https://api.trakt.tv/users/'+Ctrakt+'/watchlist/movies/added',typeload = "DialogProgress"):
	trak = xx.traktM()
	headers = {'Content-Type': 'application/json','trakt-api-version': '2','trakt-api-key': '888a9d79a643b0f4e9f58b5d4c2b13ee6d8bd584bc72bff8b263f184e9b5ed5d'}
	response_body = xx.OpenURL(elo,headers=headers)
	#response_body = xx.OpenURL("https://api.themoviedb.org/3/watch/providers/movies?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&watch_region=AU")
	entries=json.loads(response_body)
	prog = 1
	progress = eval("xbmcgui."+typeload+"()")
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	for entry in entries:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/(len(entries)) )
		progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
		prog+=1
		try:
			mm = mg.get_tmdb_details(tmdb_id=str(entry["movie"]["ids"]["tmdb"]), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False)
			pc = 1 if str(mm["tmdb_id"]) in trak else None
			#pc = 0
			#ST(mm)
			#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			xx.AddDir("", str(entry["movie"]["ids"]["tmdb"]), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
		except:
			pass
		#break
def Shows():
	meta = eval(dados)["meta"]
	#options = []
	#options.append('Busca série em trailers.to')
	#options.append('Elementum')
	#sel = xbmcgui.Dialog().contextmenu(options)
	#if sel == 0:
	try:
		mdb = xx.OpenURL('http://api.themoviedb.org/3/tv/'+url+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=en')
		mdbj = json.loads(mdb)
		#trtv = xx.OpenURL("https://trailers.to/en/popular/movies-tvshows-collections?q="+quote_plus(mdbj["name"]))
		q = re.sub('[^A-Za-z0-9] +', ' ', mdbj["name"])
		q = re.sub('\-', '', q)
		if "premiered" in meta:
			year = re.sub('(\d{4}).+', r'+\1', meta["premiered"])
		else:
			year = ""
		#ST(year)
		trtv = xx.OpenURL(Cproxy + "https://trailers.to/en/quick-search?q="+quote_plus(q)+year)
		#ST(q)
		tvshow = re.compile("\/en\/tvshow\/(\d+)").findall(trtv)
		if tvshow:
			xx.AddDir(meta["TVShowTitle"]+" (Trailers.to - Play)", tvshow[0], "trtv.SeasonsPlay", isFolder=True, dados={'meta': meta})
			if cDirtrtvDown:
				xx.AddDir(meta["TVShowTitle"]+" (Trailers.to - Download)", tvshow[0], "trtv.Seasons", isFolder=True, dados={'meta': meta})
		else:
			xx.AddDir("Indisponível em Trailers.to", "", "", isFolder=False)
	except:
		xx.AddDir("Trailers.to pode estar offline", "", "", isFolder=False)
	dados2 = eval(dados)
	#xx.AddDir(meta["TVShowTitle"]+" (Torrents)", tvshow[0], "trtv.Seasons", isFolder=True, dados={'meta': meta})
	try:
		mmm = mg.get_tvshow_details(title="",tmdb_id=url, ignore_cache=MUcache, lang=MUlang)
		#metasea=xx.mergedicts(mmm[-1],mmm[season['season_number']])
		#ST(mmm[-1]["tmdb_id"])
		xx.AddDir(mmm[-1]["TVShowTitle"]+ " (Torrents)", mmm[-1]["tmdb_id"], "trakt.Seasons", isFolder=True, dados={'meta': mmm[-1]})
	except:
		pass
def Seasons():
	link = xx.OpenURL('https://api.themoviedb.org/3/tv/'+url+'?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries=json.loads(link)
	#ST(entries)
	for season in entries["seasons"]:
		try:
			mmm = mg.get_tvshow_details(title="",tmdb_id=url, ignore_cache=MUcache, lang=MUlang)
			metasea=xx.mergedicts(mmm[-1],mmm[season['season_number']])
			xx.AddDir(metasea["name"], str(season['season_number']), "trakt.Episodes", isFolder=True, dados={'meta': metasea})
		except:
			pass
def Episodes(playordownload="PlayUrl"):
#def Episodes(playordownload="trakt.PlayTraktDirect"):
	from datetime import datetime
	today = datetime.timestamp( datetime.now() )
	dados2 = eval(dados)
	trak = xx.traktS()
	link = xx.OpenURL('https://api.themoviedb.org/3/tv/'+dados2['meta']['tmdb_id']+'/season/'+url+'?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries=json.loads(link)
	prog = 1
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	for entry in entries["episodes"]:
		try:
			epidate = entry['air_date'].split("-")
			timesepi = datetime.timestamp(  datetime(int(epidate[0]), int(epidate[1]), int(epidate[2]))  ) 
			#ST(entry['air_date'].split("-"))
			#ST(str(entry["episode_number"]) + " - " +str(today - timesepi),"1")
			if today - timesepi > - 449837:
				progtotal = int( 100*prog/(len(entries["episodes"])) )
				progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
				prog+=1
				if (progress.iscanceled()): break
				pc = 1 if dados2['meta']['tmdb_id']+url+str(entry["episode_number"]) in trak else None
				play = "plugin://plugin.video.elementum/library/show/play/"+dados2['meta']["tmdb_id"]+"/"+url+"/"+str(entry["episode_number"])
				xx.AddDir( "" , play, playordownload, isFolder=False, IsPlayable=True, dados={'meta': dados2['meta'], 'season': url, 'episode': str(entry["episode_number"]), 'pc': pc})
		except:
			pass
	progress.close()
#----------------------------------------
def PlayTrakt():
	global url
	d = xbmcgui.Dialog().yesno("CubeTor", "Marcar como visto?")
	if not d:
		return
	url = "https://github.com/D4anielCB/cb.rep/raw/master/trakt.mp4"
	dados2 = eval(dados)
	RP = '{0}?mode=PlayUrl&url={1}&dados={2}&url=https://github.com/D4anielCB/cb.rep/raw/master/trakt.mp4'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados2)))
	xbmc.executebuiltin('PlayMedia("'+RP+'")')
	#xx.PlayUrl("", "https://github.com/D4anielCB/cb.rep/raw/master/trakt.mp4")
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