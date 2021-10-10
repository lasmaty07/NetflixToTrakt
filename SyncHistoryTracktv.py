#!/usr/bin/python3

import os, sys, json, logging, requests
from pathlib import Path
from netflix_items import NetflixItems

try:
    from dotenv import load_dotenv
except:
    sys.exit("please run: pip install -r requirements.txt")


basepath = Path()
basedir = str(basepath.cwd())
envars = basepath.cwd() / "SECRETS.env"
load_dotenv(envars)

LOG_FILENAME = "SyncHistoryTracktv.log"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVEL)


_final_request = {"movies": [], "episodes": []}
_duplicates = {"movies": {}, "episodes": {}}
csvFile = os.getenv("FILE")


def api_auth(items):
    """
    API call for authentification OAUTH
    """
    if not (os.getenv("TOKEN")):
        print("Open the link in a browser and paste the pincode when prompted")
        print(
            (
                "https://trakt.tv/oauth/authorize?response_type=code&"
                "client_id={0}&redirect_uri=urn:ietf:wg:oauth:2.0:oob".format(os.getenv("TRATK_API_KEY"))
            )
        )
        pincode = str(input("Input:"))
        url = "https://api.trakt.tv" + "/oauth/token"
        values = {
            "code": pincode,
            "client_id": os.getenv("TRATK_API_KEY"),
            "client_secret": os.getenv("TRATK_API_SECRET"),
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code",
        }

        request = requests.post(url, data=values)
        response = request.json()
        items._headers["Authorization"] = "Bearer " + response["access_token"]
        items._headers["trakt-api-key"] = os.getenv("TRATK_API_KEY")
        print('Save as "oauth_token" in file {0}: {1}'.format(envars, response["access_token"]))


def importValidatedDuplicates(file):
    validatedDuplicates = []

    try:
        f = open(
            file,
        )

        data = json.load(f)
        for movie in data["movies"]:
            for item_found in data["movies"][movie]:
                if item_found["validated"] == "True":
                    m = {
                        "watched_at": item_found["watched_at"],
                        "title": item_found["title"],
                        "ids": {
                            "trakt": item_found["trakt"],
                            "imdb": item_found["Imdb_id"],
                        },
                    }
                    validatedDuplicates.append(m)
    except Exception as e:
        logging.error(f"cannot open file {file}", e)

    return validatedDuplicates


def main():

    items = NetflixItems()
    items.load_csv(csvFile)

    api_auth(items)

    print("Found " + str(len(items.items)) + " items to import\n")

    items.search_items_create_request()

    if len(_duplicates["movies"]) > 0:
        print("\nFound duplicate movies check duplicates.json\n")

    if len(_duplicates["episodes"]) > 0:
        print("\nFound duplicate episodes check duplicates.json\n")

    validatedDuplicates = importValidatedDuplicates("duplicates.json")

    items.appendValidDuplicates(validatedDuplicates)

    print("\n--------------------Final Request--------------------\n")
    print(json.dumps(items._final_request))

    with open("duplicates.json", "w") as f:
        print(json.dumps(items._duplicates), file=f)

    with open("final.json", "w") as f:
        print(json.dumps(items._final_request), file=f)

    # invoke
    file = "final.json"
    try:
        f = open(
            file,
        )
        data = json.load(f)
        print(data)
        response = requests.post(items._baseurl + "/sync/history", data=json.dumps(_final_request), headers=items._headers)
        print(response)
    except:
        print(Exception)

    print("\n------------Exiting Program------------\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
