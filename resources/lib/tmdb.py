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
import xx, google

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
cPagetmdb = "0" if Addon.getSetting("cPagetmdb")=="" else Addon.getSetting("cPagetmdb") #paginacao Filmes
cPagetmdbgenero = "0" if Addon.getSetting("cPagetmdbgenero")=="" else Addon.getSetting("cPagetmdbgenero") #paginacao Genero
cPagetmdbano = "xxxx" if Addon.getSetting("cPagetmdbano")=="" else Addon.getSetting("cPagetmdbano") #paginacao Genero
tmdbgenero = {"0": "Todos", "28": "Ação", "16":"Animação", "12":"Aventura", "35":"Comédia", "80":"Crime", "99":"Documentário", "18":"Drama", "10751":"Família", "14":"Fantasia", "27":"Horror", "878":"Sci-fi", "53":"Thriller"}
tmdbano = {"xxxx" :"Todos", "2021":"2021", "2020":"2020", "2019":"2019", "2018":"2018", "2017":"2017", "2016":"2016", "2015":"2015", "2014":"2014", "2013":"2013", "2012":"2012", "2011":"2011", "2010":"2010"}
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
	d = xbmcgui.Dialog().select("Selecione o gênero", ano)
	if d >-1:
		Addon.setSetting(url, ano2[d] )
		xbmc.executebuiltin("Container.Refresh()")
#-----------------------------------------
def ListMovies():
	xx.AddDir("[COLOR white][B]Gênero:[/B] "+tmdbgenero[cPagetmdbgenero]+" [/COLOR]", "cPagetmdbgenero" , "tmdb.Genero" ,"", isFolder=False, dados={})
	xx.AddDir("[COLOR white][B]Ano:[/B] "+tmdbano[cPagetmdbano]+" [/COLOR]", "cPagetmdbano" , "tmdb.Ano" ,"", isFolder=False, dados={})
	if int(cPagetmdb) > 0:
		xx.AddDir("[COLOR blue][B]<< Pagina Anterior ["+ str( int(cPagetmdb) ) +"[/B]][/COLOR]", cPagetmdb , "xx.PaginacaoMenos" ,"http://icons.iconarchive.com/icons/iconsmind/outline/256/Previous-icon.png", isFolder=False, dados={'page': 'cPagetmdb'})
	xx.AddDir("[COLOR blue][B]Proxima Pagina >>  ["+ str( int(cPagetmdb) + 1 ) +"[/B]][/COLOR]", cPagetmdb , "xx.PaginacaoMais" ,"http://icons.iconarchive.com/icons/iconsmind/outline/256/Next-2-2-icon.png", isFolder=False, dados={'page': 'cPagetmdb'})
	l = int(cPagetmdb) * 4
	progress = xbmcgui.DialogProgress()
	progress.create('Carregando...')
	progress.update(0, "Carregando...")
	prog = 1
	for page in range (1,5):
		with_genres = '&with_genres='+cPagetmdbgenero if cPagetmdbgenero !="0" else ""
		primary_release_year = '&primary_release_year='+cPagetmdbano if cPagetmdbano != "xxxx" else ""
		link = xx.OpenURL('https://api.themoviedb.org/3/discover/movie?api_key=bd6af17904b638d482df1a924f1eabb4&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(page+l)+'&with_watch_monetization_types=flatrate&year=2021'+with_genres+primary_release_year)
		entries=json.loads(link)
		for entry in entries['results']:
			if (progress.iscanceled()): break
			progtotal = int( 100*prog/len(entries['results'])/4 )
			progress.update(progtotal, str(progtotal)+" %")
			prog+=1
			try:
				mm = mg.get_tmdb_details(tmdb_id=str(entry['id']), imdb_id="", tvdb_id="", title="", year="", media_type="movies", preftype="", manual_select=False, ignore_cache=False)
				#ST(mm)
				#xx.AddDir(str(entry['id']), "plugin://plugin.video.elementum/library/movie/play/"+str(entry['id'])+"?doresume=true", "PlayUrl", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
				xx.AddDir(str(entry['id']), str(entry['id']), "tmdb.Opcoes", isFolder=False, IsPlayable=True, dados={'mmeta': mm})
			except:
				pass
	progress.close()
#----------------------------------------
def Opcoes():
	dados2 = eval(dados)
	ano = str(dados2["mmeta"]["year"])
	#ST(dados2["mmeta"])
	options = []
	options.append('Elementum')
	options.append('Busca Google (título original)')
	options.append('Busca Google (título pt-br)')
	options.append('Busca Google digitar o título')
	sel = xbmcgui.Dialog().contextmenu(options)
	if sel == 0:
		xx.PlayUrl(name, "plugin://plugin.video.elementum/library/movie/play/"+url+"?doresume=true")
	elif sel == 1:
		GoogleDublado("https://www.google.com/search?q="+quote_plus(dados2["mmeta"]["title"])+"+torrent+dublado+")
	elif sel == 2:
		mdb = xx.OpenURL('http://api.themoviedb.org/3/movie/'+str(dados2["mmeta"]["tmdb_id"])+'?api_key=bd6af17904b638d482df1a924f1eabb4&language=pt-br')
		mdbj = json.loads(mdb)
		GoogleDublado("https://www.google.com/search?q="+quote_plus(mdbj["title"])+"+torrent+filme+dublado")
	elif sel == 3:
		d = xbmcgui.Dialog().input("Digite o título do filme")
		GoogleDublado("https://www.google.com/search?q="+quote_plus(d)+"+torrent+filme+dublado")
def GoogleDublado(links):
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
					listao.append([0, 0, title[0][0], link])
			else:
				j = google.PeerSeed(link)
				if "seeds" in j:
					listao.append([(j["seeds"]), (j["peers"]), unquote(link), link])
				else:
					listao.append([0, 0, link, link])
		progtotal = int(100*prog/6)
		progress.update(progtotal, str(progtotal)+" %\nLinks encontrados: "+str(totalmag))
		prog+=1
	progress.close()
	listao = sorted(listao, key=lambda listao: listao[0])
	listao.reverse()
	for entry in listao:
		list.append(str(entry[0])+" / "+str(entry[1])+" "+entry[2])
	if len(listao) > 0:
		d = xbmcgui.Dialog().select("Selecione o torrent", list)
	else:
		d = -1
	if d > -1:
		xx.PlayUrl(name, "plugin://plugin.video.elementum/play?uri="+listao[d][3]+"?doresume=true")
		#xbmcgui.Dialog().ok("CubeTor",listao[d][2])
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
		y = str(str(x).encode("utf-8"))
	Path = xbmc.translatePath( xbmcaddon.Addon().getAddonInfo('path') )
	py = os.path.join( Path, "study.txt")
	#file = open(py, "a+")
	file = open(py, o)
	file.write(y+"\n"+str(type(x)))
	file.close()
#-----------------------------------------
