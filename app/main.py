"""HTTP API and minimal browser UI for the retrieval + answer stack.

This module wires the pieces together and exposes three endpoints used by
the browser UI and basic health checks:
- `GET /` serves the static chat UI
- `GET /health` returns basic corpus load stats
- `POST /chat` accepts a `ChatRequest` and returns a `ChatResponse`

Keep the API surface intentionally small so it's easy to test and mock in
integration tests.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .answering import AnswerEngine
from .corpus import CorpusLoader
from .hybrid_retriever import HybridRetriever
from .query_router import route_question
from .schemas import ChatRequest, ChatResponse
from .settings import load_settings


settings = load_settings()
app = FastAPI(title=settings.app_title)

# Templates and static assets (small single-page UI for manual testing)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")

# Initialize and keep in-memory indexes on startup; this is deliberate for
# simplicity. For very large corpora replace this with lazy or incremental
# indexing strategies.
corpus_loader = CorpusLoader(settings.data_dir)
corpus = corpus_loader.load()
retriever = HybridRetriever(
    corpus,
    min_final_score=settings.similarity_threshold,
)
answer_engine = AnswerEngine(settings)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_title": settings.app_title,
            "openai_model": settings.openai_model,
            "sample_questions": [
                "What was the fund's commentary on valuations in Q1 2025?",
                "How did the manager describe the use of the subscription credit facility across 2024?",
                "Has the fund's strategy shifted between 2022 and 2025?",
            ],
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "documents": len(corpus.documents), "chunks": len(corpus.chunks)}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    route = route_question(payload.question)
    if route.route != "finance":
        return ChatResponse(
            answer=route.answer or "I couldn't find relevant information in the corpus.",
            sources=[],
            out_of_scope=True,
            provider=f"router:{route.route}",
        )

    sources = retriever.search(payload.question, top_k=settings.top_k, max_sources=settings.max_sources)
    if not sources:
        return ChatResponse(
            answer="I couldn't find relevant information in the corpus for that question.",
            sources=[],
            out_of_scope=True,
            provider="none",
        )
    answer, provider = answer_engine.answer(payload.question, sources)
    out_of_scope = not sources or answer_engine.is_out_of_scope(answer)
    if out_of_scope:
        answer = "I couldn't find relevant information in the corpus for that question."
    return ChatResponse(answer=answer, sources=sources, out_of_scope=out_of_scope, provider=provider)
