"""
    Scrapes an example final company page from thomasnet
"""

# TODO: Implement some mechanism that checks how many failed requests per second,
# TODO: Remove all style tags
# and skips all items in the queue with that domainname

# implement selectiveness
# implement re-visit
# implement politeness
# implement parallelization

# implement website caching (request package?) https://pypi.org/project/requests-cache/

# look at robots.txt and ignore the ones that are not allowed

# link: remove # at the end

# sanitize html inputs before putting these into the postgres database: https://w3lib.readthedocs.io/en/latest/w3lib.html
# create an embedded state-representation that determines to look for further selection or not

# for now, include a certain type of whitelisting