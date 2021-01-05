### Install mongodb

On mac:

```
brew tap | grep mongodb
brew install mongodb-community@4.4
brew services start mongodb-community@4.4
brew services stop mongodb-community@4.4
mongo
```


### Spawn a database

Spawn one database for the storage,
and one database for the queue of which websites were already crawled


### Create postgres database


```
createdb scraper
```

### Useful links

[Scraping Tools](https://towardsdatascience.com/5-strategies-to-write-unblock-able-web-scrapers-in-python-5e40c147bdaf)
