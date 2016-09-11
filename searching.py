import re
from collections import defaultdict

import sys


def normalized_scores(scores, small_is_better=False):
    zero = 0.000001
    if small_is_better:
        min_score = min(scores.values())
        return {u: float(min_score) / max(zero, v) for u, v in scores.items()}
    else:
        max_score = max(scores.values())
        max_score = max_score if max_score != 0 else zero
        return {u: float(v) / max_score for u, v in scores.items()}


def frequency_score(urls):
    scores = defaultdict(int)
    for url, positions in urls:
        scores[url] += len(positions)
    return normalized_scores(scores)


def unique_word_score(urls):
    scores = defaultdict(int)
    for url, positions in urls:
        scores[url] += 1
    return normalized_scores(scores)


def location_score(urls):
    scores = defaultdict(lambda: sys.maxsize)
    for url, positions in urls:
        scores[url] = min(scores[url], positions[0])
    return normalized_scores(scores, small_is_better=True)


def get_scored_urls(urls):
    total_scores = defaultdict(float)
    weights = [
        (1.0, frequency_score(urls)),
        (1.0, unique_word_score(urls)),
        (0.25, location_score(urls)),
    ]
    for weight, scores in weights:
        for url in scores:
            total_scores[url] += weight * scores[url]
    total_scores = {k: round(v, 1) for k, v in total_scores.items()}
    return list(total_scores.items())


class Searcher(object):
    def __init__(self, index, query):
        self.index = index
        self.words = re.findall(r'[\w-]+', query)

    def get_matched_urls(self):
        all_urls = []
        for word in self.words:
            word_dict = self.index.get(word, dict())
            for url in word_dict:
                all_urls.append((url, word_dict[url]))
        return all_urls

    def search(self, with_scores=False):
        urls = self.get_matched_urls()
        if not urls:
            return urls
        scored_urls = get_scored_urls(urls)
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        if with_scores:
            return scored_urls
        return [url for url, _ in scored_urls]
