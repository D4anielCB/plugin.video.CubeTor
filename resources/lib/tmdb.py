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
import xx, google, common

MUlang = "pt-BR" if Addon.getSetting("MUlang") == "1" else "en"
MUlangM = "pt-BR" if Addon.getSetting("MUlangM") == "1" else "en"
MUcache = True if Addon.getSetting("MUcache") == "true" else False
MUcacheEpi = True if Addon.getSetting("MUcacheEpi") == "true" else False
MUfanArt = True if Addon.getSetting("MUfanArt") == "true" else False

Cproxy = "https://cbplay.000webhostapp.com/nc/nc.php?u=" if Addon.getSetting("Cproxy") else ""
Ctor = True if Addon.getSetting("Ctor") == "true" else False

Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else ""
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
cPagetmdb = "0" if Addon.getSetting("cPagetmdb")=="" else Addon.getSetting("cPagetmdb") #paginacao Filmes
cPagetmdbgenero = "0" if Addon.getSetting("cPagetmdbgenero")=="" else Addon.getSetting("cPagetmdbgenero") #paginacao Genero
cPagetmdbano = "2021" if Addon.getSetting("cPagetmdbano")=="" else Addon.getSetting("cPagetmdbano") #paginacao Genero
cPagetmdblang = "Todos" if Addon.getSetting("cPagetmdblang")=="" else Addon.getSetting("cPagetmdblang") #paginacao Genero
tmdbgenero = {"0": "Todos", "28": "Ação", "16":"Animação", "12":"Aventura", "35":"Comédia", "80":"Crime", "99":"Documentário", "18":"Drama", "10751":"Família", "14":"Fantasia", "27":"Horror", "878":"Sci-fi", "53":"Thriller"}
tmdbano = {"Todos" :"Todos", "2021" : "2021", "2020" : "2020", "2019" : "2019", "2018" : "2018", "2017" : "2017", "2016" : "2016", "2015" : "2015", "2014" : "2014", "2013" : "2013", "2012" : "2012", "2011" : "2011", "2010" : "2010", "2009" : "2009", "2008" : "2008", "2007" : "2007", "2006" : "2006", "2005" : "2005", "2004" : "2004", "2003" : "2003", "2002" : "2002", "2001" : "2001", "2000" : "2000", "1999" : "1999", "1998" : "1998", "1997" : "1997", "1996" : "1996", "1995" : "1995", "1994" : "1994", "1993" : "1993", "1992" : "1992", "1991" : "1991", "1990" : "1990"}
tmdblang = {"Todos": "Todos", "pt": "Português", "en": "Inglês", "es": "Espanhol", "fr": "Francês", "de": "Alemão", "ko": "Coreano", "zh": "Chinês", "it": "Italiano"}
#-----------------------------------------
def Genero():
	gen = []
	gen2 = []
	for entry in tmdbgenero:
		gen.append(tmdbgenero[entry])
		gen2.append(entry)
	d = xbmcgui.Dialog().select("Selecione o gênero", gen)
	if d >-1:
		Addon.setSetting(url, gen2[d] )
		xbmc.executebuiltin("Container.Refresh()")
def Ano():
	ano = []
	ano2 = []
	for entry in tmdbano:
		ano.append(tmdbano[entry])
		ano2.append(entry)
	d = xbmcgui.Dialog().select("Selecione o Ano", ano)
	if d >-1:
		Addon.setSetting(url, ano2[d] )
		xbmc.executebuiltin("Container.Refresh()")
def Lang():
	pais = []
	pais2 = []
	for entry in tmdblang:
		pais.append(tmdblang[entry])
		pais2.append(entry)
	d = xbmcgui.Dialog().select("Selecione o idioma original:", pais)
	if d >-1:
		Addon.setSetting(url, pais2[d] )
		xbmc.executebuiltin("Container.Refresh()")
#-----------------------------------------
def ListSeries():
	xx.AddDir("[COLOR white][B]Gênero:[/B] "+tmdbgenero[cPagetmdbgenero]+" [/COLOR]", "cPagetmdbgenero" , "tmdb.Genero" ,"", isFolder=False)
	xx.AddDir("[COLOR white][B]Língua original:[/B] "+tmdblang[cPagetmdblang]+" [/COLOR]", "cPagetmdblang" , "tmdb.Lang" ,"", isFolder=False)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	with_genres = '&with_genres='+cPagetmdbgenero if cPagetmdbgenero !="0" else ""
	with_original_language = "&with_original_language="+cPagetmdblang if cPagetmdblang != "Todos" else ""
	for page in range (1,5):
		link = xx.OpenURL("https://api.themoviedb.org/3/discover/tv?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&page="+str(page)+"&timezone=America%2FNew_York&include_null_first_air_dates=false&with_watch_monetization_types=flatrate"+with_genres+with_original_language)
		entries=json.loads(link)
		#ST(entries)
		for entry in entries['results']:
			if (progress.iscanceled()): break
			progtotal = int( 100*prog/len(entries['results'])/4 )
			progress.update(progtotal, str(progtotal)+" %")
			prog+=1
			try:
				meta = mg.get_tvshow_details(title="", tmdb_id=str(entry["id"]), ignore_cache=MUcache, lang=MUlang)
				xx.AddDir(entry["name"], str(entry["id"]), "trakt.Shows", isFolder=True, dados={'meta': meta[-1]})
			except:
				pass
		progress.close()
def ListSeason():
	meta = eval(dados)["meta"]
	options = []
	options.append('Busca série em trailers.to')
	options.append('Elementum...')
	sel = xbmcgui.Dialog().contextmenu(options)
	if sel == 0:
		mdb = xx.OpenURL('http://api.themoviedb.org/3/tv/'+url+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=en')
		mdbj = json.loads(mdb)
		#trtv = xx.OpenURL(Cproxy + "https://trailers.to/en/popular/movies-tvshows-collections?q="+quote_plus(mdbj["name"]))
		q = re.sub('[^A-Za-z0-9]+', ' ', mdbj["name"])
		trtv = xx.OpenURL(Cproxy + "https://trailers.to/en/quick-search?q="+quote_plus(q))
		tvshow = re.compile("\/en\/tvshow\/(\d+)").findall(trtv)
		if not tvshow: return
		xx.AddDir(meta["TVShowTitle"], tvshow[0], "trtv.Seasons", isFolder=True, dados={'meta': meta})
	else:
		mdb = xx.OpenURL('http://api.themoviedb.org/3/tv/'+url+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=en')
		mdbj = json.loads(mdb)
		meta = mg.get_tvshow_details(title="", tmdb_id=meta["tmdb_id"], ignore_cache=MUcache, lang=MUlang)
		for entry in meta:
			#ST(entry)
			if entry > 0:
				metasea=xx.mergedicts(meta[-1], meta[entry])
				xx.AddDir(metasea["name"], url, "tmdb.ListEpisodes", isFolder=True, dados={'meta': metasea, 'season': str(entry)})
def ListEpisodes():
	dados2 = eval(dados)
	prog = 1
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	trak = xx.traktS()
	mdb = xx.OpenURL('http://api.themoviedb.org/3/tv/'+url+'/season/'+dados2['season']+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=en')
	mdbj = json.loads(mdb)
	for entry in mdbj['episodes']:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(mdbj['episodes']) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		pc = 1 if dados2["meta"]["tmdb_id"]+str(entry["season_number"])+str(entry["episode_number"]) in trak else None
		xx.AddDir("", "plugin://plugin.video.elementum/library/play/show/"+url+"/season/"+str(entry["season_number"])+"/episode/"+str(entry["episode_number"]), "PlayUrlLeg", isFolder=False, IsPlayable=True, dados={'meta': dados2["meta"], 'season': str(entry["season_number"]), 'episode': str(entry["episode_number"]), 'pc': pc} )
	progress.close()
#-----------------------------------------
def ListMovies():
	trak = xx.traktM()
	xx.AddDir("[COLOR white][B]Gênero:[/B] "+tmdbgenero[cPagetmdbgenero]+" [/COLOR]", "cPagetmdbgenero" , "tmdb.Genero" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Ano:[/B] "+tmdbano[cPagetmdbano]+" [/COLOR]", "cPagetmdbano" , "tmdb.Ano" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Língua original:[/B] "+tmdblang[cPagetmdblang]+" [/COLOR]", "cPagetmdblang" , "tmdb.Lang" ,"", isFolder=False, dados={})
	if int(cPagetmdb) > 0:
		xx.AddDir("[COLOR blue][B]<< Pagina Anterior ["+ str( int(cPagetmdb) ) +"[/B]][/COLOR]", cPagetmdb , "xx.PaginacaoMenos" ,"http://icons.iconarchive.com/icons/iconsmind/outline/256/Previous-icon.png", isFolder=False, dados={'page': 'cPagetmdb'})
	xx.AddDir("[COLOR blue][B]Proxima Pagina >>  ["+ str( int(cPagetmdb) + 1 ) +"[/B]][/COLOR]", cPagetmdb , "xx.PaginacaoMais" ,"http://icons.iconarchive.com/icons/iconsmind/outline/256/Next-2-2-icon.png", isFolder=False, dados={'page': 'cPagetmdb'})
	l = int(cPagetmdb) * 4
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	with_genres = '&with_genres='+cPagetmdbgenero if cPagetmdbgenero !="0" else ""
	primary_release_year = '&primary_release_year='+cPagetmdbano if cPagetmdbano != "Todos" else ""
	with_original_language = "&with_original_language="+cPagetmdblang if cPagetmdblang != "Todos" else ""
	for page in range (1,5):
		#ST(primary_release_year)
		#return
		ano = cPagetmdbano if cPagetmdbano != "2021" else "2021"
		#link = xx.OpenURL('https://api.themoviedb.org/3/discover/movie?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(page+l)+'&with_watch_monetization_types=flatrate&year=2021&with_original_language=pt'+with_genres+primary_release_year)
		link = xx.OpenURL('https://api.themoviedb.org/3/discover/movie?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(page+l)+'&with_watch_monetization_types=flatrate&year=2021'+with_genres+primary_release_year+with_original_language)
		entries=json.loads(link)
		for entry in entries['results']:
			if (progress.iscanceled()): break
			progtotal = int( 100*prog/len(entries['results'])/4 )
			progress.update(progtotal, str(progtotal)+" %")
			prog+=1
			try:
				mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
				pc = 1 if str(mm["tmdb_id"]) in trak else None
				#ST(mm)
				#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
				xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
				#return
			except:
				pass
	progress.close()
#----------------------------------------
def DownloadTrtv():
	import trtv
	meta = eval(dados)["mmeta"]
	year = ""
	if "year" in meta:
		year = " "+str(meta["year"])
	#ST(year)
	mdb = xx.OpenURL("https://api.themoviedb.org/3/movie/"+url+"?api_key=bd6af17904b638d482df1a924f1eabb4&language=en")
	mdbj = json.loads(mdb)
	q = re.sub('[^A-Za-z0-9]+', ' ', mdbj["title"])
	try:
		#trtvpage = xx.OpenURL(Cproxy + "https://trailers.to/en/quick-search?q="+quote_plus(q+year)).replace("\r","").replace("\n","")
		trtvpage = xx.OpenURL(Cproxy + "https://trailers.to/en/popular/movies-tvshows-collections?q="+quote_plus(q+year))
		entries = re.compile("en\/movie\/(\d+).{300,600}"+meta["imdbnumber"]).findall(trtvpage.replace("\r","").replace("\n",""))
		if entries:
			id = entries[0]
			ST(id)
		else:
			xx.NF("Não encontrado")
	except:
		xx.NF("Não encontrado")
		return
	titulo = "M"+str(meta["tmdb_id"])+" "+id+" "+xx.remove_accents(meta["title"])+".mp4"
	#ST(titulo)
	trtv.DownloadMP4(titulo,id,True)
#----------------------------------------
def Historico():
	file = os.path.join(addon_data_dir, "elementum.txt")
	favList = common.ReadList(file)
	#ST(favList)
	#return
	for entry in reversed(favList):
		mm = mg.get_tmdb_details(tmdb_id=entry['imdb'], imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
		xx.AddDir(mm['title'], "plugin://plugin.video.elementum/play?uri="+entry['magnet']+"&doresume=true&type=movie&tmdb="+entry['imdb'], "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
	if cDirtrtvDown:
		xx.AddDir("Download Elementum", "", "elementum.Download", isFolder=False)
#----------------------------------------
def MovieRecom(type="recommendations"):
	mdb = xx.OpenURL('https://api.themoviedb.org/3/movie/'+url+'/'+type+'?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries = json.loads(mdb)
	if entries['results']:
		RP = 'plugin://plugin.video.CubeTor/?mode=tmdb.MovieRecomShow&url='+quote_plus(url)
		xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
	else:
		xx.NF("Não há recomendações")
def MovieRecomShow(type="recommendations"):
	mdb = xx.OpenURL('https://api.themoviedb.org/3/movie/'+url+'/'+type+'?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries = json.loads(mdb)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	trak = xx.traktM()
	#ST(trak)
	for entry in entries['results']:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries['results']) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
			#ST(mm)
			pc = 1 if str(mm["tmdb_id"]) in trak else None
			#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
			#xx.AddDir(str(pc), str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True)
		except:
			pass
	progress.close()
def tvshow_recom():
	mdb = xx.OpenURL('https://api.themoviedb.org/3/tv/'+url+'/recommendations?api_key=bd6af17904b638d482df1a924f1eabb4')
	entries = json.loads(mdb)
	#ST(entries['results'])
	#return
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	for entry in entries['results']:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries['results']) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			meta = mg.get_tvshow_details(title="", tmdb_id=str(entry["id"]), ignore_cache=MUcache, lang=MUlang)
			xx.AddDir(entry["name"], str(entry["id"]), "trakt.Shows", isFolder=True, dados={'meta': meta[-1]})
		except:
			pass
	progress.close()
#----------------------------------------
def cbID():
	#global dados
	import trtv
	mm = mg.get_tmdb_details(tmdb_id=url, imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
	dados2 = {}
	dados2["mmeta"] = mm
	dados2["RS"] = eval(dados)["RS"]
	#dados = dados2
	trtv.PlayUrlMovie(dados2)
	#ST(dados2)
	#RP = '{0}?mode=tmdb.Opcoes&url={1}&dados={2}'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados2)))
	#xbmc.executebuiltin('PlayMedia("'+RP+'")')
def Opcoes():
	import trtv
	dados2 = eval(dados)
	#ST(dados2["RS"])
	'''try:
		ano = str(dados2["mmeta"]["year"])
	except:
		ano = ""'''
	#ST(dados2["mmeta"])
	options = ['Play em Trailers.to']
	if Ctor:
		options.append('Elementum')
		options.append('Busca Google (título original)')
		options.append('Busca Google (título pt-br)')
		options.append('Busca Google digitar o título')
		options.append('Buscar em Comando Torrents')
		options.append('Buscar em Megatorrents HD')
	if len(cDirtrtvDown) > 2:
		options.append('Download em Trailers.to')
	if len(options) == 1 or "RS" in dados2: 
		trtv.PlayUrlMovie()
		return
	sel = xbmcgui.Dialog().contextmenu(options)
	#ST(len(options))
	if sel == -1: return
	if options[sel] == "Play em Trailers.to": #play
		trtv.PlayUrlMovie()
		#DownloadTrtv()
	elif options[sel] == "Download em Trailers.to": #download
		RP = '{0}?mode=tmdb.DownloadTrtv&url={1}&dados={2}'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)))
		xbmc.executebuiltin('RunPlugin("'+RP+'")')
		#RP = '{0}?mode=tmdb.DownloadTrtv&url={1}&dados={2}'.format(sys.argv[0], quote_plus(url), quote_plus(str(dados)))
		#xbmc.executebuiltin('RunPlugin("'+RP+'")')
	elif options[sel] == "Elementum":
		#xx.PlayUrl(name, "https://s1.movies.futbol/web-sources/475DC76CEA238433/56000/filme|referer=https://trailers.to/&Host=s1.movies.futbol&User-Agent=Mozilla/5.0&Keep-Alive=115&Connection=keep-alive", srt=True)
		#return
		xx.PlayUrl(name, "plugin://plugin.video.elementum/library/movie/play/"+url+"?doresume=true&type=movie", srt=True)
		#xx.PlayUrl(name, "http://vod.cometa.link:8081/d/RedeCanais/RedeCanais/RCFServer5/ondemand/TOMEJRYOFLME.mp4?mu3zAQc9HC3GbwJq=3_hEjfZkoqXNkh4kaaq64A&3U1G7qaTxrPbalZnEx=1620351348|referer=http://gamesgo.fun&User-Agent=Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100110 Firefox/11.0&redecanaisAS")
	elif options[sel] == "Busca Google (título original)":
		GoogleDublado("https://www.google.com/search?q="+quote_plus(dados2["mmeta"]["title"])+"+torrent+dublado+")
	elif options[sel] == "Busca Google (título pt-br)":
		mdb = xx.OpenURL('http://api.themoviedb.org/3/movie/'+str(dados2["mmeta"]["tmdb_id"])+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=pt-br')
		mdbj = json.loads(mdb)
		GoogleDublado("https://www.google.com/search?q="+quote_plus(mdbj["title"])+"+torrent+filme+dublado", mdbj["title"])
	elif options[sel] == "Busca Google digitar o título":
		d = xbmcgui.Dialog().input("Digite o título do filme")
		GoogleDublado("https://www.google.com/search?q="+quote_plus(d)+"+torrent+filme+dublado")
	elif options[sel] == "Buscar em Comando Torrents":
		mdb = xx.OpenURL('http://api.themoviedb.org/3/movie/'+str(dados2["mmeta"]["tmdb_id"])+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=pt-br')
		mdbj = json.loads(mdb)
		GoogleDublado("https://www.google.com/search?q="+quote_plus(mdbj["title"])+"+site%3Ahttps%3A%2F%2Fcomandotorrents.org", mdbj["title"])
	elif options[sel] == "Buscar em Megatorrents HD":
		mdb = xx.OpenURL('http://api.themoviedb.org/3/movie/'+str(dados2["mmeta"]["tmdb_id"])+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=pt-br')
		mdbj = json.loads(mdb)
		GoogleDublado("https://www.google.com/search?q="+quote_plus(mdbj["title"])+"+site%3Ahttp%3A%2F%2Fmegatorrentshd.net", mdbj["title"])
def GoogleDublado(links, top="Selecione o torrent"):
	try:
		googles = xx.OpenURL(links)
	except:
		googles = ""
	googlere = re.compile(";url=([^\"]+)\&amp;ved\=").findall(googles)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	list = []
	listao = []
	totalmag = 0
	for links in googlere[:6]:
		if (progress.iscanceled()): break
		try:
			magnet = xx.OpenURL(links)
		except:
			magnet= ""
		magnetre = re.compile('magnet\:\?[^\'|"]+').findall(magnet)
		#ST(magnetre)
		totalmag+=len(magnetre)
		for link in magnetre:
			if (progress.iscanceled()): break
			title = re.compile("dn=(.+?)(\&|$)").findall(link)
			if title:
				j = google.PeerSeed(link)
				if "seeds" in j:
					listao.append([(j["seeds"]), (j["peers"]), unquote(title[0][0]), link])
				else:
					listao.append([-1, -1, unquote(title[0][0]), link])
			else:
				j = google.PeerSeed(link)
				if "seeds" in j:
					listao.append([(j["seeds"]), (j["peers"]), unquote(link), link])
				else:
					listao.append([-1, -1, link, link])
		progtotal = int(100*prog/6)
		progress.update(progtotal, str(progtotal)+" %\nLinks encontrados: "+str(totalmag))
		prog+=1
	progress.close()
	listao = sorted(listao, key=lambda listao: listao[0])
	listao.reverse()
	for entry in listao:
		list.append(str(entry[0])+" / "+str(entry[1])+" "+entry[2])
	if len(listao) > 0:
		d = xbmcgui.Dialog().select(top, list)
	else:
		d = -1
	if d > -1:
		data = {'imdb': str(eval(dados)['mmeta']['tmdb_id']), 'magnet': listao[d][3]}
		common.SaveFile(data, 'magnet',  "elementum")
		xx.PlayUrl(name, "plugin://plugin.video.elementum/play?uri="+listao[d][3]+"&doresume=true&type=movie&tmdb="+str(eval(dados)['mmeta']['tmdb_id']), srt=True)
		#xbmcgui.Dialog().ok("CubeTor",listao[d][2])
#----------------------------------------
def CallFindActor():
	RP = 'plugin://plugin.video.CubeTor/?mode=tmdb.FindActor&dados&url={1}&dados={1}'.format(sys.argv[0], quote_plus(url))
	xbmc.executebuiltin("Dialog.Close(all, true)")
	xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
def FindActor():
	if not url:
		q = xbmcgui.Dialog().input("O que busca?")
	else:
		q = url
	if not q:
		RP = "plugin://plugin.video.CubeTor/?mode=&url="
		xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
		return
	RP = "plugin://plugin.video.CubeTor/?mode=tmdb.FindActorEnd&url="+quote_plus(q)
	xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
def FindActorEnd():
	global url,dados, iconimage
	q = url
	#url = "'\"Margot Robbie\"'"
	q = quote_plus(url.replace("'","").replace('"',''))
	link = xx.OpenURL("https://api.themoviedb.org/3/search/person?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&page=1&include_adult=false&query="+q)
	entries=json.loads(link)
	#ST((entries['results']))
	dados={"actor": q, "index": 0}
	if len(entries['results']) == 1:
		iconimage = "https://www.themoviedb.org/t/p/w220_and_h330_face/"+str(entries['results'][0]["profile_path"])
		xx.AddDir(unquote(dados["actor"]), str(entries['results'][0]["id"]), "tmdb.ListPlayActors", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": 0})
		RP = "plugin://plugin.video.CubeTor/?dados="+str(dados)+"&amp;iconimage="+quote_plus(iconimage)+"&amp;logos&amp;mode=tmdb.ListPlayActors&amp;name=Alexander%20Skarsg%c3%a5rd&amp;url="+str(entries['results'][0]["id"])
		xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
		#ListPlayActors()
	else:
		index=0
		for entry in entries['results']:
			#try:
			xx.AddDir(entry["name"], entry["id"], "tmdb.ListPlayActors", "https://www.themoviedb.org/t/p/w220_and_h330_face/"+str(entry["profile_path"]), isFolder=True, dados={"actor": q, "index": index})
			index+=1
			#except:
				#xx.AddDir(entry["name"], entry["id"], "tmdb.ListPlayActors", "", isFolder=True, dados={})
def ListPlayActors():
	#ST(dados)
	MaisConhecido()
	xx.AddDir("Filmes", url, "tmdb.MoviesFromActor", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
	xx.AddDir("Séries", url, "tmdb.TvShowsFromActor", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
	xx.AddDir("Produção", url, "tmdb.CrewFromActor", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
def ListPlayActors2():
	opt1 = ["Filmes","Séries"]
	d = xbmcgui.Dialog().select("Escolha a opção", opt1)
	if d == 0:
		MoviesFromActor()
	elif d == 1:
		TvShowsFromActor()
	else:
		MoviesFromActor()
def MaisConhecido():
	global dados
	trak = xx.traktM()
	try:
		dados = eval(dados)
	except:
		pass
	xx.AddDir(dados["actor"], url, "tmdb.ListPlayActors", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
	link = xx.OpenURL("https://api.themoviedb.org/3/search/person?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&page=1&include_adult=false&query="+quote_plus(dados["actor"]))
	entries=json.loads(link)
	#ST(entries)
	try:
		for entry in entries["results"][dados["index"]]["known_for"]:
			if entry["media_type"] == "tv":
				try:
					meta = mg.get_tvshow_details(title="", tmdb_id=str(entry["id"]), ignore_cache=MUcache, lang=MUlang)
					xx.AddDir(entry["name"], str(entry["id"]), "trakt.Shows", isFolder=True, dados={'meta': meta[-1]})
				except:
					pass
			elif entry["media_type"] == "movie":
				try:
					mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
					pc = 1 if str(mm["tmdb_id"]) in trak else None
					xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
				except:
					pass
	except:
		pass
def TvShowsFromActor():
	global dados
	try:
		dados = eval(dados)
	except:
		pass
	xx.AddDir(dados["actor"], url, "tmdb.ListPlayActors", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
	link = xx.OpenURL("https://api.themoviedb.org/3/person/"+url+"/tv_credits?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US")
	entries=json.loads(link)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	entries = entries['cast']
	#ST(entries)
	try:
		entries = sorted(entries, key = lambda i: (i['episode_count'],i['name']),reverse=True)
	except:
		pass
	for entry in entries:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			meta = mg.get_tvshow_details(title="", tmdb_id=str(entry["id"]), ignore_cache=MUcache, lang=MUlang)
			xx.AddDir(entry["name"], str(entry["id"]), "trakt.Shows", isFolder=True, dados={'meta': meta[-1]})
		except:
			pass
def MoviesFromActor(type='cast'):
	global dados
	try:
		dados = eval(dados)
	except:
		pass
	xx.AddDir(dados["actor"], url, "tmdb.ListPlayActors", iconimage, isFolder=True, dados={"actor": dados["actor"], "index": dados["index"]})
	trak = xx.traktM()
	link = xx.OpenURL("https://api.themoviedb.org/3/person/"+url+"/movie_credits?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US")
	entries=json.loads(link)
	entries = entries[type]
	#ST(entries)
	try:
		entries = sorted(entries, key = lambda i: (i['release_date'],i['original_title']),reverse=True)
	except:
		pass
	ST(entries)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	for entry in entries:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
			pc = 1 if str(mm["tmdb_id"]) in trak else None
			#pc = 0
			#ST(mm)
			#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			titulo = ""
			if "job" in entry:
				titulo = entry["title"] +" ["+entry["job"]+"]"
			xx.AddDir(titulo, str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
		except:
			pass
#----------------------------------------
def FindProviders(type):
	try:
		response_body = xx.OpenURL("https://api.themoviedb.org/3/"+type+"/"+url+"/watch/providers?api_key=bd6af17904b638d482df1a924f1eabb4")
		entries=json.loads(response_body)
		entries = entries["results"]["BR"]
		opt = []
		for entry in entries:
			'''if entry == "flatrate":
				opt.append("[COLOR blue]Streams[/COLOR]")
			elif entry == "buy":
				opt.append("[COLOR red]Comprar[/COLOR]")
			elif entry == "rent":
				opt.append("[COLOR red]Alugar[/COLOR]")'''
			for entry2 in entries[entry]:
				cor = "red"
				if entry == "flatrate":
					cor = "blue"
				if entry != "link":
					opt.append(str("[COLOR "+cor+"]"+entry2["provider_name"]+"[/COLOR]"))
		d = xbmcgui.Dialog().select("Providers encontrados:", opt)
	except:
		xx.NF("Nenhum Provider encontrado")
#----------------------------------------
def Collections():
	link = xx.OpenURL("https://api.themoviedb.org/3/movie/"+url+"?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US")
	entries=json.loads(link)
	if entries["belongs_to_collection"]:
		RP = 'plugin://plugin.video.CubeTor/?mode=tmdb.ShowCollections&dados&url={1}&dados={1}'.format(sys.argv[0], str(entries["belongs_to_collection"]["id"]))
		xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
	else:
		xx.NF("Não encontrado")
def ShowCollections():
	trak = xx.traktM()
	link = xx.OpenURL("https://api.themoviedb.org/3/collection/"+url+"?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US")
	entries=json.loads(link)
	entries = entries["parts"]
	try:
		entries = sorted(entries, key = lambda i: (i['release_date'],i['original_title']),reverse=False)
	except:
		pass
	#ST(entries)
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	for entry in entries:
		if "id" in entry:
			#xx.AddDir(str(entry['id']), str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True)
			if (progress.iscanceled()): break
			progtotal = int( 100*prog/len(entries) )
			progress.update(progtotal, str(progtotal)+" %")
			prog+=1
			try:
				mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
				pc = 1 if str(mm["tmdb_id"]) in trak else None
				#pc = 0
				#ST(mm)
				#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
				xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
			except:
				pass
#----------------------------------------
def RandomMovies():
	import random
	with_genres = '&with_genres='+cPagetmdbgenero if cPagetmdbgenero !="0" else ""
	primary_release_year = '&primary_release_year='+cPagetmdbano if cPagetmdbano != "Todos" else ""
	with_original_language = "&with_original_language="+cPagetmdblang if cPagetmdblang != "Todos" else ""
	#link = xx.OpenURL('https://api.themoviedb.org/3/discover/movie?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate&year=2021'+with_genres+primary_release_year+with_original_language)
	link = xx.OpenURL('https://api.themoviedb.org/3/trending/movie/week?api_key=bd6af17904b638d482df1a924f1eabb4'+with_genres+primary_release_year+with_original_language)
	entries=json.loads(link)
	ST(entries)
	#pagina = random.randint(1,100)
	pagina = random.randint(1,entries["total_pages"])
	RP = 'plugin://plugin.video.CubeTor/?mode=tmdb.RandomMoviesShow&dados&url='+str(pagina)
	xbmc.executebuiltin('ActivateWindow(10025,"'+RP+'")')
def RandomMoviesShow():
	trak = xx.traktM()
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	xx.AddDir("Novos Filmes - "+str(url), "" , "tmdb.RandomMovies" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Gênero:[/B] "+tmdbgenero[cPagetmdbgenero]+" [/COLOR]", "cPagetmdbgenero" , "tmdb.Genero" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Ano:[/B] "+tmdbano[cPagetmdbano]+" [/COLOR]", "cPagetmdbano" , "tmdb.Ano" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Língua original:[/B] "+tmdblang[cPagetmdblang]+" [/COLOR]", "cPagetmdblang" , "tmdb.Lang" ,"", isFolder=False, dados={})
	with_genres = '&with_genres='+cPagetmdbgenero if cPagetmdbgenero !="0" else ""
	primary_release_year = '&primary_release_year='+cPagetmdbano if cPagetmdbano != "Todos" else ""
	with_original_language = "&with_original_language="+cPagetmdblang if cPagetmdblang != "Todos" else ""
	try:
		#link = xx.OpenURL('https://api.themoviedb.org/3/discover/movie?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+(url)+'&with_watch_monetization_types=flatrate&year=2021'+with_genres+primary_release_year+with_original_language)
		link = xx.OpenURL('https://api.themoviedb.org/3/trending/movie/week?page='+url+'&api_key=bd6af17904b638d482df1a924f1eabb4'+with_genres+primary_release_year+with_original_language)
	except:
		return
	#link = xx.OpenURL('https://api.themoviedb.org/3/trending/movie/week?api_key=bd6af17904b638d482df1a924f1eabb4&page='+url)
	entries=json.loads(link)
	#ST(entries)
	for entry in entries['results']:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries['results']) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
			pc = 1 if str(mm["tmdb_id"]) in trak else None
			#ST(mm)
			#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
		except:
			pass
#----------------------------------------
def InTheaters(region="us"):
	trak = xx.traktM()
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	link = xx.OpenURL('https://api.themoviedb.org/3/movie/upcoming?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&page=1&region='+region)
	entries=json.loads(link)
	for entry in entries['results']:
		if (progress.iscanceled()): break
		progtotal = int( 100*prog/len(entries['results']) )
		progress.update(progtotal, str(progtotal)+" %")
		prog+=1
		try:
			mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False, lang=MUlangM)
			pc = 1 if str(mm["tmdb_id"]) in trak else None
			#ST(mm)
			#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			xx.AddDir("", str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm, 'pc': pc})
		except:
			pass
#----------------------------------------
def CategoryOrdem(x):
	x2 = Addon.getSetting(eval("x"))
	name2 = "Data" if x2=="0" else "Título"
	AddDir("[COLOR green][B][Organizado por:][/B] "+name2 +" (Clique para alterar)[/COLOR]" , x, "", "https://lh5.ggpht.com/gv992ET6R_InCoMXXwIbdRLJczqOHFfLxIeY-bN2nFq0r8MDe-y-cF2aWq6Qy9P_K-4=w300", "https://lh5.ggpht.com/gv992ET6R_InCoMXXwIbdRLJczqOHFfLxIeY-bN2nFq0r8MDe-y-cF2aWq6Qy9P_K-4=w300", isFolder=False)
#----------------------------------------
def ST(x="", o="w"):
	if o == "1":
		o = "a+"
	if type(x) == type({}) or type(x) == type([]) or type(x) == type(set([''])):
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
#-----------------------------------------
