### Order of starting the distributed frontera application

```
python -m frontera.contrib.messagebus.zeromq.broker
```

Must use kafka-python==1.4.4. 
Change directory to inside frontera/examples/general-spider.

Add the different seed urls.

```
python -m frontera.utils.add_seeds --config config.dbw --seeds-file seeds_es_smp.txt
```

Start the strategy worker, which scores links, descides order or crawling, and decides when to stop crawling.

```
python -m frontera.worker.strategy --config config.sw
```

Now start the scrapy spider

``` 
python -m scrapy crawl general
```

Now start the database

```
python -m frontera.worker.db --no-incoming --config config.dbw --partitions 0
```