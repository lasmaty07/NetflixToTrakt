# Program to import watched history into Trakt from Netflix

This is a work in progress.

- Export csv from Netflix (Netflix.com -> Account -> {Profile} -> Viewing activity -> View -> Download all )
- Remove first line in csv (headers)
- Complete `SECRETS.env` with this value

```
TRAKT_API_KEY={YOUR_TRAKT_API_KEY}

#CLIENT SECRET
TRAKT_API_SECRET={YOUR_TRAKT_API_SECRET}

#CSV FILE EXPORTED FROM NETFLIX
FILE=change_me/NetflixViewingHistory.csv

TOKEN=
```

run `SyncHistoryTracktv.py`
