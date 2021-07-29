# Program to import whatched history into tratk from netflix

this is a work in progress.

- Export csv from netflix (netflix.com -> account -> {Profile} -> Viewing activity -> view -> Download all )
- remove first line in csv (headers)
- complete `SECRETS.env` with this values

```
TRATK_API_KEY={YOUR_TRATK_API_KEY}

#CLIENT SECRET
TRATK_API_SECRET={YOUR_TRATK_API_SECRET}

#CSV FILE EXPORTEF FROM NETFLIX
FILE=change_me/NetflixViewingHistory.csv

TOKEN=
```

run `SyncHistoryTracktv.py`