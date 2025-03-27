"""
attempt at automated classification of the named entity and themes
"""
import pandas as pd
import spacy

from common import Query, ENGINE


query = Query( "SELECT named_entity.id, named_entity.entry_name, named_entity.category FROM named_entity"
             , "named_entity_classification"
             , "named_entity" )

def pipeline():
    query.df = pd.read_sql(query.sql, ENGINE)

    # before, you must run in cli : python -m spacy download fr_core_news_sm
    # smh the big model doesn't work...
    # nlp = spacy.load("fr_dep_news_trf")  # https://spacy.io/models/fr/#fr_dep_news_trf
    nlp = spacy.load("fr_core_news_sm")

    query.df["doc"] = query.df.entry_name.apply(lambda x: nlp(x))
    print(query.df.doc)
    query.df["ents"] = query.df.doc.apply(lambda x: [ (ent.text, ent.label_) for ent in x.ents ])
    print(query.df[["entry_name", "ents"]])

    print(query.df.loc[ query.df.ents.apply(len).gt(1) ])
    print(query.df.ents.apply(lambda x: [ ent[1] for ent in x ]))
    # print(query.df[["entry_name", "doc"]])
    # for doc in nlp.pipe(query.df.entry_name.to_list()):
    #     print([(ent) for ent in doc.ents])
    # for doc in nlp.pipe(query.df.entry_name, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
    #     print([ (ent.text, ent.label_) for ent in doc.ents ])
    # for ent in nlp("Banque de France").ents:
    #     print(ent.text, ent.start_char, ent.end_char, ent.label_)


if __name__ == "__main__":
    pipeline()