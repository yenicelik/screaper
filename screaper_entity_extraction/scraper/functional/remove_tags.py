"""
    Any functions that are related to removing tags
"""


def remove_tag(soup, tag_name):
    for x in soup.find_all(tag_name):
        x.decompose()


def remove_tags(soup):
    # These tags should not be removed per-se, but just unwrapped.
    # The underlying items should be pushed up,
    # the tags should be replaced by "divs", so to speak
    # Pose this as an optimization problem if we label end-to-end
    tags = [
        "script",
        "style",
        "svg",
        "link",
        "br"
        # "noscript",
        # "footer",
        # "form",
        # "button",
        # "input"  # This one is needed!
        # "class",
        # slightly optional
        # "select",
        # "header"
    ]
    for x in soup.find_all(tags):
        x.decompose()
