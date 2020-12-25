"""
    Entity Extraction
"""

def extract_entities(soup, model_ner):

    for x in soup():

        if x.string is None:
            continue

        query = x.string.split(".")
        query = [x for x in query if x]
        if not query:
            continue

        sentences, named_entities = model_ner.predict(query=query)

        # -> TODO: This is going to be very lossy!!!
        # -> But this is fine
        # TODO: Also keep if a link is nearby

        # Check if all are Os
        if all([x == "O" for named_entity in named_entities for x in named_entity]):
            print("Should delete this string: ")
            print(x.string)
            # Do not look further
            # Do not delete if external link:
            if not ("www." or ".com" in x.string):
                x.string = ""
            continue

        out = []

        # iterate over each sentence
        for sentence, named_entity in zip(sentences, named_entities):

            # Extract the named entities, and add them as an attribute
            if all([x == "O" for x in named_entity]):
                # Replace the string with an empty string
                # We still keep the string, as this may be useful for contextual word embeddings
                continue

            # TODO: Add named entities as an attribute
            # Can process this later?
            # Maybe also add to the database as a named entity
            # Or add it at a later stage?
            # TODO: Continue here
            # Will this be fast enough? I think not... :/
            # Perhaps use Google instead. But that's gonna be expensive
            # Merge multiple entities, and create a list of such entities.
            # You can then save such named entities
            a = 0
            b = 0
            start = False
            finish = False
            # Account for the case: ['B-ORG', 'I-ORG'] 0
            # TODO: I forgot the fact that there could be multiple entities!!!
            for i in range(len(named_entity)):

                # TODO: Write some unittests for this portion

                # Identify Named Entity
                if "B-" in named_entity[i]:
                    print("Found named entity: ", named_entity, sentence, i)

                    # Skip if not a useful entity?
                    if named_entity[i] in ("B-LAW", "B-PERCENT", "B-ORDINAL"):
                        continue

                    start = True
                    finish = False
                    a = i

                # Finish Named Entity
                elif "I-" in named_entity[i]:
                    print("Continue named entity: ", named_entity, i)

                elif start and "O" == named_entity[i]:
                    print("Partial named entity: ", named_entity, i)
                    b = i
                    start = False
                    finish = True

                elif start and i == len(named_entity) - 1:
                    # Reached the end of the named entity list
                    print("Full named entity: ", named_entity, i)
                    b = None  # i
                    start = False
                    finish = True

                elif start and "B-" in named_entity[ i +1]:
                    # above case rules out that i+1 >= len(named_entity)
                    print("Continue named entity: ", named_entity, i)
                    b = i + 1
                    start = False
                    finish = True

                if (not start) and finish:
                    entity_pair = (" ".join(sentence[a:b]), " ".join(named_entity[a:b]))
                    print("Appending entity pair: ", entity_pair, a, b)
                    out.append(entity_pair)
                    start = False
                    finish = False

        if out:
            print("Appending entity pair: ", out)
            x.attrs["ner"] = str(out)

    # TODO: Remove unnecessary nodes and unwrap even further
    # Perhaps just be aggressive and see how it works
    for x in reversed(soup()):
        # print("At tag: ", x, x.string, x.attrs, x.findChildren(recursive=False))
        if not x.string and not x.attrs and len(x.findChildren(recursive=False)) <= 1:
            # print("Unwrapping!")
            x.unwrap()
