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
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else None

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
def ListSeries(tipo="watched"):
	#ST(MUlang)
	headers = {'Content-Type': 'application/json','trakt-api-version': '2','trakt-api-key': '888a9d79a643b0f4e9f58b5d4c2b13ee6d8bd584bc72bff8b263f184e9b5ed5d'}
	response_body = xx.OpenURL('https://api.trakt.tv/users/'+Ctrakt+'/'+tipo+'/shows?extended=noseasons',headers=headers)
	entries=json.loads(response_body)
	prog = 1
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	for entry in entries:
		#ST(entry['seasons'])
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/(len(entries)) )
		progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
		prog+=1
		#titley = re.findall('(.+) \((\d+)\)', entry)
		meta = mg.get_tvshow_details(title="", tmdb_id=str(entry['show']['ids']['tmdb']), ignore_cache=MUcache, lang=MUlang)
		try:
			xx.AddDir(entry['show']['title'], str(entry['show']['ids']['tmdb']), "trakt.Seasons", isFolder=True, dados={'meta': meta[-1]})
		except:
			pass
	progress.close()
def Seasons():
	dados2 = eval(dados)
	link = xx.OpenURL('https://api.themoviedb.org/3/tv/'+dados2['meta']['tmdb_id']+'?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries=json.loads(link)
	for season in entries["seasons"]:
		mmm = mg.get_tvshow_details(title="",tmdb_id=url, ignore_cache=MUcache, lang=MUlang)
		metasea=xx.mergedicts(mmm[-1],mmm[season['season_number']])
		xx.AddDir(metasea["name"], str(season['season_number']), "trakt.Episodes", isFolder=True, dados={'meta': metasea})
def Episodes():
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
				xx.AddDir( "" , play, "PlayUrl", isFolder=False, IsPlayable=True, dados={'meta': dados2['meta'], 'season': url, 'episode': str(entry["episode_number"]), 'pc': pc})
		except:
			pass
	progress.close()
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
