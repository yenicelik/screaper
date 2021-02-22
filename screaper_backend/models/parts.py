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

    def parts(self):
        return self._parts

    def part_ids(self):
        return set(self._part_ids)

    def part_external_identifiers(self):
        return set(self._part_external_identifiers)


    #     # Run the individial DataImporters and aggregate a parts list
    #     data_importer_union_special = DataImporterUnionSpecial()
    #     self.data = data_importer_union_special.parts_list()
    #     self._searchstring = self.data['searchstring'].tolist()
    #     self._parts = self.data.to_dict("records")
    #     print(f"{len(self._parts)} parts collected")
    #
    # def id_to_dict(self, idx):
    #     out = self.data.iloc[idx].to_dict()
    #     out.update({"id": idx})
    #     return out
    #
    # def parts_list(self):
    #     return self._parts
    #
    # def searchstring_list(self):
    #     """
    #         Python List of Searchstrings for each part.
    #         For faster querying of tf-idf and other language models
    #     """
    #     return self._searchstring


model_parts = Parts()
