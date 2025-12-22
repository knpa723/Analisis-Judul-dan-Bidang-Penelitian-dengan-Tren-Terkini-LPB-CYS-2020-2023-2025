from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS_ID = [
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan",
    "pada", "oleh", "dalam", "sebagai", "terhadap",
    "penelitian", "studi", "analisis", "pengaruh",
    "berbasis", "melalui", "menggunakan", "of", "the"
]

def extract_keywords(texts, top_n=10):
    tfidf = TfidfVectorizer(
        stop_words=STOPWORDS_ID,
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=2
    )

    X = tfidf.fit_transform(texts)
    scores = X.sum(axis=0).A1
    keywords = tfidf.get_feature_names_out()

    result = sorted(
        zip(keywords, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return result[:top_n]
