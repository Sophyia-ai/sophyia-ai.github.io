#!/usr/bin/env python3
"""
faq_engine.py — FAQ statique pour sophyia.io (EN), à l'image du site (DM Sans / Instrument
Serif, fond sombre, accent indigo). FAQPage + BreadcrumbList JSON-LD, maillage interne.
Hébergement GitHub Pages → fichiers statiques servis directement.

Produit : faq/index.html (hub) + faq/<rubrique>.html
Usage   : python3 automation/faq_engine.py
"""
import html as _html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAQ = ROOT / "faq"
BASE = "https://sophyia.io"

# Rubriques — focus IA & dev. "live": True = page générée ; sinon "À venir" dans le hub.
RUBRIQUES = {
    "platform": {
        "live": True, "accent": "#6366f1",
        "label": "Platform & multi-agent AI",
        "title": "The Sophyia platform & multi-agent AI — questions & answers",
        "intro": "How Sophyia works: an intelligence orchestration platform that makes several AI instances reason, debate and adjudicate before answering — beyond the single model.",
        "qa": [
            {"q": "What is Sophyia?",
             "a": "Sophyia is a Swiss SaaS company building an intelligence orchestration platform. Instead of routing a question to a single AI model, Sophyia runs several AI instances that reason, debate and adjudicate before producing an answer — turning fragmented intelligence into reliable, auditable decisions. Its signature: \"Beyond the Single Model\"."},
            {"q": "What does \"Beyond the Single Model\" mean?",
             "a": "A conventional assistant sends your question to one model and returns its answer. Sophyia goes further: it orchestrates multiple instances in opposing cognitive roles — analyst, risk officer, contradictor, adjudicator — that argue against each other first. What you get is not one model's opinion, but what survives the debate, with the full reasoning trail attached."},
            {"q": "How does the orchestration architecture work?",
             "a": "Sophyia assigns AI instances distinct cognitive postures — generate, investigate, contradict, adjudicate — then puts them in structured confrontation. It is not an orchestrator routing prompts between tools: it is a cognitive architecture that engineers consensus between models, surfaces blind spots and objections, and eliminates much of the hallucination risk through cross-model validation."},
            {"q": "Does Sophyia need several different AI models to work?",
             "a": "No. The counter-intuitive part: running the same frontier model three, five or nine times in opposing roles surfaces objections, corrections and angles that no single pass produces. Depth is not a matter of upgrading the model — it is a property of the architecture. Sophyia therefore grows more powerful with every new model generation, without changing its principle."},
            {"q": "What does Sophyia do when the evidence is thin?",
             "a": "It is built to refuse. When the corpus is stale or the evidence is weak, Sophyia says so and names the data it is missing, rather than producing a plausible but wrong answer. In regulated markets a confident wrong answer is the real liability — and it is the failure mode every single-model product structurally shares, because there is no one in the room to contradict it."},
            {"q": "Who is Sophyia for, and for which decisions?",
             "a": "Sophyia targets decisions that carry consequences — where a mistake is expensive and you must be able to prove why the answer you got is the right one. It generates and stress-tests scenarios, runs deep research in parallel and adjudicates complex cases. The architecture is not bound to one industry: it earns its place wherever accuracy, auditability and sovereignty decide."},
            {"q": "Where is Sophyia's data hosted?",
             "a": "Sophyia runs in Switzerland, on servers in Zurich: data and inference stay on Swiss soil. This sovereignty is not incidental — it is what makes Sophyia usable by regulated clients, for whom data residency and auditability determine adoption."},
            {"q": "What are the products built on the Sophyia platform?",
             "a": "Three products on one platform: Sophyia Chat, a business assistant deployed with paying customers; The Beasts, an autonomous multi-agent workforce for enterprise, with audit trails and structured debate; and nOOai, a live multi-agent debate platform. All rest on the same core: parallel cognition with depth."},
        ],
    },
    "products":   {"live": False, "accent": "#a855f7", "label": "Products",
                   "desc": "Sophyia Chat, The Beasts, nOOai — what each does."},
    "developers": {"live": False, "accent": "#06b6d4", "label": "AI for developers",
                   "desc": "Integrating multi-agent AI, APIs, use cases for dev teams."},
    "sovereignty":{"live": False, "accent": "#10b981", "label": "Sovereignty & Swiss hosting",
                   "desc": "Data residency, auditability, regulated markets."},
}

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">'
FAVICON = "<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='44' fill='none' stroke='%236366f1' stroke-width='8'/></svg>\">"

CSS = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--bg-deep:#0a0a0f;--bg-dark:#0f0f18;--bg-card:#14141f;--bg-card-hover:#1a1a28;
      --text-primary:#e8e6e3;--text-secondary:#8a8a9a;--text-muted:#5a5a6a;--accent:#6366f1}
    html{scroll-behavior:smooth}
    body{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg-deep);color:var(--text-secondary);line-height:1.7;-webkit-font-smoothing:antialiased}
    a{color:inherit;text-decoration:none}
    .serif{font-family:'Instrument Serif',serif;font-weight:400}
    ::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:var(--bg-deep)}::-webkit-scrollbar-thumb{background:var(--accent);border-radius:4px}
    .nav{position:fixed;top:0;left:0;right:0;z-index:50;background:rgba(10,10,15,.85);backdrop-filter:blur(14px);border-bottom:1px solid rgba(255,255,255,.06);padding:.9rem 0}
    .nav-inner{max-width:72rem;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;justify-content:space-between}
    .brand{font-size:1.25rem;font-weight:700;letter-spacing:.14em;color:var(--text-primary)}
    .nav-links{display:flex;align-items:center;gap:1.75rem}
    .nav-links a{font-size:.9rem;color:var(--text-secondary);transition:color .2s}
    .nav-links a:hover,.nav-links a.active{color:var(--text-primary)}
    .nav-toggle{display:none;background:none;border:0;color:var(--text-primary);font-size:1.5rem;line-height:1;cursor:pointer}
    @media(max-width:760px){.nav-toggle{display:block}.nav-links{position:absolute;top:100%;left:0;right:0;flex-direction:column;align-items:flex-start;gap:0;background:rgba(10,10,15,.98);border-bottom:1px solid rgba(255,255,255,.08);padding:.75rem 1.5rem 1rem;display:none}.nav-links.open{display:flex}.nav-links a{padding:.6rem 0;width:100%}}
    .wrap{max-width:48rem;margin:0 auto;padding:0 1.5rem}
    .header{padding:7.5rem 0 1rem}
    .crumb{font-size:.82rem;color:var(--text-muted);margin-bottom:1rem}
    .crumb a:hover{color:var(--text-secondary)}
    .back{display:inline-flex;align-items:center;gap:.4rem;margin-bottom:1.25rem;font-size:.85rem;font-weight:500;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:.35rem .9rem;transition:all .2s}
    .back:hover{background:var(--accent);color:#fff}
    .badge{display:inline-block;padding:.25rem .8rem;border-radius:999px;font-size:.72rem;font-weight:500;margin-bottom:1.1rem}
    h1.title{font-size:2.6rem;line-height:1.1;color:var(--text-primary);margin-bottom:1rem}
    .intro{font-size:1.05rem;color:var(--text-secondary);max-width:40rem}
    .list{max-width:48rem;margin:2.25rem auto 0;padding:0 1.5rem}
    details{border:1px solid rgba(255,255,255,.08);border-radius:.85rem;margin-bottom:.75rem;background:var(--bg-card);overflow:hidden;transition:border-color .2s}
    details[open]{border-color:var(--accent)}
    summary{list-style:none;cursor:pointer;padding:1.15rem 1.3rem;font-size:1.02rem;font-weight:500;color:var(--text-primary);display:flex;align-items:center;justify-content:space-between;gap:1rem}
    summary::-webkit-details-marker{display:none}
    summary::after{content:'+';font-size:1.5rem;color:var(--accent);font-weight:300}
    details[open] summary::after{content:'\\2212'}
    .ans{padding:0 1.3rem 1.3rem;font-size:.97rem;color:var(--text-secondary)}
    .ans a{color:var(--accent);text-decoration:underline}
    .cards{display:grid;grid-template-columns:1fr;gap:1rem;max-width:48rem;margin:0 auto;padding:0 1.5rem}
    @media(min-width:640px){.cards{grid-template-columns:1fr 1fr}}
    .card{display:block;padding:1.5rem;border-radius:1rem;border:1px solid rgba(255,255,255,.08);background:var(--bg-card);transition:all .2s;position:relative}
    .card:hover{transform:translateY(-2px);background:var(--bg-card-hover)}
    .card .cat{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.68rem;font-weight:600;margin-bottom:.7rem}
    .card h3{font-size:1.1rem;color:var(--text-primary);margin-bottom:.35rem}
    .card p{font-size:.85rem;color:var(--text-muted)}
    .card.soon{opacity:.55;pointer-events:none}
    .card.soon::after{content:'Soon';position:absolute;top:1rem;right:1rem;font-size:.62rem;color:var(--text-muted);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:.1rem .5rem}
    .related{max-width:48rem;margin:2.5rem auto;padding:1.4rem;background:var(--bg-dark);border:1px solid rgba(255,255,255,.06);border-radius:1rem}
    .related h2{font-size:.8rem;font-weight:600;color:var(--text-primary);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.9rem}
    .related ul{list-style:none;display:flex;flex-wrap:wrap;gap:.6rem}
    .related a{display:inline-block;padding:.4rem .9rem;border-radius:999px;font-size:.8rem;background:rgba(99,102,241,.12);color:var(--accent);border:1px solid rgba(99,102,241,.3)}
    .foot{border-top:1px solid rgba(255,255,255,.06);margin-top:2.5rem;padding:2.5rem 1.5rem;text-align:center;color:var(--text-muted);font-size:.8rem}
"""

def esc(s): return _html.escape(s, quote=True)

def _nav(active_faq=True):
    return f'''<nav class="nav"><div class="nav-inner">
    <a href="{BASE}/" class="brand">SOPHYIA</a>
    <button class="nav-toggle" aria-label="Menu" onclick="this.nextElementSibling.classList.toggle('open')">&#9776;</button>
    <div class="nav-links">
      <a href="{BASE}/#engine">Platform</a>
      <a href="{BASE}/#solutions">Solutions</a>
      <a href="/blog/">Blog</a>
      <a href="/faq/"{' class="active"' if active_faq else ''}>FAQ</a>
      <a href="{BASE}/#contact">Contact</a>
    </div>
  </div></nav>'''

def _head(title, desc, canonical, ld_blocks):
    lds = "\n".join(f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>' for b in ld_blocks)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/og-image.png"><meta name="twitter:card" content="summary_large_image">
{FAVICON}
{FONTS}
{lds}
<style>{CSS}</style>
</head>
<body>'''

def build_rubrique(key, rub):
    accent = rub["accent"]; label = rub["label"]; canonical = f"{BASE}/faq/{key}.html"
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage","inLanguage":"en","name":rub["title"],
              "url":canonical,"about":{"@type":"Organization","name":"Sophyia","url":BASE},
              "mainEntity":[{"@type":"Question","name":qa["q"],
                             "acceptedAnswer":{"@type":"Answer","text":qa["a"]}} for qa in rub["qa"]]}
    crumb_ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE},
        {"@type":"ListItem","position":2,"name":"FAQ","item":f"{BASE}/faq/"},
        {"@type":"ListItem","position":3,"name":label,"item":canonical}]}
    items = "\n".join(
        f'''    <details{" open" if i==0 else ""}>
      <summary>{esc(qa["q"])}</summary>
      <div class="ans"><p>{qa["a"]}</p></div>
    </details>''' for i,qa in enumerate(rub["qa"]))
    html = _head(f'{rub["title"]} | Sophyia', rub["intro"], canonical, [faq_ld, crumb_ld])
    html += f'''
{_nav()}
<header class="header wrap" style="--accent:{accent}">
  <a href="/faq/" class="back">&larr; All topics</a>
  <div class="crumb"><a href="{BASE}/">Home</a> &rsaquo; <a href="/faq/">FAQ</a> &rsaquo; {esc(label)}</div>
  <span class="badge" style="background:{accent}1f;color:{accent}">{esc(label)}</span>
  <h1 class="title serif">{esc(rub["title"])}</h1>
  <p class="intro">{esc(rub["intro"])}</p>
</header>
<main class="list" style="--accent:{accent}">
{items}
</main>
<section class="related">
  <h2>Explore</h2>
  <ul>
    <li><a href="/faq/">All FAQs</a></li>
    <li><a href="{BASE}/#engine">The platform</a></li>
    <li><a href="/blog/">Blog</a></li>
  </ul>
</section>
<footer class="foot">&copy; 2026 Sophyia — Swiss intelligence orchestration. <a href="{BASE}/" style="color:var(--accent)">sophyia.io</a></footer>
</body></html>'''
    return html

def build_hub():
    canonical = f"{BASE}/faq/"
    cards = []
    for key, rub in RUBRIQUES.items():
        acc = rub["accent"]
        if rub.get("live"):
            cards.append(f'<a class="card" href="/faq/{key}.html" style="--c:{acc}"><span class="cat" style="background:{acc}1f;color:{acc}">{esc(rub["label"])}</span><h3>{esc(rub["label"])}</h3><p>{esc(rub.get("intro","")[:90])}</p></a>')
        else:
            cards.append(f'<span class="card soon" style="--c:{acc}"><span class="cat" style="background:{acc}1f;color:{acc}">{esc(rub["label"])}</span><h3>{esc(rub["label"])}</h3><p>{esc(rub.get("desc",""))}</p></span>')
    html = _head("FAQ — Sophyia | Multi-agent AI platform",
                 "Questions & answers about Sophyia: the Swiss multi-agent AI orchestration platform, its products and its approach to AI for developers and regulated markets.",
                 canonical, [])
    html += f'''
{_nav()}
<header class="header wrap" style="text-align:center;--accent:#6366f1">
  <h1 class="title serif" style="font-size:3rem">Frequently asked questions</h1>
  <p class="intro" style="margin:0 auto">Clear answers about Sophyia — the multi-agent AI orchestration platform, its products, and AI for developers &amp; regulated markets.</p>
</header>
<section class="cards" style="margin-top:2.25rem">
{chr(10).join("  "+c for c in cards)}
</section>
<footer class="foot">&copy; 2026 Sophyia — Swiss intelligence orchestration. <a href="{BASE}/" style="color:#6366f1">sophyia.io</a></footer>
</body></html>'''
    return html

def main():
    FAQ.mkdir(parents=True, exist_ok=True)
    (FAQ / "index.html").write_text(build_hub(), encoding="utf-8")
    n = 1
    for key, rub in RUBRIQUES.items():
        if rub.get("live"):
            (FAQ / f"{key}.html").write_text(build_rubrique(key, rub), encoding="utf-8")
            n += 1
            print(f"  ✓ faq/{key}.html ({len(rub['qa'])} Q/A)")
    print(f"✓ hub + {n-1} rubrique(s) live générée(s)")

if __name__ == "__main__":
    main()
