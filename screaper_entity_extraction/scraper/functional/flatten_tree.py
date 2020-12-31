"""
    Anything that
"""
import re

def remove_empty_nodes(soup):
    """
        CURRENTLY NOT USED!!!
    :param soup:
    :return:
    """
    remove_redundant = True
    if remove_redundant:
        # Iterate each line
        for x in soup.find_all():

            # fetching text from tag and remove whitespaces
            # Empty attributes!
            # print("x is: ", x.get_text().replace("\n", " ").strip())
            # print("x is: ", len(x.get_text().replace("\n", " ").strip()))

            # Also check if there's any children (unless we do in-order node traversal
            # Actually, this should be correct, bcs get text gets the text collectively

            # TODO: But then we must check if any child nodes have any attributes!!
            # We can

            # TODO: Does this include text for all childs as well?
            if len(x.get_text().replace("\n", " ").strip()) == 0:
                if x.attrs is None:
                    print("Deleting: ", x, x.get_text, x.attrs)
                    x.decompose()
                elif len(x.attrs) == 0:
                    # Remove empty tag
                    print("Deleting: ", x, x.get_text, x.attrs)
                    x.decompose()

            print("x attrs: ", x.attrs)

            if x.attrs is not None:
                print("x attrs: ", len(x.attrs))


def unwrap_span(soup):
    # Unwrap all style tags
    for x in soup.find_all("span"):
        x.unwrap()

    # TODO: Add unittests

    # Replace all redundant newlines and whitespaces with a single newline or whitespace
    for x in soup():

        if x.string:
            bfr = x.string
            x.string = x.string.replace("\n", " ")
            x.string = re.sub(' +', ' ', x.string).strip()
            print("{} x string is: (befor)".format("-->" if bfr != x.string else ""), bfr)
            print("{} x string is: (after)".format("-->" if bfr != x.string else ""), x.string)

            if len(x.string) <= 2:
                # Also remove all strings that have less than 2 characters
                # We can consider this as noise
                x.string = ""

    # If no other attributes are present,
    # then add the attributes here
    for x in reversed(soup()):
        # print("At tag: ", x, x.string, x.attrs, x.findChildren(recursive=False))
        if not x.string and not x.attrs and len(x.findChildren(recursive=False)) <= 1:
            # print("Unwrapping!")
            x.unwrap()

        # Remove all tags that can be merged

    # TODO: Need to fix encoding issues
    # Designer and fabricator of medical devices, including ventilators for use during the COVID-19 crisis. Selected by NASAâs Jet Propulsion Lab (JPL) to manufacture a new ventilator designed specially for COVID-19 response. Also manufactures other devices, implantables and software products. ISO 13485 Certified.
    # Weâve curated a list of mission-critical resources &	 real-time information for manufacturers &	 distributors.
