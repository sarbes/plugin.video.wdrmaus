# -*- coding: utf-8 -*-
"""
Attributes:
        subtitle (bool): Display subtitles with the video
        signlang (bool): Use the sign-language version of the video
        viddesc  (bool): Use the video description version of the video
"""
import libwdr
import re
import requests
import xbmcaddon

ArchiveXml = 'http://www.wdrmaus.de/_export/videositemap.php5'
CurrentXml = 'http://www.wdrmaus.de/aktuelle-sendung/index.php5'
PreviousXml = 'http://www.wdrmaus.de/aktuelle-sendung/vorwoche.php5'

ADDON = xbmcaddon.Addon(id='plugin.video.wdrmaus')

class wdrmaus(libwdr.libwdr):
	def __init__(self):
		libwdr.libwdr.__init__(self)
		self.modes['mausListVideos'] = self.mausListVideos

	def libWdrListMain(self):
		result = {'items':[],'name':'root'}

		response = requests.get(CurrentXml).text
		d = {'metadata':{'art':{}}, 'params':{'mode':'libWdrPlayJs'}, 'type':'video'}
		d['metadata']['name'] = (re.compile('name\" : \"(.+?)\"', re.DOTALL).findall(response))[1]
		d['metadata']['plot'] = (re.compile('<p>(.+?)\</p>', re.DOTALL).findall(response))[0]
		d['metadata']['art']['thumb'] = (re.compile('thumbnailURL\" : \[ \"(.+?)\"', re.DOTALL).findall(response))[0]
		d['params']['url'] = re.search('https://kinder(.+?)jsonp', response)[0]
		d['params']['uservideomode'] = self.getVideoMode()
		result['items'].append(d)
		
		response = requests.get(PreviousXml).text
		d = {'metadata':{'art':{}}, 'params':{'mode':'libWdrPlayJs'}, 'type':'video'}
		d['metadata']['name'] = (re.compile('name\" : \"(.+?)\"', re.DOTALL).findall(response))[1]
		d['metadata']['plot'] = (re.compile('<p>(.+?)\</p>', re.DOTALL).findall(response))[0]
		d['metadata']['art']['thumb'] = (re.compile('thumbnailURL\" : \[ \"(.+?)\"', re.DOTALL).findall(response))[0]
		d['params']['url'] = re.search('https://kinder(.+?)jsonp', response)[0]
		d['params']['uservideomode'] = self.getVideoMode()
		result['items'].append(d)
		
		response = requests.get(ArchiveXml).text
		categories = re.compile('<video:category>(.+?)</video:category>', re.DOTALL).findall(response)
		names = []
		for cat in categories:
			if not cat in names:
				result['items'].append({'metadata':{'name':cat}, 'params':{'mode':'mausListVideos', 'cat':cat}, 'type':'dir'})
				names.append(cat)
		return result
	
	def mausListVideos(self):
		result = {'items':[]}
		response = requests.get(ArchiveXml).text
		videos = re.compile('<url>(.+?)</url>', re.DOTALL).findall(response)
		for video in videos:
			if self.params['cat'] == re.compile('<video:category>(.+?)</video:category>', re.DOTALL).findall(video)[0]:
				d = {'metadata':{'art':{}}, 'params':{'mode':'libWdrPlayJs'}, 'type':'video'}
				d['metadata']['name'] = re.compile('<video:title><!\[CDATA\[(.+?)\]\]></video:title>', re.DOTALL).findall(video)[0].replace('![CDATA[','').replace(']]','')
				d['metadata']['art']['thumb'] = re.compile('<video:thumbnail_loc>(.+?)</video:thumbnail_loc>', re.DOTALL).findall(video)[0].replace('<![CDATA[','').replace(']]>','')
				d['params']['url'] = re.compile('<video:player_loc.+?>(.+?)</video:player_loc>', re.DOTALL).findall(video)[0].replace('<![CDATA[','').replace(']]>','')
				d['params']['uservideomode'] = self.getVideoMode()
				result['items'].append(d)
		return result
	
	def getVideoMode(self):
		result = 'none'
		if ADDON.getSetting('subtitle') == 'true':
			result = 'subtitle'
		if ADDON.getSetting('signlang') == 'true':
			result = 'signlang'
		if ADDON.getSetting('viddesc') == 'true':
			result = 'viddesc'
		return result

o = wdrmaus()
o.action()