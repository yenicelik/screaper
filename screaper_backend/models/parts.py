"""
    Get orders for a certain user
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Parts:

    def __init__(self):
        self._parts = screaper_database.read_parts()
        print(f"{len(self._parts)} parts collected")
        self._part_ids = [x["id"] for x in self._parts]
        self._part_external_identifiers = [x["part_external_identifier"] for x in self._parts]
        self._searchstring = [x["searchstring"] for x in self._parts]

    def parts(self):
        return self._parts

    def part_ids(self):
        return set(self._part_ids)

    def part_external_identifiers(self):
        return set(self._part_external_identifiers)

    def id_to_dict(self, idx):
        translated_idx = self._part_ids[idx]
        # TODO: This seems to be corrupt?
        out = screaper_database.read_part_by_part_id_obj(translated_idx).to_dict()
        return out

    def searchstring_list(self):
        """
            Python List of Searchstrings for each part.
            For faster querying of tf-idf and other language models
        """
        return self._searchstring

model_parts = Parts()
