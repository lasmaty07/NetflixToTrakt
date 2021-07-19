#!/usr/bin/python3

import os,sys,json

try:
  from pathlib import Path
  import logging,requests, datetime, csv,json
  from dotenv import load_dotenv
except:
  sys.exit("Please use your favorite mehtod to install the following module requests and simplejson to use this script")


basepath = Path()
basedir = str(basepath.cwd())
envars = basepath.cwd() / 'SECRETS.env'
load_dotenv(envars)

LOG_FILENAME = 'SyncHistoryTracktv.log'
LOG_LEVEL=logging.INFO

logging.basicConfig(filename=LOG_FILENAME,level=LOG_LEVEL)

_headers = {
  'Accept'            : 'application/json',
  'Content-Type'      : 'application/json',
  'User-Agent'        : 'Tratk importer',
  'Connection'        : 'Keep-Alive',
  'trakt-api-version' : '2',
  'trakt-api-key'     : os.getenv("TRATK_API_KEY"),
  'Authorization'     : 'Bearer ' + os.getenv("TOKEN"),
}

_final_request = {"movies":[],"episodes": []}
_duplicates = {"movies": {}, "episodes":{}}
_baseurl = 'https://api.trakt.tv'
csvFile=open(os.getenv("FILE"), newline='')

def read_csv(file):
        reader = csv.reader(file, delimiter=',')
        return dict(reader)

def api_auth():
        """API call for authentification OAUTH"""
        print("Open the link in a browser and paste the pincode when prompted")
        print(("https://trakt.tv/oauth/authorize?response_type=code&"
              "client_id={0}&redirect_uri=urn:ietf:wg:oauth:2.0:oob".format(
                  os.getenv("TRATK_API_KEY"))))
        pincode = str(input('Input:'))
        url = 'https://api.trakt.tv' + '/oauth/token'
        values = {
            "code": pincode,
            "client_id": os.getenv("TRATK_API_KEY"),
            "client_secret": os.getenv("TRATK_API_SECRET"),
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        }

        request = requests.post(url, data=values)
        response = request.json()
        _headers['Authorization'] = 'Bearer ' + response["access_token"]
        _headers['trakt-api-key'] = os.getenv("TRATK_API_KEY")
        print('Save as "oauth_token" in file {0}: {1}'.format(envars, response["access_token"]))

def search():
  """Search movies or tv shows and find it's trakt id"""
  global _final_request
  m = {}
  for item_to_search in _items:

    if item_to_search.find(':')>0:
      pos1 = item_to_search.find(':')
      pos2 = item_to_search[item_to_search.find(':')+2:].find(':')
      show_title = item_to_search[:pos1]
      episode_name = item_to_search[pos1+pos2+2+2:]

      title = episode_name
      response = requests.get(_baseurl + '/search/episode?query='+title.replace(' ','%20'), headers=_headers)
      type = 'episode'
      type2 = 'episodes'
    else:
      title = item_to_search
      response = requests.get(_baseurl + '/search/movie?query='+title.replace(' ','%20'), headers=_headers)
      type = 'movie'
      type2 = 'movies'
      
    if response:
      json_data = json.loads(response.text)
      i = 0
      item_found_prev = {type:{}}
      for item_found in json_data:

        if item_found[type]['title'].lower() == title.lower() and (type == 'movie' or item_found['show']['title'] == show_title):
          
          watched_at = datetime.datetime.strptime(_items[item_to_search], '%m/%d/%y')
          # time un 2020-09-12T00:00:00.000Z 
          m = {"watched_at": watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
          "title": item_found[type]['title'],
          "ids": {
            "trakt": item_found[type]['ids']['trakt'],
            "imdb": item_found[type]['ids']['imdb']
            }
          }

          if i!=0 and item_found[type]['title'].lower() == item_found_prev[type]['title'].lower():
            addDuplicate(item_found,item_to_search,type,type2,watched_at)

          item_found_prev = item_found
          i = i + 1 
      else:
        if m !={} and i==1:
          _final_request[type2].append(m)

def addDuplicate(item_found,item_to_search,type,type2,watched_at):
  global _duplicates

  item = {"title":item_found[type]['title'],
          "year" : str(item_found[type]['year']),
          "Imdb_id": (item_found[type]['ids']['imdb'] if item_found[type]['ids']['imdb'] else 'null'),
          "trakt":item_found[type]['ids']['trakt'],
          "URL": ' https://trakt.tv/movies/'+ str(item_found[type]['ids']['trakt']),
          "watched_at":watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
          "validated":"False"
    }

  if item_to_search in _duplicates[type2]:
    _duplicates[type2][item_to_search].append(item)
  else:
    _duplicates[type2][item_to_search] = []
    _duplicates[type2][item_to_search].append(item)

def importValidatedDuplicates():
  file = 'duplicates.json'
  try:
    f = open(file,)
    data = json.load(f)
    print(data)
    for movie in data['movies']:
      for item_found in data['movies'][movie]:
        if item_found['validated'] == 'True':
            m = {"watched_at": item_found['watched_at'],
            "title": item_found['title'],
            "ids": {
              "trakt": item_found['trakt'],
              "imdb": item_found['Imdb_id']
              }
            }
            _final_request['movies'].append(m)
  except Exception as e:
    print(f'no file {file}. ',e)

def main():
  #load from csv
  global _items
  _items = read_csv(csvFile)

  if not(os.getenv("TOKEN")):
    api_auth()

  print(_headers)

  print('Found ' + str(len(_items)) + ' items to import\n')
  search()
  if len(_duplicates['movies'])>0:
    print('\nFound duplicate movies check duplicates.json\n')

  if len(_duplicates['episodes'])>0:
    print('\nFound duplicate episodes check duplicates.json\n')    

  importValidatedDuplicates()
  print('\n--------------------Final Request--------------------\n')
  print(json.dumps(_final_request))
  
  with open('duplicates.json', 'w') as f:
    print(json.dumps(_duplicates), file=f)

  with open('final.json', 'w') as f:
    print(json.dumps(_final_request), file=f)

  # invoke   
  response =requests.post( _baseurl + '/sync/history',data=json.dumps(_final_request), headers=_headers)
  print(response)

  print('\n------------Exiting Program------------\n')
  sys.exit(0)

if __name__ == '__main__':
  main()