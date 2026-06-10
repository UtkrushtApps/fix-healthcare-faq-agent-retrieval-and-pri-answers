import json
import re

from app.config import KB_PATH, MAX_CONTEXT_ARTICLES


STOPWORDS = {
    'a',
    'an',
    'and',
    'are',
    'at',
    'by',
    'can',
    'do',
    'for',
    'from',
    'how',
    'i',
    'if',
    'in',
    'is',
    'it',
    'my',
    'of',
    'on',
    'or',
    'the',
    'to',
    'we',
    'what',
    'when',
    'where',
    'with',
    'you',
    'your',
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r'[a-z0-9]+', text.lower())
    return {word for word in words if len(word) > 2 and word not in STOPWORDS}


def build_context(query: str) -> dict | None:
    with open(KB_PATH, encoding='utf-8') as f:
        articles = json.load(f)['articles']

    query_terms = _tokenize(query)
    if not query_terms:
        return None

    ranked_matches: list[tuple[int, int, dict]] = []

    for index, article in enumerate(articles):
        if article.get('visibility') != 'public':
            continue

        searchable_text = f"{article.get('title', '')} {article.get('body', '')}"
        article_terms = _tokenize(searchable_text)
        overlap = query_terms & article_terms

        if not overlap:
            continue

        ranked_matches.append((len(overlap), index, article))

    if not ranked_matches:
        return None

    ranked_matches.sort(key=lambda item: (-item[0], item[1]))
    top_articles = [article for _, _, article in ranked_matches[:MAX_CONTEXT_ARTICLES]]

    snippets = [
        f"[{article['source_id']}] {article['title']}\n{article['body']}"
        for article in top_articles
    ]
    source_ids = [article['source_id'] for article in top_articles]

    return {
        'context': '\n\n'.join(snippets),
        'source_ids': source_ids,
    }
