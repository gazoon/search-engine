from flask import Flask, request, render_template

from indexing import Crawler
from pymongo import MongoClient
from urllib.parse import urlparse
from urllib.request import urlopen
from bson.binary import Binary
import pickle
from searching import Searcher

app = Flask(__name__)
client = MongoClient('localhost', 27017)
DB = 'indices'
COLLECTION = 'indices'


@app.route('/search', methods=['POST'])
def search():
    url = request.form.get('url')
    if not url:
        return "Empty url"
    query = request.form.get('query')
    if not query:
        return "Empty query"
    domain = urlparse(url).netloc
    if not domain:
        return "Incorrect site domain"

    collection = client[DB][COLLECTION]
    doc = collection.find_one({'domain': domain})
    if not doc:
        return "Site not indexed yet"
    index_bytes = doc['index']
    try:
        index = pickle.loads(index_bytes)
    except pickle.UnpicklingError:
        return "Server error try later"
    s = Searcher(index, query)
    urls_list = s.search(with_scores=True)
    return render_template("results.html", urls_list=urls_list)


@app.route('/index', methods=['POST'])
def index_site():
    url = request.form.get('url')
    if not url:
        return "Empty url"
    domain = urlparse(url).netloc
    if not domain:
        return "Incorrect site domain"
    try:
        with urlopen(url) as f:
            f.read()
    except:
        return "Bad site url"
    collection = client[DB][COLLECTION]
    doc = collection.find_one({'domain': domain})
    if doc:
        return "Site already in index"
    c = Crawler(domain)
    c.crawl(url)
    index = c.get_index()
    index_bytes = pickle.dumps(index)
    doc = {
        'domain': domain,
        'index': Binary(index_bytes),
    }
    collection.insert_one(doc)
    return "Success"


@app.route('/')
def root():
    return render_template('root.html')


if __name__ == '__main__':
    app.run()
