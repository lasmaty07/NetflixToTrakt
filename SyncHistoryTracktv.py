#!/usr/bin/python3

import os,sys

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

_final_request = {}
_movies_matched = []
_shows_matched = []
_duplicates = {"movies": [], "episodes":[]}
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

def search_movies():
  global _final_request,_duplicates
  m = {}
  for movie_to_search in _items:
    movie_title = movie_to_search.replace(' ','%20')
    response = requests.get(_baseurl + '/search/movie?query='+movie_title, headers=_headers)
    if response:
      json_data = json.loads(response.text)
      i = 0
      for movie in json_data:            
        if movie['movie']['title'] == movie_to_search:
          i += 1 
          watched_at = datetime.datetime.strptime(_items[movie_to_search], '%m/%d/%y')
          # time un 2020-09-12T00:00:00.000Z 
          m = {"watched_at": watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
          "title": movie['movie']['title'],
          "ids": {
            "trakt": movie['movie']['ids']['trakt'],
            "imdb": movie['movie']['ids']['imdb']
            }
          }
          if i >1:
            _duplicates['movies'].append(movie['movie']['title'] + ' ' + str(movie['movie']['year']) + ' Imdb id: '+ (movie['movie']['ids']['imdb'] if movie['movie']['ids']['imdb'] else 'null') + ' https://trakt.tv/movies/'+ str(movie['movie']['ids']['trakt']))
      else:
        if m !={} and i==1:
          _movies_matched.append(m)
  if _movies_matched:          
    _final_request['movies'] = _movies_matched

def search_shows():
  global _final_request,_duplicates
  e = {}
  for show_to_search in _items:
    pos1 = show_to_search.find(':')
    pos2 = show_to_search[show_to_search.find(':')+2:].find(':')
    show_title = show_to_search[:pos1]
    episode_name = show_to_search[pos1+pos2+2+2:]

    title = episode_name.replace(' ','%20')
    response = requests.get(_baseurl + '/search/episode?query='+title, headers=_headers)
    if response:
      json_data = json.loads(response.text)
      i = 0
      for episode in json_data:            
        if episode['episode']['title'] == episode_name and episode['show']['title'] == show_title:
          i += 1 
          watched_at = datetime.datetime.strptime(_items[show_to_search], '%m/%d/%y')
          # time un 2020-09-12T00:00:00.000Z 
          e = {
              "watched_at": watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
              "ids": {
                  "trakt": episode['episode']['ids']['trakt'],
                  "imdb": episode['episode']['ids']['imdb']
              }
          }
          if i >1:
            _duplicates['movies'].append(show_to_search)
      else:
        if e !={} and i==1:
          _shows_matched.append(e)
  if _shows_matched:
    _final_request['episodes'] = _shows_matched

def main():
  #load from csv
  global _items
  _items = read_csv(csvFile)

  if not(os.getenv("TOKEN")):
    api_auth()

  print(_headers)

  print('Found ' + str(len(_items)) + ' items to import\n')
  search_movies()
  search_shows()
  print('\nFound duplicates\n')
  print(_duplicates)
  print('\nFinal Request\n')
  print(_final_request)
  
  with open('duplicates.json', 'w') as f:
    print(json.dumps(_duplicates), file=f)

  # invoke   
  response =requests.post( _baseurl + '/sync/history',data=json.dumps(_final_request), headers=_headers)
  print(response)

  sys.exit(0)

if __name__ == '__main__':
  main()