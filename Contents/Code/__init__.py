import urllib, json, zipfile, os

TITLE = 'Plexopedia'
PREFIX = '/video/plexopedia'

ICON  = 'icon-default.png'
ART = 'art-default.jpg'

BASE_URL = 'http://www.plexopedia.com'
CATEGORIES_URL = '/api/categories'
SEARCH_URL = '/api/channel_search'
DOWNLOAD_URL = '/api/download'

GITHUB_URL = 'https://github.com'

PLUGIN_PATH = '';

def Start():
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'AppleTV/7.2 iOS/8.3 AppleTV/7.2 model/AppleTV3,2 build/12F69 (3; dt:12)'

	global PLUGIN_PATH
	if 'LOCALAPPDATA' in os.environ:
		PLUGIN_PATH = os.getenv('LOCALAPPDATA') + '/Plex Media Server/Plug-ins/'
	elif 'PLEX_HOME' in os.environ:
		PLUGIN_PATH = os.getenv('PLEX_HOME') + '/Library/Application Support/Plex Media Server/Plug-ins/'
	elif 'HOME' in os.environ:
		PLUGIN_PATH = os.getenv('HOME') + '/Library/Application Support/Plex Media Server/Plug-ins'
	else:
		PLUGIN_PATH = ''

@handler(PREFIX, TITLE)
def MainMenu():
	Log(Core.storage)
	oc = ObjectContainer()
	oc.view_group = 'List'
	url = BASE_URL + CATEGORIES_URL
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	oc.add(
		DirectoryObject(
			key = Callback(Collections, title = 'Show All', id = None),
			title = 'Show All'
		)
	)

	for item in data:
		title = item['name']
		id = item['tid']

		oc.add(
			DirectoryObject(
				key = Callback(Collections, title = title, id = id),
				title = title
			)
		)

	title = unicode("Search")
	oc.add(
		InputDirectoryObject(
			key = Callback(Search),
			title = title,
			prompt = title,
			thumb = R('search.png'),
			art = R(ART)
		)
	)
	return oc

def Search(query):

	oc = ObjectContainer(title2='Search Results')
	oc.view_group = 'Details'
	oc.add(PrefsObject(title=L('Preferences')))
	url = BASE_URL + SEARCH_URL + '?keys=' + unicode(String.Quote(query))
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	for item in data['channels']:
		title = item['channel']['title'] + ' (Rating: '
		id = item['channel']['nid']
		img = item['channel']['field_icon']['src']
		description = item['channel']['field_long_description']
		maxint = int(float(item['channel']['field_rating']))
		for x in range(0, maxint):
			title = title + '*'
		title = title + ')'
		oc.add(
			DirectoryObject(
				key = Callback(Download, title = title, id = id),
				title = title,
				thumb = img,
				summary = description
			)
		)
	return oc

@route(PREFIX + '/collections')
def Collections(title, id):
	Log(PLUGIN_PATH)
	
	oc = ObjectContainer(title2=unicode(title))
	oc.view_group = 'Details'
	oc.add(PrefsObject(title=L('Preferences')))
	addon = ' '
	if id is not None:
		addon = '?field_category_tid=' + id
	
	url = BASE_URL + SEARCH_URL + addon
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	for item in data['channels']:
		title = item['channel']['title'] + ' (Rating: '
		id = item['channel']['nid']
		img = item['channel']['field_icon']['src']
		description = item['channel']['field_long_description']
		maxint = int(float(item['channel']['field_rating']))
		for x in range(0, maxint):
			title = title + '*'
		title = title + ')'
		oc.add(
			DirectoryObject(
				key = Callback(Download, title = title, id = id),
				title = title,
				thumb = img,
				summary = description
			)
		)
	return oc
	
def Download(title, id):
	url = BASE_URL + DOWNLOAD_URL + '/' + id
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	zip, headers = urllib.urlretrieve(GITHUB_URL + data['file'])
	z = zipfile.ZipFile(zip)
	for name in z.namelist():
		z.extract(name, PLUGIN_PATH)
	src = PLUGIN_PATH + data['basename'] + '-' + data['type']
	dst = PLUGIN_PATH + data['basename']
	os.rename(src, dst)
	return ObjectContainer(title2 = unicode(title), message='Plugin installed/updated')