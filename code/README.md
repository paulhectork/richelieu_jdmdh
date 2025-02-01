#

---

## Installation et utilisation
```python
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python -m spacy download fr_dep_news_trf  # installer le dataset de NER
```

Ce dépôt utilise `python 3.8` qui n'est pas compatible avec la dernière version de Spacy. 
On utilise donc `spacy<=3.7`.
