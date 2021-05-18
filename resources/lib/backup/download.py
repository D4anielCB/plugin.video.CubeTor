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
#import common
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else None
MUlang = "pt-BR" if Addon.getSetting("MUlang") == "1" else "en"
MUcache = True if Addon.getSetting("MUcache") == "true" else False
MUcacheEpi = True if Addon.getSetting("MUcacheEpi") == "true" else False
MUfanArt = True if Addon.getSetting("MUfanArt") == "true" else False
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
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class Down:
	def __init__(self, url, file, ref, cDownload):
		self.url = url
		self.file = file
		self.ref = ref
		self.cDownload = cDownload

	def StartDownload(self):
		'''ST("")
		ST(self.url,"1")
		ST(self.file,"1")
		ST(self.ref,"1")
		ST(self.cDownload,"1")'''
		#return
		if self.cDownload == True:
			d = xbmcgui.Dialog().yesno("CubeTor", "Parar o download e começar esse?")
			if d:
				self.cDownload = False
				xbmc.sleep(6000)
				self.cDownload = True
				self.Download(self.url, self.file, self.ref)
		else:
			d = xbmcgui.Dialog().yesno("CubeTor", "Começar o download?")
			if not d: return
			Addon.setSetting("cDownload", "True")
			self.Download(self.url, self.file, self.ref)
		#Download("https://s1.movies.futbol/web-sources/download/475DC76CEA238433/275941/Chernobyl+-+Season+1%3a+miniseries+-+1%3a23%3a45+(Trailers.to).mp4", "http://trailers.to")
		
	def StopDownload(self):
		#ST(self.cDownload)
		if self.cDownload == False:
			xbmcgui.Dialog().ok("CubeTor", "Nenhum download ativo")
			return
		d = xbmcgui.Dialog().yesno("CubeTor", "Stop Downloading?")
		if d:
			self.cDownload = False
			
	def Download(self, url="", file="", ref=""):
		if not url: return
		#Path = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('path') )
		#file = os.path.join( Path, "video.mp4")
		req = Request(url)
		if ref:
			req.add_header('referer', ref)
		req.add_header('Content-Type', 'video/mp4')
		req.add_header('Accept-Ranges', 'bytes')
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/248.65')
		sizechunk = 10 * 1024 * 1024
		totalsize = 0
		#req.add_header('Range', 'bytes=1000000000-')
		#req.add_header('Range', 'bytes=104857601-209715202')
		resp = urlopen(req)
		length = re.compile('ength\: ?(\d+)').findall(str(resp.headers))
		tamanho = convert_size(int(length[0]))
		File = file +".mp4"
		#resp2 = urlopen(req)
		prog=0
		progress = xbmcgui.DialogProgressBG()
		progress.create(file +" "+ tamanho+ ".mp4")
		with open(File, 'wb') as f:
			while self.cDownload == True:
				progtotal = int( 100*totalsize/(int(length[0])) )
				progress.update(progtotal, "")
				prog+=1
				chunk = resp.read(sizechunk)
				if not chunk:
					self.cDownload = False
					progress.close()
					break
				f.write(chunk)
				totalsize+=sizechunk
		progress.close()
		
	def RunDownload(self):
		titulo = re.sub(r'[\\/*?:"<>|]',"",eval(dados)['titulo'])
		link = OpenURL("https://trailers.to/en/episode/"+url+"/link")
		key = re.compile("[0-9a-fA-F]{15,16}").findall(link[0])
		self.url = 'https://s0.blogspotting.art/web-sources/'+key[0]+'/'+url+'/file'
		self.file = os.path.join( cDirtrtvDown, titulo)
		self.ref="http://trailers.to"
		self.StartDownload()
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
def NF(text):
	xbmc.executebuiltin("Notification({0}, {1}, {3}, {2})".format(AddonName, str(text), icon, 1000))