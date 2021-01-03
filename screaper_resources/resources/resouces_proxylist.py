"""
    Implements the proxy-list resources
"""
import json
from urllib.request import urlopen

# TODO: Download a fuller list

# Use this instead? https://github.com/constverum/ProxyBroker Supports async
# Version 2? https://github.com/bluet/proxybroker2
# Or this: https://github.com/iw4p/proxy-scraper
# Or this: https://github.com/OceanFireSoftware/python-simple-proxy
# Or this: https://github.com/esec-exploits/bruteproxy.py
# Or this: https://github.com/SkuzzyxD/ProxyGrab
# Or this: https://github.com/bashkirtsevich-llc/PyProxyList
# Or this: https://github.com/machinia/fake-proxy

class ProxyList:

    # TODO: Re-create this object every couple times
    # I can do this by re-starting processes every now and then
    def __init__(self):

        json_url = "https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json"
        # Add more proxy-lists
        with urlopen(json_url) as url:
            proxies = json.loads(url.read().decode('utf-8'))
        proxies = proxies['proxies']
        # How many proxies in first
        print("Proxies are: ", len(proxies))

        # # TODO: Pop from list once the proxy proves itself to be bad
        # scrapper = Scrapper(category='ALL', print_err_trace=False)
        # print("Scrapper is: ", scrapper.getProxies())
        # exit(0)

        # TODO: Replace with environment variable
        proxies = [(x["ip"], x["port"]) for x in proxies if x["google_status"] == 200]
        self._proxies = set(("http://" + str(x[0]) + ":" + str(x[1])) for x in proxies)
        self._bad_proxy_counter = dict((x, 0) for x in self._proxies)

        self._proxies_blacklist = set()

        self.max_retries_per_proxy = 10
        self.total_tries = 0
        self.total_bad_tries = 0
        
    @property
    def proxies(self):
        self.total_tries += 1
        return list(self._proxies.difference(self._proxies_blacklist))

    def warn_proxy(self, proxy, harsh=False):
        """
            Adds a counter that a proxy is not very stable.
            If the harsh parameter is raised, will immediately delete this proxy
                (this is usefule with ClientHttpProxyError s for example)
        :param proxy:
        :param harsh:
        :return:
        """
        if harsh:
            self._proxies_blacklist.add(proxy)

        self._bad_proxy_counter[proxy] += 1
        self.total_bad_tries += 1
        # Remove proxy if it repeatedly turns out to be a bad one
        if self._bad_proxy_counter[proxy] > self.max_retries_per_proxy and \
                ((self._bad_proxy_counter[proxy] / self.total_bad_tries) > 0.01) and \
                (self.total_bad_tries / self.total_tries > 0.01):
            # TODO: Devise this rule
            self._proxies_blacklist.add(proxy)
            # del self._bad_proxy_counter[proxy]
        if len(self._proxies) < 10:
            raise Exception("Less than 5 proxies left!!!", self._proxies, self._bad_proxy_counter)


if __name__ == "__main__":
    print("Scrapper is: ")
    proxy_list = ProxyList()
    print()
