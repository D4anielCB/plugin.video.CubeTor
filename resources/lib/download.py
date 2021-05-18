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

AddonID = 'plugin.video.CubeTor' # xbmcaddon.Addon('plugin.video.CubeTor')
Addon = xbmcaddon.Addon(AddonID)
AddonName = Addon.getAddonInfo("name")
addonDir = Addon.getAddonInfo('path')
icon = os.path.join(addonDir,"icon.png")
iconsDir = os.path.join(addonDir, "resources", "images")

libDir = os.path.join(addonDir, 'resources', 'lib')
sys.path.insert(0, libDir)
#import common
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else None
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
def StartDownload(url="", file="", ref=""):
	if Addon.getSetting("cDownload") == "True":
		d = xbmcgui.Dialog().yesno("CubeTor", "Parar o download e começar esse?")
		if d:
			Addon.setSetting("cDownload", "False")
			xbmc.sleep(6000)
			Addon.setSetting("cDownload", "True")
			Download(url, file, ref)
	else:
		d = xbmcgui.Dialog().yesno("CubeTor", "Começar o download?")
		if not d: return
		Addon.setSetting("cDownload", "True")
		Download(url, file, ref)
	#Download("https://s1.movies.futbol/web-sources/download/475DC76CEA238433/275941/Chernobyl+-+Season+1%3a+miniseries+-+1%3a23%3a45+(Trailers.to).mp4", "http://trailers.to")
	
def StopDownload():
	if Addon.getSetting("cDownload") == "False":
		xbmcgui.Dialog().ok("CubeTor", "Nenhum download ativo")
		return
	d = xbmcgui.Dialog().yesno("CubeTor", "Stop Downloading?")
	if d:
		Addon.setSetting("cDownload", "False")
		
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])
		
def Download(url="", file="", ref=""):
	if not url: return
	req = Request(url)
	if ref:
		req.add_header('referer', ref)
	req.add_header('Content-Type', 'video/mp4')
	req.add_header('Accept-Ranges', 'bytes')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/248.65')
	sizechunk = 10 * 1024 * 1024
	File = file +".mp4" if not ".mp4" in file else file
	try:
		file_stats = os.stat(File)
		escrever = 'ab+'
		file_a_size = (file_stats.st_size)
		totalsize = file_a_size
		req.add_header('Range', 'bytes='+str(file_a_size)+'-')
		NF("Retomando o download", 1000)
	except:
		totalsize = 0
		escrever = 'wb'
	try:
		resp = urlopen(req)
	except:
		Addon.setSetting("cDownload", "False")
		NF("Download pode ter acabado",1000)
		return
	length = re.compile('ength\: ?(\d+)').findall(str(resp.headers))
	length = int(length[0]) + totalsize
	tamanho = convert_size(length)
	#return
	prog=0
	progress = xbmcgui.DialogProgressBG()
	progress.create(file +" "+ tamanho+ ".mp4")
	with open(File, escrever) as f:
		while xbmcaddon.Addon('plugin.video.CubeTor').getSetting("cDownload") == "True":
			chunk = resp.read(sizechunk)
			if not chunk:
				#NF("parou")
				break
			progtotal = int( 100*totalsize/(length) )
			progress.update(progtotal, "")
			prog+=1
			f.write(chunk)
			totalsize+=sizechunk
	NF("Download concluido", 1000)
	Addon.setSetting("cDownload", "False")
	progress.close()
#----------------------------------------
def ST(x="", o="w"):
	if o == "1":
		o = "a+"
	if type(x) == type({}) or type(x) == type([]):
		y = json.dumps(x, indent=4, ensure_ascii=True)
	else:
		try:
			y = str(x)
		except:
			y = str(str(x).encode("utf-8"))
	Path = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('path') )
	py = os.path.join( Path, "study.txt")
	#file = open(py, "a+")
	file = open(py, o)
	file.write(y+"\n"+str(type(x)))
	file.close()
def NF(text, t=5000):
	xbmc.executebuiltin("Notification({0}, {1}, {3}, {2})".format(AddonName, str(text), icon, t))