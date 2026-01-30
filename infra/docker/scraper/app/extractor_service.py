# extractor_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import re
from newspaper import Article
import asyncio

app = FastAPI(title="Extractor (newspaper3k)")


class ExtractIn(BaseModel):
    urls: List[str] = Field(..., description="Listado de URLs a procesar")
    lang: Optional[str] = Field("es", description="Idioma preferido para newspaper")
    concurrency: Optional[int] = Field(6, description="Máximo de descargas concurrentes")


class ArticleResult(BaseModel):
    url: str
    titulo: str
    texto: str
    error: Optional[str] = None


class ExtractOut(BaseModel):
    ok: bool
    results: List[ArticleResult]

# === core igual al de Plan Democracia ===

JS_CONCAT_RE = re.compile(r"""(?:
    ['"]\s*\+\s*\n      # ' +\n  o  " +\n
  | `\s*\+\s*\n         # backtick +\n
)""", re.VERBOSE)

def sanitize_js_artifacts(text: str, max_chars: int = 20000) -> str:
    if not text:
        return ""
    t = text

    # 1) un-pegar concatenaciones tipo "' +\n", '" +\n', "` +\n"
    t = JS_CONCAT_RE.sub("\n", t)

    # 2) escapar visibles -> reales
    t = t.replace("\\n", "\n").replace("\\t", " ")

    # 3) normalizaciones generales
    t = (t
         .replace("’", "'").replace("“", '"').replace("”", '"')
         .replace("\r", "")
    )
    # quitar refs [12] de Wikipedia
    t = re.sub(r"$begin:math:display$\\d+$end:math:display$", "", t)
    # líneas basura muy cortas o con demasiados símbolos (tipo CSS/JS)
    lines = [ln.strip() for ln in t.splitlines()]
    clean_lines = []
    for ln in lines:
        if not ln:      # vacías se filtrarán más abajo con saltos
            clean_lines.append("")
            continue
        sym_ratio = (len(re.findall(r"[{};=#<>]", ln)) / max(len(ln), 1))
        if sym_ratio > 0.08:
            continue
        clean_lines.append(ln)

    t = "\n".join(clean_lines)
    # colapsar espacios y saltos
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()

    if max_chars and len(t) > max_chars:
        t = t[:max_chars - 1].rstrip() + "…"
    return t

def extraer_contenido(url: str, lang: str = "es") -> ArticleResult:
    try:
        art = Article(url, language=lang)
        art.download()
        art.parse()

        titulo = art.title or ""
        texto = sanitize_js_artifacts(art.text or "")
        return ArticleResult(url=url, titulo=titulo, texto=texto)
    except Exception as e:
        return ArticleResult(url=url, titulo="", texto="", error=str(e))


@app.post("/extract", response_model=ExtractOut)
async def extract(payload: ExtractIn):
    if not payload.urls:
        raise HTTPException(400, "Debes enviar { urls: [...] }")

    desired_concurrency = payload.concurrency or 6
    sem = asyncio.Semaphore(max(1, min(desired_concurrency, 20)))
    results: List[Optional[ArticleResult]] = [None] * len(payload.urls)

    async def worker(i: int, u: str):
        async with sem:
            # newspaper es sync, lo corremos en thread pool
            results[i] = await asyncio.to_thread(extraer_contenido, u, payload.lang or "es")

    await asyncio.gather(*[worker(i, u) for i, u in enumerate(payload.urls)])
    return ExtractOut(ok=True, results=[r for r in results if r is not None])
