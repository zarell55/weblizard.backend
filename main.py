from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from db import get_conn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zarell55.github.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            url,
            title,
            ts_headline(content, plainto_tsquery(%s)) AS snippet,
            pagerank
        FROM pages
        WHERE tsv @@ plainto_tsquery(%s)
        ORDER BY
            ts_rank(tsv, plainto_tsquery(%s)) * 0.7
            + pagerank * 0.3 DESC
        LIMIT 20;
    """, (q, q, q))

    results = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "url": r["url"],
            "title": r["title"],
            "snippet": r["snippet"],
            "pagerank": r["pagerank"],
        }
        for r in results
    ]
