from screaper_backend.importer.data_importer_unionspecial import DataImporterUnionSpecial


class PartsList:

    def __init__(self):
        # Run the individial DataImporters and aggregate a parts list
        data_importer_union_special = DataImporterUnionSpecial()
        self.data = data_importer_union_special.parts_list()
        self._searchstring = self.data['searchstring'].tolist()
        self._parts = self.data.to_dict("records")
        print(f"{len(self._parts)} parts collected")

    def id_to_dict(self, idx):
        out = self.data.iloc[idx].to_dict()
        return out

    def parts_list(self):
        return self._parts

    def searchstring_list(self):
        """
            Python List of Searchstrings for each part.
            For faster querying of tf-idf and other language models
        """
        return self._searchstring

if __name__ == "__main__":
    print("Curate partslist")
    partslist = PartsList()
    print("Selecting the fifth part")
    print(partslist.id_to_dict(5))
