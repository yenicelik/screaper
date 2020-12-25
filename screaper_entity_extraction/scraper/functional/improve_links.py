"""
    Improve
"""
from tldextract import tldextract


def improve_links(soup, base_url):
    for link in soup.find_all('a'):

        if 'href' not in link.attrs:
            # What to do in this case?
            continue

        url = link.attrs['href'].strip()

        if url is None:
            # TODO: Log a warning that some url is none!
            # Pop the href attribute
            # TODO: Remove link if not existent
            link.attrs.pop('href')
            continue
        # apply whitelisting
        if url == "":
            # if link is empty, it is probably broken, skip
            link.attrs.pop('href')
            continue
        if url[0] == "#":
            # if link starts with "#", skip this (because this is just an anchor
            # I'm going to be aggressive here
            link.attrs.pop('href')
            continue
        if len(url) >= 10 and url[:10] == "javascript":
            # pop the url
            print("Detected javascript!", url)
            link.attrs.pop('href')
            continue
        if url[:6] == "tel://":
            # Maybe don't skip, but find phone-number from this ...?
            print("Detected tel, skipping!", url)
            link.attrs.pop('href')
            continue

        if url[0] == "/":
            # if link starts with slash, then this is a relative link. We append the domain to the url
            if not base_url.subdomain:
                url = "http://{}.{}".format(base_url.domain, base_url.suffix) + url
                link.attrs['href'] = url
            else:
                url = "http://{}.{}.{}".format(base_url.subdomain, base_url.domain, base_url.suffix) + url
                link.attrs['href'] = url
            # TODO: Does this destroy the inner contents???
        elif url[:4] != "http" and ":" not in url:
            print("Detected no http!", url)
            if not base_url.subdomain:
                url = "http://{}.{}".format(base_url.domain, base_url.suffix) + "/" + url
                link.attrs['href'] = url
            else:
                url = "http://{}.{}.{}".format(base_url.subdomain, base_url.domain,
                                               base_url.suffix) + "/" + url  # else:
                link.attrs['href'] = url

                # Mark the link as an external link:
        print("External url?", tldextract.extract(url).domain != base_url.domain,
              tldextract.extract(url).domain, base_url.domain, type(tldextract.extract(url).domain),
              type(base_url.domain))
        if tldextract.extract(url).domain != base_url.domain:
            link.attrs["external_link"] = "True"
        else:
            link.attrs["external_link"] = "False"
