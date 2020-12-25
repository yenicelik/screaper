"""
    Any functions that are related to removing tags
"""


def remove_attributes(soup, whitelist, blacklist):
    white = True
    if white:
        print("Whitelisting attributes")
        for s in soup.find_all():
            print("Attributes are: ", s.attrs)
            del_attr = set()
            for attr in s.attrs:
                print("Attr is: ", attr)
                if attr not in whitelist:
                    print("Popping: ", attr)
                    del_attr.add(attr)
            for x in del_attr:
                s.attrs.pop(x)
    else:
        print("Deleting attributes")
        for s in soup.find_all():
            print("Attributes are: ", s.attrs)
            del_attr = set()
            for attr in s.attrs:
                print("Attr is: ", attr)
                if attr in blacklist:
                    print("Popping: ", attr)
                    del_attr.add(attr)
            for x in del_attr:
                s.attrs.pop(x)
