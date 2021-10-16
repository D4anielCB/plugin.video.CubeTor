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
Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else ""
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
def PlayUrl(name, url, srt=False, RS="0"): #1
	#ST(url)
	clearlogo = ""
	dados2 = eval(dados)
	listitem = xbmcgui.ListItem(path=url)
	if RS != "0":
		listitem.setProperty('StartPercent', RS)
	infol = {}
	if "mmeta" in dados2:
		try:
			ids = json.dumps({u'tmdb': dados2['mmeta']['tmdb_id']})
			xbmcgui.Window(10000).setProperty('script.trakt.ids', ids)
		except:
			pass
		if MUfanArt:
			try:
				fanart = OpenURL("http://webservice.fanart.tv/v3/movies/"+dados2["mmeta"]["imdbnumber"]+"?api_key=f8ba25de3d50ea5655f5b6bd78387878")
				fanartj = json.loads(fanart)
				clearlogo = fanartj["hdmovielogo"][0]['url']
			except:
				pass
	if "meta" in dados2:
		if MUfanArt:
			#import random
			try:
				fanart = OpenURL("https://webservice.fanart.tv/v3/tv/"+dados2["meta"]["tvdb_id"]+"?api_key=f8ba25de3d50ea5655f5b6bd78387878")
				fanartj = json.loads(fanart)
				#rand = random.randrange(0,len(fanartj["hdtvlogo"]))
				clearlogo = fanartj["hdtvlogo"][0]['url']
			except:
				pass
		if 'season' in dados and 'episode' in dados:
			infol["season"] =  dados2["season"]
			infol["episode"] =  dados2["episode"]	
			infol["title"] = re.sub('\d{1,2}x\d{1,3}. ', '', xbmc.getInfoLabel("ListItem.Label"))
		try:
			ids = json.dumps({u'tmdb': dados2['meta']['tmdb_id']})
			xbmcgui.Window(10000).setProperty('script.trakt.ids', ids)
		except:
			pass
	xbmc.log('--- Playing "{0}". {1}'.format(name, url), 2)
	if srt:
		from pathlib import Path
		try:
			path = xbmc.translatePath( "special://temp" )
			paths = sorted(Path(path).iterdir(), key=os.path.getmtime)
			for entry in reversed(paths):
				if ".srt" in str(entry):
					listitem.setSubtitles([str(entry), str(entry) ])
					break
		except:
			pass
	listitem.setInfo( "video", infol )
	listitem.setArt({"clearlogo": clearlogo })
	#listitem.setMimeType('video/mp2t')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
# --------------------------------------------------
def mergedicts2(dict1, dict2):
    return(dict2.update(dict1))
def mergedicts(x, y):
    z = x.copy()
    z.update(y)
    return z
def Data(x):
	x = re.sub('\d\d(\d+)\-(\d+)\-(\d+)', r'\3/\2/\1', x )
	return "[COLOR white]("+x+")[/COLOR]"
def EPI(x):
	x = re.sub('[0]+(\d+)', r'\1', x )
	return str(x)
def SEAS(x):
	x = re.sub('0(\d)', r'\1', x )
	return str(x)
#-----------------------------------------
def AddDir(name, url, mode, iconimage='', logos='', info='', dados={}, isFolder=True, IsPlayable=False):
	urlParams = {'name': name, 'url': url, 'mode': mode, 'iconimage': iconimage, 'logos': logos, 'dados': dados}
	liz = xbmcgui.ListItem(name)
	if 'meta' in dados:
		if 'season' in dados and 'episode' in dados:
			eInfo1 = mg.get_episode_details(dados['meta']['tmdb_id'], SEAS(dados['season']), EPI(dados['episode']), ignore_cache=MUcacheEpi, lang=MUlang)
			eInfo = mergedicts(dados['meta'],eInfo1)
			eInfo['mediatype'] = "episode"
			if 'pc' in dados:
				eInfo['playcount'] = 1 if dados['pc'] else 0
			#eInfo['playcount'] = 1 if playcount else 0
			if 'EpisodeTitle' in eInfo:
				liz=xbmcgui.ListItem(dados['season']+"x"+EPI(dados['episode'])+". "+eInfo['EpisodeTitle'])
			else:
				liz=xbmcgui.ListItem(dados['season']+"x"+EPI(dados['episode'])+". Episode "+EPI(dados['episode']))
			if ".jpg" in eInfo['imagepi']:
				pass
				liz.setArt({"icon": eInfo['imagepi'], "thumb": eInfo['imagepi'], "poster": eInfo['cover_url'], "banner": eInfo['cover_url'], "fanart": eInfo['backdrop_url'] })
			else:
				liz.setArt({"thumb": eInfo['cover_url'], "poster": eInfo['cover_url'], "banner": eInfo['cover_url'], "fanart": eInfo['backdrop_url'] })
			if "cast" in eInfo:
				count = 0
				for value in eInfo['cast']:
					for value2 in value:
						if 'thumbnail' in eInfo['cast'][count]:
							eInfo['cast'][count]['thumbnail']=eInfo['cast'][count]['thumbnail'].replace("/original/","/w300/")
					count+=1
				liz.setCast(eInfo['cast'])
			eInfo.pop('cast', 1)
			eInfo.pop('genre', 1)
			liz.setInfo( "video", eInfo )
		else:
			liz=xbmcgui.ListItem(name)
			if "cast" in dados['meta']:
				liz.setCast(dados['meta']['cast'])
			dados['meta'].pop('cast', 1)
			if not 'mediatype' in dados['meta']:
				dados['meta']['mediatype'] = u'tvshow'
			dados['meta']['tagline'] = ""
			if "genre" in dados['meta']:
				for i in dados['meta']['genre']:
					dados['meta']['tagline'] = i if dados['meta']['tagline'] == "" else dados['meta']['tagline'] + ", " + i
			liz.setArt({"thumb": dados['meta']['cover_url'], "poster": dados['meta']['cover_url'], "banner": dados['meta']['cover_url'], "fanart": dados['meta']['backdrop_url'] })
			liz.setInfo("video", dados['meta'])
	elif 'mmeta' in dados:
		dados['mmeta']['mediatype'] = u'movie'
		dados['mmeta']['Imdbnumber'] = dados['mmeta']['imdbnumber']
		if 'Runtime' in dados['mmeta']:
			dados['mmeta']['Duration'] = dados['mmeta']['Runtime']
		dados['mmeta']['tagline'] = ""
		for i in dados['mmeta']['genre']:
			dados['mmeta']['tagline'] = i if dados['mmeta']['tagline'] == "" else dados['mmeta']['tagline'] + ", " + i
		if 'pc' in dados:
			dados['mmeta']['playcount'] = 1 if dados['pc'] else 0
		liz=xbmcgui.ListItem(name)
		if "fanart" in dados['mmeta']['art']:
			liz.setArt({"poster": dados['mmeta']['art']['poster'], "banner": dados['mmeta']['art']['poster'], "fanart": dados['mmeta']['art']['fanart'] })
		else:
			liz.setArt({"poster": dados['mmeta']['art']['poster'], "banner": dados['mmeta']['art']['poster'], "fanart": "" })
		count=0
		if "cast" in dados['mmeta']:
			count = 0
			for value in dados['mmeta']['cast']:
				for value2 in value:
					if 'thumbnail' in dados['mmeta']['cast'][count]:
						dados['mmeta']['cast'][count]['thumbnail'] = dados['mmeta']['cast'][count]['thumbnail'].replace("/original/","/w300/")
				count+=1
			liz.setCast(dados['mmeta']['cast'])
		dados['mmeta'].pop('cast', 1)
		dados['mmeta'].pop('castandrole', 1)
		dados['mmeta'].pop('art', 1)
		if name:
			dados['mmeta']['title'] = name
		#ST(name)
		liz.setInfo( "video", dados['mmeta'] )
	else:
		liz.setContentLookup(False)
		liz.setInfo("video", { "Title": name, "Plot": info })
		liz.setArt({"icon":iconimage ,"poster": iconimage, "banner": logos, "fanart": logos, "thumb": iconimage })
	if IsPlayable:
		liz.setProperty('IsPlayable', 'true')
	if mode == "trtv.PlayFile":
		items = [("Download", 'RunPlugin({0}?mode=trtv.DownloadMP4&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("Deletar arquivo", 'RunPlugin({0}?mode=trtv.DeleteFile&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("Parar Download", 'RunPlugin({0}?mode=download.StopDownload)'.format(sys.argv[0] ))]
		liz.addContextMenuItems(items)
	elif mode == "PlayUrl" and info == "delete":
		items = [("Resume Download", 'RunPlugin({0}?mode=trtv.ResumeFile&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("Deletar arquivo", 'RunPlugin({0}?mode=trtv.DeleteFile&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("Parar Download", 'RunPlugin({0}?mode=download.StopDownload)'.format(sys.argv[0] ))]
		liz.addContextMenuItems(items)
	if mode == "tmdb.Opcoes":
		liz.addContextMenuItems(items = [("[COLOR green]Recomendações[/COLOR]", 'RunPlugin({0}?mode=tmdb.MovieRecom&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("[COLOR yellow]Buscar em Trailers.to[/COLOR]", 'RunPlugin({0}?mode=tmdb.DownloadTrtv&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("Marcar como visto", 'RunPlugin({0}?mode=trakt.PlayTrakt&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("[COLOR blue]Procurar Providers[/COLOR]", 'RunPlugin({0}?mode=tmdb.FindProvidersM&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("[COLOR salmon]Collections[/COLOR]", 'RunPlugin({0}?mode=tmdb.Collections&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) ))	])
		#liz.addContextMenuItems(items = [])
	if mode == "trakt.Shows":
		liz.addContextMenuItems(items = [("[COLOR green]Recomendações[/COLOR]", 'ActivateWindow(10025,{0}?mode=tmdb.tvshow_recom&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),
		("[COLOR blue]Procurar Providers[/COLOR]", 'RunPlugin({0}?mode=tmdb.FindProvidersTV&url={1}&dados={2})'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)) )),		])
		#liz.addContextMenuItems(items = [])
	u = '{0}?{1}'.format(sys.argv[0], urllib.parse.urlencode(urlParams))
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)
# --------------------------------------------------
def OpenURL(url, headers={}, user_data={}, cookieJar=None, justCookie=False):
	req = Request(url)
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/11.0'
	for k, v in headers.items():
		req.add_header(k, v)
	#if not 'User-Agent' in headers:
		#req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/11.0')
	return urlopen(req).read().decode("utf-8").replace("\r", "")
#----------------------------------------
Sortxbmc=["SORT_METHOD_UNSORTED","SORT_METHOD_LABEL","SORT_METHOD_LASTPLAYED","SORT_METHOD_VIDEO_RATING","SORT_METHOD_DATE","SORT_METHOD_GENRE"]
def setViewS():
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	for s in Sortxbmc:
		xbmcplugin.addSortMethod(int(sys.argv[1]), eval("xbmcplugin."+s))
	xbmc.executebuiltin("Container.SetViewMode(50)")
def setViewS2():
	xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	for s in Sortxbmc:
		xbmcplugin.addSortMethod(int(sys.argv[1]), eval("xbmcplugin."+s))
	xbmc.executebuiltin("Container.SetViewMode(55)")
def setViewS3():
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')	
	xbmc.executebuiltin("Container.SetViewMode(54)")
def setViewM():
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	for s in Sortxbmc:
		xbmcplugin.addSortMethod(int(sys.argv[1]), eval("xbmcplugin."+s))
	xbmc.executebuiltin("Container.SetViewMode(50)")
def setViewM2():
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	for s in Sortxbmc:
		xbmcplugin.addSortMethod(int(sys.argv[1]), eval("xbmcplugin."+s))
	xbmc.executebuiltin("Container.SetViewMode(55)")
# --------------  Trakt
def traktS():
	if not Ctrakt:
		return []
	try:
		headers1 = {'Content-Type': 'application/json','trakt-api-version': '2','trakt-api-key': '888a9d79a643b0f4e9f58b5d4c2b13ee6d8bd584bc72bff8b263f184e9b5ed5d'}
		response_body = OpenURL('https://api.trakt.tv/users/'+Ctrakt+'/watched/shows',headers=headers1)
		j=json.loads(response_body)
		trak=[]
	except:
		return []
	for m in j:
		try:
			for Sea in m['seasons']:
				for epi in Sea['episodes']:
					trak.append(str(m['show']['ids']['tmdb'])+str(Sea['number'])+str(epi['number']))
		except:
			pass
	return trak	
def traktM():
	if not Ctrakt:
		return []
	headers1 = {'Content-Type': 'application/json','trakt-api-version': '2','trakt-api-key': '888a9d79a643b0f4e9f58b5d4c2b13ee6d8bd584bc72bff8b263f184e9b5ed5d'}
	response_body = OpenURL('https://api.trakt.tv/users/'+Ctrakt+'/watched/movies',headers=headers1)
	j=json.loads(response_body)
	trak=[]
	for m in j:
		try:
			trak.append(str(m['movie']['ids']['tmdb']))
		except:
			pass
	return trak
#----------------------------------------
def PaginacaoMenos():
	dados2 = eval(dados)
	Addon.setSetting(dados2['page'], str(int(url) - 1) )
	xbmc.executebuiltin("Container.Refresh()")
def PaginacaoMais():
	dados2 = eval(dados)
	#ST(url)
	#return
	#xbmcgui.Dialog().ok('Cube Play', url + " " +background)
	Addon.setSetting(dados2['page'], str(int(url) + 1) )
	xbmc.executebuiltin("Container.Refresh()")
#----------------------------------------
def remove_accents(input_str):
	import unicodedata
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	only_ascii = nfkd_form.encode('ASCII', 'ignore')
	return re.sub('[^\w\-_\. ]', '', only_ascii.decode("utf-8") ) 
	
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