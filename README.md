# screaper
Don't fear the scReaper

## Who buys what from Whom?

### Iteration One

Niche market focus: Bearings

### Who?

We identify the list of companies active in this field.

### Buys what?

We will identify the list of products associated with each seller.

### From whom?

We will apply relation extraction, 
as well as design the platform to ask people where they sell, 
to make similar recommendations.

### Further installation steps

Pre-requisite:

```
python -m deeppavlov install ner_ontonotes_bert_mult
```

### Resources:

- Record all contacts and companies that could be useful on [HubSpot](https://app.hubspot.com/contacts/8785787/contacts/list/view/all/)
- Record all TODOs on this [Google Sheet](https://docs.google.com/spreadsheets/d/1li-v-0ilx5eAwvKL_c9rq0KBxRftTe_ss5y03LgVPT8/edit#gid=0)



### Ideas

- Treat this as an ontology learning problem

- Create a database of all documents, then you can apply tf-idf for document similarity
- Create a database of all edges between entities, entitiy-classifications and entity-link. You can then apply supervised learning (e.g. graph neural networks) to infer structure on such websites. You would need to a manually crafted website for this.
- Each node can have PoS, NER information, and any other NLP information
- Only if a node occurs multiple times, and is classified as a specific NER, use it as a NER. 
- Only use text of certain length to classify as an entity.
- Save all extracted entities into a database, and then do big data operations on this (do a script-first implementation) 
- On this edge-set apply matrix factorization techniques to induce hidden relations


### Incredibly good talk

- https://www.youtube.com/watch?v=vf0t2R0FZ5M 
- index all websites around key entities (organizations, brands, products)
- -> how to determine a key entity
- entities, attributes, relationships, trends, events, bare analytics, predictions over time, connect them
- 1.3T documents, 4-5 biggest elasticsearch cluster
- recommender engines, semantic searchers, contextual searchers, inference engines
- closed domains around companies and related entities
- knowledge graph embedding
- base-url as entitiy (?) (bcs organization).
- then do entity-label-matching (title of html)
- rule-based feature engineering
- 2.5k features per website
- predictor on what sites to prioritize by the terms included in the data
- 

- NLP tasks:
    - language detection
    - text similarity
    - text classification
    - POS
    - Noun Chunking
    - Dependency Parsing
    - Named Entity Recognition
    - Named Entity Disambiguation
    - Key Phrases
    - Concept Extraction ->
    - Sentiment Analysis
    - Relation Extraction
    - Summarization
    
    - NER: CRF models, another one BERT models

- populate knowledge graph with links from web
- DBPedia Schema
- AGDISTIS NED
- apache lucene triplet store

- ontology of 100s of tasks
    - based on semantic rules on NLP tasks
    
- topic classifier
- record linking 

- schema mapping, normalization, blocking, pairwise similarity classification, agglorometive clustering, cluster UUID assignment
- truth discovery with majority voting

- human validation of feedback loop

- check out later: https://www.youtube.com/watch?v=UGPT64wo7lU 

-> start scraping the website already? (on bob)
    
- 700M documents per day ; 120 articles/s 


#### Quick Start

Install all dependencies

- `pip install -r kubernetes/scraper_language_model/requirements.txt `
- `sudo apt-get install python3 python-dev python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip`
- `pip install --upgrade pip`
- `pip install deeppavlov`
- `python -m deeppavlov install ner_ontonotes_bert_mult`
- `python -c "from deeppavlov import configs, build_model; build_model(configs.ner.ner_ontonotes_bert_mult, download=True)"`

Install PostgreSQL and create database

- `sudo apt update`
- `sudo apt install postgresql postgresql-contrib`
- `sudo -i -u postgres`
- `CREATE DATABASE screaper;`

Instantiate the tables

- `python -m screaper.resources.entities`


#### Graph Neural Networks

- https://towardsdatascience.com/overview-of-deep-learning-on-graph-embeddings-4305c10ad4a4

-> Perhaps do not include any scripts that are not company pages, or just be more careful which pages to scrape, and which ones to just skip


#### Run with higher priority

``` 
nice -n 17 python -m screaper.core.main
nice -n 17 python -m screaper.engine.core.

```