# -*- coding: utf-8 -*-
import sys, xbmcplugin ,xbmcgui, xbmcaddon, xbmc, os, json, hashlib, re, math, html, xbmcvfs
from urllib.parse import urlparse, quote_plus
from urllib.request import urlopen, Request
import urllib.request, urllib.parse, urllib.error
import urllib.parse

AddonID = 'plugin.video.CubePlayMeta'
Addon = xbmcaddon.Addon(AddonID)
addon_data_dir = xbmcvfs.translatePath(Addon.getAddonInfo("profile"))
addonDir = Addon.getAddonInfo('path')
icon = os.path.join(addonDir,"icon.png")
AddonName = Addon.getAddonInfo("name")


def OpenURL(url, headers={}, user_data={}, cookieJar=None, justCookie=False):
	req = Request(url)
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/11.0'
	for k, v in headers.items():
		req.add_header(k, v)
	#if not 'User-Agent' in headers:
		#req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/11.0')
	return urlopen(req).read().decode("utf-8").replace("\r", "")

def ReadList(fileName):
	import shutil
	try:
		with open(fileName, 'r', encoding='utf-8') as handle:
			content = json.load(handle)
	except Exception as ex:
		xbmc.log(str(ex), 5)
		if os.path.isfile(fileName):
			shutil.copyfile(fileName, "{0}_bak.txt".format(fileName[:fileName.rfind('.')]))
			xbmc.executebuiltin('Notification({0}, NOT read file: "{1}". \nBackup createad, {2}, {3})'.format(AddonName, os.path.basename(fileName), 5000, icon))
		content=[]
	return content
def SaveList(filname, chList):
	try:
		f = open(filname, 'w+', encoding='utf-8')
		f.write(json.dumps(chList, indent=4, ensure_ascii=False))
		f.close()
		success = True
	except:
		#xbmc.log(str(ex), 3)
		success = False
	return success
def ReadFile(fileName):
	try:
		f = open(fileName, 'r', encoding='utf-8')
		content = f.read().replace("\n\n", "\n")
		f.close()
	except Exception as ex:
		xbmc.log(str(ex), 3)
		content = ""
	return content

# --------------------------------------
def SaveFile(data, check,  file, title=""):
	file = os.path.join(addon_data_dir, file+".txt")
	favList = ReadList(file)
	for item in favList:
		if str(item[check]) == str(data[check]):
			xbmc.executebuiltin("Notification({0}, {1}, {3}, {2})".format(AddonName, "Anime "+title+" ja adicionado", icon, 5000))
			return False
	favList.append(data)
	SaveList(file, favList)
	xbmc.executebuiltin("Notification({0}, {1}, {3}, {2})".format(AddonName, title+" Adicionado", icon, 5000))
	return True
# -----------------------------
params =  urllib.parse.parse_qs( sys.argv[2][1:] ) 
logos = params.get('logos',[None])[0]
index = int(params.get('index', '-1')[0]) if params.get('index') else -1

# -----------------------------
def RemoveList(): #534
	listFile = os.path.join(addon_data_dir, logos+".txt")
	chList = ReadList(listFile) 
	if index < 0 or index >= len(chList):
		return
	del chList[index]
	SaveList(listFile, chList)
	xbmc.executebuiltin("Container.Refresh()")
	xbmc.sleep(1000)
	xbmc.executebuiltin('reloadskin')