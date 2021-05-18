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
import xx, comando, comandotv, google, elementum, trakt, tmdb, trtv, download

addon_data_dir = xbmcvfs.translatePath(Addon.getAddonInfo("profile"))
cacheDir = os.path.join(addon_data_dir, "cache")

Ctrakt = Addon.getSetting("Ctrakt") if Addon.getSetting("Ctrakt") != "" else None
cDirtrtv = Addon.getSetting("cDirtrtv") if Addon.getSetting("cDirtrtv") != "" else None

if not os.path.exists(cacheDir):
	os.makedirs(cacheDir)

def Categories(): #0
	if Ctrakt:
		xx.AddDir("Series Trakt (Vistas)", "", "trakt.ListSeriesVistas", isFolder=True)
		xx.AddDir("Series Trakt (Coletadas)", "", "trakt.ListSeriesColetadas", isFolder=True)
		xx.AddDir("Series Trakt (Watchlist)", "", "trakt.ListSeriesWatchList", isFolder=True)
	xx.AddDir("Filmes Populares (TMDB)", "", "tmdb.ListMovies", isFolder=True)
	xx.AddDir("Histórico Filmes (Elementum)", "", "tmdb.Historico", isFolder=True)
	if cDirtrtv:
		xx.AddDir("Trtv.to", "", "trtv.Categories", isFolder=True)
	xx.AddDir("Series Elementum", "", "elementum.ListSeries", isFolder=True)
	xx.AddDir("Comando.org", "", "comando.org", isFolder=True)
	xx.AddDir("Comando.TV", "", "comando.tv", isFolder=True)
	xx.AddDir("Busca no Google", "", "google.Busca", isFolder=True)
def comandoorg():
	xx.AddDir("Principal", "", "comando.Principal", isFolder=True)
	xx.AddDir("Dublados", "", "comando.Dublado", isFolder=True)
def comandoTV():
	xx.AddDir("2021", "", "comandotv.2021", isFolder=True)
	xx.AddDir("Dublados", "", "comandotv.Dublado", isFolder=True)
	xx.AddDir("Filmes", "", "comandotv.Filmes", isFolder=True)

	
params = urllib.parse.parse_qs(sys.argv[2][1:]) 
name = params.get('name',[None])[0]
url = params.get('url',[None])[0]
mode = params.get('mode',[None])[0]
iconimage = params.get('iconimage',[None])[0]
logos = params.get('logos',[None])[0]
info = params.get('info',[None])[0]
dados = params.get('dados',[{}])[0]
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

if mode == None:
	Categories()
	xx.setViewM()
elif mode == "comando.org":
	comandoorg()
	xx.setViewM2()
elif mode == "comando.tv":
	comandoTV()
	xx.setViewM2()
#-------------------------------
elif mode == "trtv.Categories":
	trtv.Categories()
	xx.setViewM()
elif mode == "trtv.SeriesFolder":
	trtv.SeriesFolder()
	xx.setViewS()
elif mode == "trtv.EpisodesFolder":
	trtv.EpisodesFolder()
	xx.setViewS2()
elif mode == "trtv.MoviesFolder":
	trtv.MoviesFolder()
	xx.setViewM()
elif mode == "download.StopDownload":
	download.StopDownload()
elif mode == "trtv.Busca":
	trtv.Busca()
	xx.setViewM2()
elif mode == "trtv.Episodes":
	trtv.Episodes()
	xx.setViewS2()
elif mode == "trtv.DownloadMP4":
	trtv.DownloadMP4()
elif mode == "trtv.ResumeFile":
	trtv.ResumeFile()
elif mode == "trtv.PlayFile":
	trtv.PlayFile()
elif mode == "trtv.DeleteFile":
	trtv.DeleteFile()
#-------------------------------
elif mode == "tmdb.ListMovies":
	tmdb.ListMovies()
	xx.setViewS()
elif mode == "tmdb.Genero":
	tmdb.Genero()
elif mode == "tmdb.Ano":
	tmdb.Ano()
elif mode == "tmdb.Opcoes":
	tmdb.Opcoes()
elif mode == "tmdb.Historico":
	tmdb.Historico()
	xx.setViewM()
#-------------------------------
elif mode == "trakt.ListSeriesVistas":
	trakt.ListSeries()
	xx.setViewS()
elif mode == "trakt.ListSeriesColetadas":
	trakt.ListSeries("collection")
	xx.setViewS()
elif mode == "trakt.ListSeriesWatchList":
	trakt.ListSeries("watchlist")
	xx.setViewS()
elif mode == "trakt.Seasons":
	trakt.Seasons()
	xx.setViewS()
elif mode == "trakt.Episodes":
	trakt.Episodes()
	xx.setViewS2()
#-------------------------------
elif mode == "xx.PaginacaoMenos":
	xx.PaginacaoMenos()
elif mode == "xx.PaginacaoMais":
	xx.PaginacaoMais()
#-------------------------------
elif mode == "elementum.ListSeries":
	elementum.ListSeries()
	xx.setViewS()
elif mode == "elementum.Seasons":
	elementum.Seasons()
	xx.setViewS()
elif mode == "elementum.Episodes":
	elementum.Episodes()
	xx.setViewS2()
#-------------------------------
elif mode == "comando.Principal":
	comando.Torrents("https://comandotorrents.org/")
	xx.setViewM2()
elif mode == "comando.Dublado":
	comando.Torrents("https://comandotorrents.org/category/dublado/")
	xx.setViewM2()
elif mode == "comando.ListTorrents":
	comando.ListTorrents()
	xx.setViewM2()
elif mode == "comando.PlayTorrents":
	comando.PlayTorrents()
#-------------------------------
elif mode == "comandotv.Dublado":
	comandotv.Torrents("https://comandotorrent.tv/category/dublado/")
	xx.setViewM2()
elif mode == "comandotv.Filmes":
	comandotv.Torrents("https://comandotorrent.tv/category/filmes/")
	xx.setViewM2()
elif mode == "comandotv.2021":
	comandotv.Torrents("https://www.comandotorrent.tv/category/2021/")
	xx.setViewM2()
elif mode == "comandotv.ListTorrents":
	comandotv.ListTorrents()
	xx.setViewM2()
elif mode == "comandotv.PlayTorrents":
	comandotv.PlayTorrents()
#-------------------------------
elif mode == "PlayUrl":
	xx.PlayUrl(name, url)
elif mode == "PlayUrlLeg":
	xx.PlayUrl(name, url, True)
elif mode == "google.Busca":
	google.Busca()
	xx.setViewM2()
elif mode == "google.BuscaCat":
	google.BuscaCat()
	xx.setViewM2()
#-------------------------------
elif mode == "Reload":
	xbmc.executebuiltin("Container.Refresh()")
#-------------------------------
xbmcplugin.endOfDirectory(int(sys.argv[1]))