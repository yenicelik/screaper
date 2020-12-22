# screaper
Don't fear the scReaper

### Further installation steps

Pre-requisite:

```
python -m deeppavlov install ner_ontonotes_bert_mult
```

### Ideas

- Treat this as an ontology learning problem

- Create a database of all documents, then you can apply tf-idf for document similarity
- Create a database of all edges between entities, entitiy-classifications and entity-link. You can then apply supervised learning (e.g. graph neural networks) to infer structure on such websites. You would need to a manually crafted website for this.
- Each node can have PoS, NER information, and any other NLP information
- Only if a node occurs multiple times, and is classified as a specific NER, use it as a NER. 
- Only use text of certain length to classify as an entity.
- Save all extracted entities into a database, and then do big data operations on this (do a script-first implementation) 
- On this edge-set apply matrix factorization techniques to induce hidden relations