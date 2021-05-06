# -*- coding: utf-8 -*-
import xbmc
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, json, hashlib, re, unicodedata, math, xbmcvfs
import shutil
from urllib.parse import urlparse, quote_plus, unquote
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
def Torrents(url):
	for i in range(1,6):
		try:
			link = xx.OpenURL(url+"/page"+str(i))
		except:
			break
			return
		if not link: return
		match = re.compile('itemprop="headline".{1,15}(http.{1,10}comandotorrent.tv[^"]+)..([^\<]+)').findall(link)
		img = re.compile('src..([^\"]+)" data-recalc-dims="1"').findall(link)
		i = 0
		for link,title in match:
			xx.AddDir(unquote(title), link, "comandotv.ListTorrents", img[i], img[i], isFolder=True)
			i+=1
def ListTorrents():
	link = xx.OpenURL(url).replace("\n","")
	match = re.compile('strong\>([^\<]+(.)+?)a href=\"(magnet[^"]+)').findall(link)
	for title,espaco,link in match:
		title2 = re.compile("dn=(.+?)(\&|$)").findall(link)
		xx.AddDir(unquote(title2[0][0]), link, "comandotv.PlayTorrents", iconimage, logos, isFolder=False, IsPlayable=True)
def PlayTorrents():
	xx.PlayUrl(name,"plugin://plugin.video.elementum/play?uri="+url)
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
	file = open(py, o)
	file.write(y+"\n"+str(type(x)))
	file.close()