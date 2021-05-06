# -*- coding: utf-8 -*-
import xbmc
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, json, hashlib, re, unicodedata, math, xbmcvfs
import shutil
from urllib.parse import urlparse, quote_plus, unquote, urlencode
from urllib.request import urlopen, Request
import urllib.request, urllib.parse, urllib.error
import urllib.parse

AddonID = 'plugin.video.CubeTor'
Addon = xbmcaddon.Addon(AddonID)
AddonName = Addon.getAddonInfo("name")
addonDir = Addon.getAddonInfo('path')
icon = os.path.join(addonDir,"icon.png")
iconsDir = os.path.join(addonDir, "resources", "images")

libDir = os.path.join(addonDir, 'resources', 'lib')
sys.path.insert(0, libDir)
import xx

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
def PeerSeed(url2):
	import html
	try:
		link = quote_plus(html.unescape(url2))
		seeds = xx.OpenURL("https://checker.openwebtorrent.com/check?magnet="+link)
		j = json.loads(seeds)
	except:
		j = {"error": "nao carregou"}
	return j
#-----------------------------------------
def Busca():
	q = xbmcgui.Dialog().input("O que busca?")
	xx.AddDir(q+" Dublado 1080p", quote_plus(q+" Dublado 1080p"), "google.BuscaCat", "", info="", isFolder=True, IsPlayable=False)
	xx.AddDir(q+" x265", quote_plus(q+" x265"), "google.BuscaCat", "", info="", isFolder=True, IsPlayable=False)
	xx.AddDir(q+" YTS", quote_plus(q+" YTS"), "google.BuscaCat", "", info="", isFolder=True, IsPlayable=False)
	xx.AddDir(q, quote_plus(q), "google.BuscaCat", "", info="", isFolder=True, IsPlayable=False)
def BuscaCat():
	try:
		google = xx.OpenURL("https://www.google.com/search?q="+url+"+torrent")
		googlere = re.compile(";url=([^\"]+)\&amp;ved\=").findall(google)
		progress = xbmcgui.DialogProgress()
		progress.create('Carregando...')
		progress.update(0, "Carregando...")
		prog = 1
		#ST(googlere)
		for links in googlere[:5]:
			if (progress.iscanceled()): break
			magnet = xx.OpenURL(links)
			magnetre = re.compile('magnet\:\?[^\'|"]+').findall(magnet)
			for link in magnetre:
				title = re.compile("dn=(.+?)(\&|$)").findall(link)
				if title:
					j = PeerSeed(link)
					if "seeds" in j:
						xx.AddDir(str(j["seeds"])+" / "+str(j["peers"])+" "+unquote(title[0][0]), link, "comando.PlayTorrents", iconimage, info=links, isFolder=False, IsPlayable=True)
					else:
						xx.AddDir(unquote(title[0][0]), link, "comando.PlayTorrents", iconimage, info=links, isFolder=False, IsPlayable=True)
			progtotal = int(100*prog/5)
			progress.update(progtotal, str(progtotal)+" %")
			prog+=1
		progress.close()
	except:
		xx.AddDir("Erro no servidor", "", "", iconimage, info="", isFolder=False, IsPlayable=True)
#----------------------------------------
def ST(x="", o="w"):
	if o == "1":
		o = "a+"
	if type(x) == type({}) or type(x) == type([]):
		y = json.dumps(x, indent=4, ensure_ascii=True)
	else:
		y = str(str(x).encode("utf-8"))
	Path = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('path') )
	py = os.path.join( Path, "study.txt")
	#file = open(py, "a+")
	file = open(py, o)
	file.write(y+"\n"+str(type(x)))
	file.close()