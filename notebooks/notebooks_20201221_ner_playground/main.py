from deeppavlov import configs, build_model

# Organization has pretty bad accuracy

if __name__ == "__main__":
    print("Testing multilingual DeepPavlov NER model")
    ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=False)

    query = ner_model(['Bob Ross lived in Florida'])
    print("Query is: ", query)
