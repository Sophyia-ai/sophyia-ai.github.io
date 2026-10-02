#!/usr/bin/env python3
"""
blog_engine.py — blog statique pour sophyia.io (EN), focus IA & dev, à l'image du site.
Réécrit des articles depuis des flux IA/dev (Azure OpenAI gpt-4o-mini, voix Sophyia) → contenu
UNIQUE (pas de duplicate avec d'autres sites). Source citée + lien. Article JSON-LD.

Produit : blog/index.html (hub + filtres) + blog/<slug>.html
Env     : AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
Usage   : python3 automation/blog_engine.py --max 3 [--category ai]
"""
import os, sys, re, json, html as _html, ssl, urllib.request, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from faq_engine import BASE, FONTS, FAVICON, esc  # chrome commun

ROOT = HERE.parent
BLOG = ROOT / "blog"
DATA = HERE / "blog_data.json"
DEPLOYMENT = "gpt-4o-mini"
API_VERSION = "2024-12-01-preview"

CATEGORIES = {
    "ai":          {"label": "AI & Research",      "accent": "#6366f1"},
    "multi-agent": {"label": "Multi-Agent AI",     "accent": "#a855f7"},
    "dev":         {"label": "AI for Developers",  "accent": "#06b6d4"},
}

# Flux IA/dev. La catégorie réelle de chaque article est DÉTECTÉE au contenu
# (orchestration/agents → multi-agent), pas figée par le flux.
ALL_FEEDS = [
    "https://huggingface.co/blog/feed.xml",      # agents, orchestration, open-source IA
    "https://research.google/blog/rss/",          # recherche IA Google
    "https://www.technologyreview.com/feed/",     # MIT Tech Review (IA + tech)
]

# Termes qui signalent le cœur de Sophyia : l'orchestration d'IA / les systèmes multi-agents.
_ORCH = ("orchestrat", "multi-agent", "multi agent", "agentic", " agent", "agent ", "agents",
         "autonomous", "ai agent", "agent workflow", "langchain", "langgraph", "autogen",
         "crewai", "llamaindex", "tool use", "tool-calling", "agent system", "swarm",
         "copilot", "reasoning agent")
_DEVKW = ("developer", "sdk", "api", "open source", "open-source", "coding", "fine-tun",
          "training infra", "framework", "library", "deployment", "inference engine")

def detect_category(title, content):
    t = (str(title) + " " + str(content or "")).lower()
    if any(k in t for k in _ORCH): return "multi-agent"
    if any(k in t for k in _DEVKW): return "dev"
    return "ai"

PROMPT = """You write for the Sophyia blog. Sophyia is a Swiss company building an intelligence
orchestration platform — multi-agent AI that reasons, debates and adjudicates before answering
("beyond the single model"). Audience: technical and business readers interested in AI and
software development.

RULES (accuracy first):
1. Rewrite COMPLETELY in your own words — never copy the source. Stay FAITHFUL to the facts;
   invent nothing (no figures/dates/names not in the source).
2. Analytical, forward-looking tone; clear, no fluff, no marketing clichés.
3. Where natural, connect to the Sophyia angle (multi-agent reasoning, orchestration, reliability,
   auditability) — but stay informative, not promotional.
4. Structure with ## subheadings. 700-1100 words. No emojis.
5. End the body with a "## Source" heading followed by the link: {source}
Return ONLY valid JSON (no text/markdown around it) with EXACTLY these keys:
{{"title":"...","excerpt":"...","content":"...","tags":["t1","t2","t3"],"meta":"(<=160 chars)","read_time":"5 min"}}

ARTICLE TO REWRITE:
Title: {title}
Source: {source}
Content:
{content}
"""

def _ctx():
    try:
        import certifi; return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()

def slugify(t):
    t = re.sub(r"[^\w\s-]", "", (t or "").lower()).strip()
    return re.sub(r"[\s_]+", "-", t)[:80].strip("-") or "article"

def scrape(url, n=3):
    try:
        import feedparser
    except Exception:
        os.system(f"{sys.executable} -m pip install -q feedparser >/dev/null 2>&1"); import feedparser
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=40, context=_ctx()).read()
    except Exception as e:
        print(f"  [WARN] {url}: {e}"); return []
    d = feedparser.parse(raw)
    out = []
    for e in d.entries[:n]:
        body = ""
        if e.get("content"): body = e["content"][0].get("value", "")
        body = body or e.get("summary", "") or e.get("description", "")
        body = re.sub(r"<[^>]+>", " ", body)
        out.append({"title": e.get("title", ""), "link": e.get("link", ""), "content": body})
    return out

_AI_KEEP = ("ai ", "a.i", "artificial intelligence", "llm", "gpt", "machine learning", " ml ",
    "neural", "deep learning", "generative", "diffusion", "transformer", "inference", "model",
    "agent", "multi-agent", "dataset", "training", "fine-tun", "rag", "embedding", "chatbot",
    "open source", "hugging face", "developer", "software", "coding", "code", "api", "algorithm",
    "openai", "anthropic", "gemini", "benchmark", "reasoning", "automation",
    "orchestrat", "agentic", "autonomous agent", "agent framework", "copilot", "workflow")
_AI_DROP = ("de-aging", "biological youth", "longevity", "climate", "vaccine", "crispr")

def _ai_relevant(title, content):
    t = (str(title) + " " + str(content or "")).lower()
    if any(k in t for k in _AI_DROP) and not any(s in t for s in ("llm","artificial intelligence","multi-agent","generative ai")):
        return False
    return any(k in t for k in _AI_KEEP)

def rewrite(title, content, source):
    key = os.environ["AZURE_OPENAI_API_KEY"]; ep = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    url = f"{ep}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    body = json.dumps({"messages": [{"role": "user", "content": PROMPT.format(
        title=title, source=source, content=(content or "")[:6000])}],
        "temperature": 0.7, "max_tokens": 2600, "response_format": {"type": "json_object"}}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Content-Type": "application/json", "api-key": key})
    try:
        r = urllib.request.urlopen(req, timeout=90, context=_ctx())
    except ssl.SSLError:
        unv = ssl.create_default_context(); unv.check_hostname = False; unv.verify_mode = ssl.CERT_NONE
        r = urllib.request.urlopen(req, timeout=90, context=unv)
    data = json.loads(json.loads(r.read().decode())["choices"][0]["message"]["content"])
    content = data.get("content", "")
    # On RETIRE toute section source écrite par le modèle (URL potentiellement inventée)…
    content = re.sub(r'\n*#{1,6}\s*Sources?\b.*$', '', content, flags=re.S | re.I).rstrip()
    content = re.sub(r'\n*Source\s*:.*$', '', content, flags=re.S | re.I).rstrip()
    # …et on remet le VRAI lien du flux (déterministe), cliquable. Jamais l'URL du modèle.
    if source:
        dom = re.sub(r"^https?://(www\.)?", "", source).split("/")[0]
        content += f"\n\n## Source\n\n[{dom}]({source})"
    data["content"] = content
    data["_source"] = source
    return data

def md(t):
    t = esc(t)
    t = re.sub(r"^## (.+)$", r"<h2>\1</h2>", t, flags=re.M)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'(^|[\s>])(https?://[^\s<)"]+)', r'\1<a href="\2" target="_blank" rel="noopener">\2</a>', t)  # autolien URLs brutes
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    paras = []
    for blk in t.split("\n\n"):
        blk = blk.strip()
        if not blk: continue
        paras.append(blk if blk.startswith("<h2>") else f"<p>{blk}</p>")
    return "\n".join(paras)

BLOG_CSS = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--bg-deep:#0a0a0f;--bg-dark:#0f0f18;--bg-card:#14141f;--bg-card-hover:#1a1a28;
      --text-primary:#e8e6e3;--text-secondary:#8a8a9a;--text-muted:#5a5a6a;--accent:#6366f1}
    html{scroll-behavior:smooth}
    body{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg-deep);color:var(--text-secondary);line-height:1.75;-webkit-font-smoothing:antialiased}
    a{color:inherit;text-decoration:none}.serif{font-family:'Instrument Serif',serif;font-weight:400}
    ::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:var(--bg-deep)}::-webkit-scrollbar-thumb{background:var(--accent);border-radius:4px}
    .nav{position:fixed;top:0;left:0;right:0;z-index:50;background:rgba(10,10,15,.85);backdrop-filter:blur(14px);border-bottom:1px solid rgba(255,255,255,.06);padding:.9rem 0}
    .nav-inner{max-width:72rem;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;justify-content:space-between}
    .brand{font-size:1.25rem;font-weight:700;letter-spacing:.14em;color:var(--text-primary)}
    .nav-links{display:flex;align-items:center;gap:1.75rem}.nav-links a{font-size:.9rem;color:var(--text-secondary);transition:color .2s}
    .nav-links a:hover,.nav-links a.active{color:var(--text-primary)}
    .nav-toggle{display:none;background:none;border:0;color:var(--text-primary);font-size:1.5rem;cursor:pointer}
    @media(max-width:760px){.nav-toggle{display:block}.nav-links{position:absolute;top:100%;left:0;right:0;flex-direction:column;align-items:flex-start;gap:0;background:rgba(10,10,15,.98);border-bottom:1px solid rgba(255,255,255,.08);padding:.75rem 1.5rem 1rem;display:none}.nav-links.open{display:flex}.nav-links a{padding:.6rem 0;width:100%}}
    .wrap{max-width:46rem;margin:0 auto;padding:0 1.5rem}
    .hero{padding:7.5rem 0 1rem;text-align:center}.hero h1{font-size:3rem;color:var(--text-primary);margin-bottom:.8rem}
    .hero p{color:var(--text-secondary);max-width:38rem;margin:0 auto}
    .filters{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin:2rem auto;max-width:46rem;padding:0 1.5rem}
    .fbtn{padding:.5rem 1.1rem;border-radius:999px;font-size:.85rem;background:var(--bg-card);color:var(--text-secondary);border:1px solid rgba(255,255,255,.08);cursor:pointer;transition:all .2s}
    .fbtn:hover{color:var(--text-primary)}.fbtn.active{color:#fff;border-color:var(--c)}
    .cards{display:grid;grid-template-columns:1fr;gap:1.25rem;max-width:62rem;margin:0 auto;padding:0 1.5rem}
    @media(min-width:680px){.cards{grid-template-columns:1fr 1fr}}@media(min-width:1000px){.cards{grid-template-columns:1fr 1fr 1fr}}
    .card{display:block;border-radius:1rem;border:1px solid rgba(255,255,255,.08);background:var(--bg-card);overflow:hidden;transition:all .2s}
    .card:hover{transform:translateY(-3px);background:var(--bg-card-hover)}
    .card-top{height:4px;background:var(--c)}
    .card-body{padding:1.3rem}
    .card .cat{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.66rem;font-weight:600;margin-bottom:.7rem}
    .card h3{font-size:1.08rem;color:var(--text-primary);line-height:1.35;margin-bottom:.5rem}
    .card .ex{font-size:.86rem;color:var(--text-muted)}
    .card .date{font-size:.72rem;color:var(--text-muted);margin-top:.8rem}
    /* article */
    .art{max-width:44rem;margin:0 auto;padding:7rem 1.5rem 0}
    .art .cat{display:inline-block;padding:.25rem .8rem;border-radius:999px;font-size:.72rem;font-weight:600;margin-bottom:1rem}
    .art h1{font-size:2.5rem;line-height:1.12;color:var(--text-primary);margin-bottom:.8rem}
    .art .meta{font-size:.82rem;color:var(--text-muted);margin-bottom:2rem}
    .prose h2{font-family:'Instrument Serif',serif;font-size:1.6rem;color:var(--text-primary);margin:2rem 0 .8rem;font-weight:400}
    .prose p{margin-bottom:1.2rem}.prose strong{color:var(--text-primary)}
    .prose a{color:var(--accent);text-decoration:underline}
    .back{display:inline-flex;gap:.4rem;margin-bottom:1.25rem;font-size:.85rem;font-weight:500;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:.35rem .9rem}
    .back:hover{background:var(--accent);color:#fff}
    .tags{display:flex;flex-wrap:wrap;gap:.5rem;margin:2rem 0}
    .tag{padding:.25rem .75rem;border-radius:999px;font-size:.72rem}
    .foot{border-top:1px solid rgba(255,255,255,.06);margin-top:3rem;padding:2.5rem 1.5rem;text-align:center;color:var(--text-muted);font-size:.8rem}
"""

def _nav(blog=True):
    return f'''<nav class="nav"><div class="nav-inner">
    <a href="{BASE}/" class="brand">SOPHYIA</a>
    <button class="nav-toggle" aria-label="Menu" onclick="this.nextElementSibling.classList.toggle('open')">&#9776;</button>
    <div class="nav-links">
      <a href="{BASE}/#engine">Platform</a><a href="{BASE}/#solutions">Solutions</a>
      <a href="/blog/"{' class="active"' if blog else ''}>Blog</a><a href="/faq/">FAQ</a>
      <a href="{BASE}/#contact">Contact</a>
    </div></div></nav>'''

def _head(title, desc, canonical, ld=None):
    lds = f'<script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False, indent=2)}\n</script>' if ld else ""
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/og-image.png"><meta name="twitter:card" content="summary_large_image">
{FAVICON}{FONTS}{lds}<style>{BLOG_CSS}</style></head><body>'''

def article_html(a):
    cat = a["category"]; acc = CATEGORIES[cat]["accent"]; lab = CATEGORIES[cat]["label"]
    d = a["article_data"]; canonical = f"{BASE}/blog/{a['slug']}.html"
    ld = {"@context":"https://schema.org","@type":"BlogPosting","headline":d["title"],
          "datePublished":a["date"],"inLanguage":"en","url":canonical,
          "author":{"@type":"Organization","name":"Sophyia","url":BASE},
          "publisher":{"@type":"Organization","name":"Sophyia","url":BASE}}
    tags = "".join(f'<span class="tag" style="background:{acc}1f;color:{acc}">#{esc(t)}</span>' for t in d.get("tags", [])[:4])
    date_fmt = datetime.date.fromisoformat(a["date"]).strftime("%d %B %Y")
    src = a.get("source", "")
    src_bit = ""
    if src:
        sdom = re.sub(r"^https?://(www\.)?", "", src).split("/")[0]
        src_bit = f' · Source: <a href="{src}" target="_blank" rel="noopener" style="color:{acc}">{esc(sdom)}</a>'
    h = _head(f'{d["title"]} | Sophyia', d.get("meta", d["title"]), canonical, ld)
    h += f'''
{_nav()}
<article class="art" style="--accent:{acc}">
  <a href="/blog/" class="back">&larr; All articles</a>
  <div><span class="cat" style="background:{acc}1f;color:{acc}">{esc(lab)}</span></div>
  <h1 class="serif">{esc(d["title"])}</h1>
  <div class="meta">{date_fmt}{src_bit}</div>
  <div class="prose">
{md(d["content"])}
  </div>
  <div class="tags">{tags}</div>
</article>
<footer class="foot">&copy; 2026 Sophyia — Swiss intelligence orchestration. <a href="{BASE}/" style="color:{acc}">sophyia.io</a> · <a href="/faq/" style="color:{acc}">FAQ</a></footer>
</body></html>'''
    return h

def card(a):
    cat = a["category"]; acc = CATEGORIES[cat]["accent"]; d = a["article_data"]
    date_fmt = datetime.date.fromisoformat(a["date"]).strftime("%d %b %Y")
    return (f'<a class="card" href="/blog/{a["slug"]}.html" data-cat="{cat}" style="--c:{acc}">'
            f'<div class="card-top"></div><div class="card-body">'
            f'<span class="cat" style="background:{acc}1f;color:{acc}">{esc(CATEGORIES[cat]["label"])}</span>'
            f'<h3>{esc(d["title"])}</h3><p class="ex">{esc(d.get("excerpt",""))}</p>'
            f'<div class="date">{date_fmt}</div></div></a>')

def build_hub(data):
    data = sorted(data, key=lambda x: x.get("date",""), reverse=True)
    filters = '<button class="fbtn active" onclick="flt(\'all\',this)" style="--c:#6366f1">All</button>' + "".join(
        f'<button class="fbtn" onclick="flt(\'{k}\',this)" style="--c:{v["accent"]}">{esc(v["label"])}</button>' for k,v in CATEGORIES.items())
    cards = "\n".join("  "+card(a) for a in data)
    h = _head("Blog — Sophyia | AI & multi-agent engineering",
              "Sophyia's blog on artificial intelligence, multi-agent systems and AI for developers — analysis and signals from the field.",
              f"{BASE}/blog/")
    h += f'''
{_nav()}
<header class="hero wrap"><h1 class="serif">Signals &amp; Analysis</h1>
<p>Artificial intelligence, multi-agent systems and AI for developers — what matters, rewritten with the Sophyia lens.</p></header>
<div class="filters">{filters}</div>
<section class="cards" id="cards">
{cards}
</section>
<footer class="foot">&copy; 2026 Sophyia — Swiss intelligence orchestration. <a href="{BASE}/" style="color:#6366f1">sophyia.io</a></footer>
<script>function flt(c,b){{document.querySelectorAll('.fbtn').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelectorAll('#cards .card').forEach(k=>{{k.style.display=(c==='all'||k.dataset.cat===c)?'':'none'}})}}</script>
</body></html>'''
    return h

def load(): return json.loads(DATA.read_text()) if DATA.exists() else []
def save(d): DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2))

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=3); p.add_argument("--category", default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    BLOG.mkdir(exist_ok=True)
    data = load(); seen = {a["slug"] for a in data}; today = datetime.date.today().isoformat()
    new = 0
    for url in ALL_FEEDS:
        if new >= args.max: break
        for raw in scrape(url, 6):
            if new >= args.max: break
            slug = slugify(raw["title"])
            if not raw["title"] or slug in seen: continue
            if not _ai_relevant(raw["title"], raw.get("content","")):
                print(f"  [skip off-topic] {raw['title'][:55]}"); continue
            cat = detect_category(raw["title"], raw.get("content",""))
            if args.category and cat != args.category: continue
            print(f"  [{cat}] {raw['title'][:60]}")
            if args.dry_run: continue
            try:
                d = rewrite(raw["title"], raw["content"], raw.get("link",""))
            except Exception as e:
                print(f"    [ERR] {e}"); continue
            entry = {"slug": slug, "category": cat, "date": today, "source": raw.get("link", ""), "article_data": d}
            (BLOG / f"{slug}.html").write_text(article_html(entry), encoding="utf-8")
            data.append(entry); seen.add(slug); new += 1
            print(f"    ok -> blog/{slug}.html")
    save(data)
    (BLOG / "index.html").write_text(build_hub(data), encoding="utf-8")
    print(f"✓ {new} nouvel(s) article(s) · hub régénéré ({len(data)} au total)")

if __name__ == "__main__":
    main()
