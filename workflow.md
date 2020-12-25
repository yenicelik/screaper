## General Workflow

Our MVP will cover bearings. Thus, we will only focus on bearings as examples.
Our goal is to have the same principles as an Exchange, but with human design.
Bearings will be grown by the secular demand of urbanization and automation.

1. Identify seed pages: 
    - I.e. select a [website](https://www.thomasnet.com)
    - Identify multiple starting points reg. your topic of cohice, like a [product catalogue](https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/) or a [supplier catalogue](https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html)
    
2. Run Scraper:
    - Apply Breadth First Search until a good amount of websites were scraped 
    Look for obvious
    - Do some heuristic to prefer pages that include search terms of some quantity
    - Do this until a sensible amount of web-pages is indexed   
    
3. Extract companies and products:
    - Using the raw-html, extract companies and products using NER. 
    - Dump the found referrer_url, found string, position in html, NER type into a postgres table (this is a minimal example).
    - Apply clustering algorithm to find a representative centroid for each of these items.
    
TODOs:

- Implement priority queue based on text contents (i.e. contains bearing)
