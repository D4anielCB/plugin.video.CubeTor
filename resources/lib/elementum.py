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
import xx,download

MUlang = "pt-BR" if Addon.getSetting("MUlang") == "1" else "en"
MUcache = True if Addon.getSetting("MUcache") == "true" else False
MUcacheEpi = True if Addon.getSetting("MUcacheEpi") == "true" else False
MUfanArt = True if Addon.getSetting("MUfanArt") == "true" else False

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
def Download():
	download.Download2("https://github.com/elgatito/plugin.video.elementum/releases/download/v0.1.82/plugin.video.elementum-0.1.82.zip?","elementum.zip","")
def ListSeries():
	folder = addon_data_dir.replace("plugin.video.CubeTor","plugin.video.elementum")
	settings = os.path.join(folder, "settings.xml")
	file = open(settings, "r")
	f = file.read()
	file.close()
	folderserie = re.compile("id=.library_path..([^\<]+)").findall(f)
	folderserie = os.path.join(folderserie[0], "Shows")
	entries = os.listdir(folderserie)
	prog = 1
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	for entry in entries:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/(len(entries)) )
		progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
		prog+=1
		if not re.findall(r'[\u4E00-\u9FCC]+', entry):
			titley = re.findall('(.+) \((\d+)\)', entry)
			meta = mg.get_tvshow_details(title=titley[0][0], year=titley[0][1], ignore_cache=MUcache, lang=MUlang)
			try:
				xx.AddDir(titley[0][0], entry, "elementum.Seasons", isFolder=True, dados={'meta': meta[-1], 'folder': folderserie})
			except:
				pass
	progress.close()
def Seasons():
	dados2 = eval(dados)
	folderseason = os.path.join(dados2['folder'], url)
	entries = os.listdir(folderseason)
	seasons = {}
	for entry in entries:
		try:
			s = re.findall('S(\d+)E\d+', entry)
			seasons[s[0]] = s[0]
		except:
			pass
	for season in seasons:
		mmm = mg.get_tvshow_details(title="",tmdb_id=dados2['meta']['tmdb_id'], ignore_cache=MUcache, lang=MUlang)
		metasea=xx.mergedicts(mmm[-1],mmm[int(season)])
		#ST(metasea)
		xx.AddDir(metasea["name"], "S"+season+"E", "elementum.Episodes", isFolder=True, dados={'meta': metasea, 'folder': folderseason})
def Episodes():
	prog = 1
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	trak = xx.traktS()
	dados2 = eval(dados)
	entries = os.listdir(dados2['folder'])
	totalepi =  re.findall(url,   ",".join(entries))
	for episodes in entries:
		if url in episodes:
			progtotal = int( 100*prog/(len(totalepi)) )
			progress.update(progtotal, "Só o primeiro acesso que demora\n"+str(progtotal)+" %")
			prog+=1
			if (progress.iscanceled()): break
			se = re.findall('S(\d+)E(\d+)', episodes)
			pc = 1 if dados2['meta']['tmdb_id']+str(int(se[0][0]))+str(int(se[0][1])) in trak else None
			play = "plugin://plugin.video.elementum/library/show/play/"+dados2['meta']["tmdb_id"]+"/"+se[0][0]+"/"+se[0][1]
			xx.AddDir( "" , play, "PlayUrl", isFolder=False, IsPlayable=True, dados={'meta': dados2['meta'], 'season': se[0][0], 'episode': se[0][1], 'pc': pc})
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
