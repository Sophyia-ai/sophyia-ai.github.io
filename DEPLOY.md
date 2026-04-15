# Sophyia.io — Documentation complete du site

## 1. Informations generales

| Element | Valeur |
|---------|--------|
| Compte Firebase | `hello@sophyia.io` |
| Projet Firebase | `sophyia-lab` |
| Console | https://console.firebase.google.com/project/sophyia-lab/overview |
| URL de prod | https://sophyia-lab.web.app |
| Domaine custom | `sophyia.io` (via CNAME, bascule Firebase en cours) |
| Repo GitHub | `git@github.com:Sophyia-ai/sophyia-ai.github.io.git` |
| Dossier local | `/Users/raoul/Documents/Clients/Sofyia/sophyia-ai.github.io/` |

## 2. Structure du projet

```
sophyia-ai.github.io/
├── index.html                    ← Site complet (single-page, tout en un)
├── 404.html                      ← Page erreur (generee par Firebase)
├── CNAME                         ← sophyia.io
├── firebase.json                 ← Config hosting (public: ".")
├── .firebaserc                   ← Projet: sophyia-lab
├── DEPLOY.md                     ← CE FICHIER
└── .git/                         ← Repo GitHub
```

**Le site est un fichier unique `index.html`.** Pas de build, pas de framework, pas de dependances. Tout est inline : HTML, CSS, JS, traductions.

## 3. Architecture du index.html

Le fichier est organise en blocs dans cet ordre :

```
<head>
  ├── Meta SEO + Open Graph + Twitter Cards
  ├── Schema JSON-LD (Organization)
  ├── Fonts Google (DM Sans + Instrument Serif)
  ├── Favicon inline SVG
  └── <style> — TOUT le CSS inline
      ├── Variables CSS (:root)
      ├── Reset + layout general
      ├── Sidebar navigation
      ├── Hero section
      ├── Engine section
      ├── Solutions section
      ├── Team section
      ├── Lab section
      ├── Contact section + formulaire
      ├── Animations (reveal, fadeSlideUp)
      ├── Responsive (max-width: 768px)
      └── Lang selector

<body>
  ├── Sidebar (navigation fixe gauche)
  ├── Sidebar toggle (mobile)
  ├── Lang selector (fixe haut-droite) — EN · FR · DE · ES · IT
  ├── Sidebar overlay (mobile)
  ├── <main>
  │   ├── #welcome — Hero
  │   ├── #engine — The Atomic Swarm Architecture (4 cards)
  │   ├── #solutions — The Beasts + nOOai (2 cards)
  │   ├── #team — Founder bio + Trust blocks (Ark + Swiss Foundation)
  │   ├── #lab — Research Lab (4 cards)
  │   └── #contact — Contact info + Formulaire
  ├── <footer>
  └── <script> — TOUT le JS inline
      ├── Objet translations (en/fr/de/es/it)
      ├── setLanguage() — systeme i18n
      ├── Scroll reveal (IntersectionObserver)
      ├── Navigation active tracking
      ├── Sidebar toggle (mobile)
      ├── Email reveal (click-to-show)
      ├── Captcha mathematique
      ├── Form submit handler (honeypot + captcha + fetch)
      └── Init (savedLang + setLanguage)
```

## 4. Systeme i18n (internationalisation)

### Principe

5 langues : EN, FR, DE, ES, IT.

Chaque element traduisible a un attribut `data-i18n="cle"` dans le HTML. La fonction `setLanguage(lang)` parcourt tous ces elements et remplace leur `innerHTML` avec la traduction correspondante.

### Objet translations

Dans le `<script>`, l'objet `translations` contient toutes les cles :

```javascript
const translations = {
    en: { meta_title: "...", tagline: "...", ... },
    fr: { ... },
    de: { ... },
    es: { ... },
    it: { ... }
};
```

### Cles existantes (au 10/03/2026)

**Navigation & Hero :**
`meta_title`, `tagline`, `nav_welcome`, `nav_engine`, `nav_solutions`, `nav_team`, `nav_lab`, `nav_contact`, `supported_by`, `hero_label`, `hero_title`, `hero_text`, `hero_cta_primary`, `hero_cta_ghost`

**Engine :**
`engine_label`, `engine_title`, `engine_subtitle`, `engine_c1_title`, `engine_c1_text`, `engine_c2_title`, `engine_c2_text`, `engine_c3_title`, `engine_c3_text`, `engine_c4_title`, `engine_c4_text`, `engine_github`

**Solutions :**
`solutions_label`, `solutions_title`, `solutions_subtitle`

**Team :**
`team_label`, `team_title`

**Trust blocks :**
`trust_ark_title`, `trust_ark_text`, `trust_swiss_title`, `trust_swiss_text`

**Lab :**
`lab_label`, `lab_title`

**Contact :**
`contact_label`, `contact_title`

**Formulaire :**
`form_name`, `form_email`, `form_company`, `form_message`, `form_submit`, `form_captcha_error`, `form_success`, `email_click_reveal`

### Ajouter une traduction

1. Dans le HTML, ajouter `data-i18n="ma_cle"` sur l'element
2. Le texte brut dans le HTML sert de fallback (anglais par defaut)
3. Ajouter `ma_cle: "..."` dans les 5 blocs de langues de l'objet `translations`

### Langue par defaut

La langue est stockee dans `localStorage('preferredLang')`. Si absente, fallback sur `'en'`.

### Ce qui N'EST PAS traduit

- Footer — minimaliste, pas besoin
- Adresse physique — invariante
- Nom "Raoul Baudlez" — invariant
- Lien LinkedIn — invariant

### Ce qui A ETE traduit (14 avril 2026)

~50 nouvelles cles ajoutees dans les 5 langues :
- Solutions : The Beasts (tag, desc, 6 features, 9 audience tags, CTA)
- Solutions : nOOai (tag, desc, 6 features, 8 audience tags, CTA)
- Team : subtitle, founder_title, founder_bio (traduit dans les 5 langues)
- Lab : titre, subtitle, 6 cartes (tag + titre + desc chacune), note
- Contact : cta_title, cta_text
- Audience : target_audience label

### Captcha — cas special

Le label du captcha ("Verification: what is X + Y?") n'utilise PAS `data-i18n` car il contient des nombres dynamiques. Il est gere par l'objet `captchaLabels` dans le JS, avec une fonction par langue :

```javascript
const captchaLabels = {
    en: (a, b) => `Verification: what is ${a} + ${b}?`,
    fr: (a, b) => `Vérification : combien font ${a} + ${b} ?`,
    ...
};
```

Le label est rafraichi automatiquement quand on change de langue (via le wrapper autour de `setLanguage`).

## 5. Anti-spam — 4 couches de protection

### Couche 1 : Honeypot

```html
<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
```

Champ invisible. Les bots le remplissent, les humains non. Si rempli, le JS ignore silencieusement le submit.

### Couche 2 : Captcha mathematique

Question aleatoire "combien font X + Y ?" (X et Y entre 1 et 9). Regeneree a chaque erreur et a chaque changement de langue. Traduite dans les 5 langues.

### Couche 3 : Interception JS (pas de POST direct)

Le `<form>` n'a PAS d'attribut `action`. Impossible de poster directement sur l'endpoint. Le JS intercepte le submit, valide honeypot + captcha, puis envoie via `fetch()` :

```javascript
await fetch('https://formspree.io/f/mdalkdoo', {
    method: 'POST', body: formData,
    headers: { 'Accept': 'application/json' }
});
```

L'endpoint Formspree (`mdalkdoo`) n'est visible que dans le JS, pas dans le HTML du form.

### Couche 4 : Email obfusque (click-to-reveal)

L'email `hello@sophyia.io` n'apparait JAMAIS dans le HTML brut. Il est decoupe en deux attributs data :

```html
<a href="#" id="email-link" data-n="hello" data-d="sophyia.io" style="display:none;"></a>
```

Un texte "Cliquer pour reveler l'email" (traduit) s'affiche a la place. Au clic, le JS reconstruit l'adresse et l'affiche. Les crawlers ne voient que `data-n` et `data-d` — pas un email valide.

### Schema JSON-LD

L'email a ete retire du schema JSON-LD. Le `contactPoint` pointe vers l'URL de la section contact :

```json
"contactPoint": {
    "@type": "ContactPoint",
    "url": "https://sophyia.io/#contact",
    "contactType": "customer support"
}
```

### Comparaison avec raoulbaudlez.com

| Protection | raoulbaudlez.com | sophyia.io |
|-----------|-----------------|------------|
| Email obfusque | Oui (morceaux JS) | Oui (data attributes + click-to-reveal) |
| Honeypot | Oui | Oui |
| Captcha math | Oui | Oui |
| Envoi indirect | Oui (mailto:) | Oui (fetch vers Formspree) |
| Endpoint expose dans HTML | Non | Non (retire du `<form action>`) |

## 6. Formspree

| Element | Valeur |
|---------|--------|
| Endpoint | `https://formspree.io/f/mdalkdoo` |
| Champs envoyes | `name`, `email`, `company`, `message`, `_subject` |
| Subject | "New contact from sophyia.io" |

Les messages arrivent sur l'email configure dans le dashboard Formspree. Verifier sur https://formspree.io (connexion avec le compte Sophyia).

## 7. Deploiement

### Deployer une mise a jour

```bash
cd "/Users/raoul/Documents/Clients/Sofyia/sophyia-ai.github.io"
firebase deploy
```

Le site est live en ~10 secondes sur https://sophyia-lab.web.app.

### Si credentials expirees

```bash
firebase login --reauth
```

Ca ouvre le navigateur. Se connecter avec `hello@sophyia.io`. Puis relancer `firebase deploy`.

### Tester en local avant deploiement

```bash
open /Users/raoul/Documents/Clients/Sofyia/sophyia-ai.github.io/index.html
```

Ouvre le fichier directement dans le navigateur. Tout fonctionne en local sauf :
- L'envoi Formspree (necessite un vrai domaine)
- Les fonts Google (necessitent une connexion internet)

### Strategie de backups

Avant toute modification significative :

```bash
cp index.html index.html.bak-DESCRIPTION
```

Exemples utilises :
- `index.html.bak-ark-visible` — apres avoir montre le bloc Ark, avant i18n
- `index.html.bak-pre-antispam` — avant ajout des protections anti-spam

**Supprimer les backups** une fois la modification validee en prod. Ne pas les deployer (Firebase deploie tout le dossier).

### Premiere installation (deja fait)

Ces etapes ne sont a refaire que sur une nouvelle machine :

```bash
# 1. Installer Firebase CLI
npm install -g firebase-tools

# 2. Se connecter (compte hello@sophyia.io)
firebase login

# 3. Initialiser le projet (deja fait, ne pas refaire)
cd "/Users/raoul/Documents/Clients/Sofyia/sophyia-ai.github.io"
firebase init hosting
# → Use existing project: sophyia-lab
# → Public directory: .
# → Single-page app: No
# → GitHub deploys: No
```

## 8. Domaine custom (sophyia.io)

Le CNAME `sophyia.io` pointe vers GitHub Pages (historique). Pour le basculer vers Firebase :

1. Console Firebase → Hosting → Domaines personnalises → Ajouter un domaine
2. Entrer `sophyia.io`
3. Firebase donne des enregistrements DNS (A ou TXT) a configurer chez le registrar
4. Attendre propagation DNS (~24h)

**Etat actuel** : le CNAME pointe encore vers GitHub Pages. Le site est accessible via `sophyia-lab.web.app`.

## 9. Rollback

Firebase garde un historique des versions :

1. Console Firebase → Hosting → Historique des versions
2. Cliquer sur la version precedente → "Deployer cette version"

Ou en CLI :
```bash
firebase hosting:channel:list
```

## 10. GitHub (backup)

Le repo GitHub `sophyia-ai/sophyia-ai.github.io` existe toujours mais n'est plus la source de verite pour le deploiement. Firebase est le canal principal.

Pour pousser sur GitHub (backup) :
```bash
cd "/Users/raoul/Documents/Clients/Sofyia/sophyia-ai.github.io"
git add index.html
git commit -m "Update site"
git push origin main
```

## 11. Lien avec Google Cloud / Vertex

Le projet Firebase `sophyia-lab` est lie au projet Google Cloud du meme nom :

- La console GCP (https://console.cloud.google.com) montre le meme projet
- Les APIs Google Cloud (Vertex AI, Gemini, etc.) sont disponibles dans le meme projet
- Le billing est partage (meme compte de facturation)
- Firebase Hosting est un service Google Cloud sous le capot

| Projet | Usage |
|--------|-------|
| `sophyia-lab` | Site sophyia.io (Firebase Hosting) + futur APIs |
| VPS `34.65.237.57` | nOOai Gemini (Compute Engine, meme billing) |

## 12. SEO & metadata

### Meta tags

- `<title>` et `<meta description>` en anglais (traduits dynamiquement via `meta_title`)
- Open Graph (LinkedIn, Slack, email previews) : `og:title`, `og:description`, `og:image`, `og:url`
- Twitter Cards : `twitter:title`, `twitter:description`
- `hreflang` : EN, FR, DE, ES, IT + x-default — tous pointent vers `https://sophyia.io/`

### Schema JSON-LD

Organisation structuree avec : nom, URL, description, date de fondation, adresse (Crans-Montana), LinkedIn, deux produits (The Beasts + nOOai), keywords.

**Attention** : le `contactPoint.email` a ete volontairement retire (anti-spam). Remplace par une URL vers `#contact`.

## 13. CSS — Variables et design system

```css
:root {
    --bg-deep: #0a0a0f;        /* Fond le plus sombre */
    --bg-dark: #0f0f18;        /* Fond des sections alternees */
    --bg-card: #14141f;        /* Fond des cartes */
    --bg-card-hover: #1a1a28;  /* Hover des cartes */
    --sidebar-bg: #08080d;     /* Sidebar */
    --text-primary: #f0f0f5;   /* Texte principal */
    --text-secondary: #a0a0b0; /* Texte secondaire */
    --text-muted: #6a6a7a;     /* Texte discret */
    --accent-primary: #6366f1; /* Violet principal (indigo) */
    --accent-secondary: #818cf8; /* Violet clair */
    --accent-glow: rgba(99,102,241,0.15); /* Glow focus */
    --border-subtle: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --transition-smooth: cubic-bezier(0.22, 1, 0.36, 1);
    --sidebar-width: 260px;
}
```

Fonts : **DM Sans** (corps) + **Instrument Serif** (titres).

## 14. Pieges connus

| Piege | Detail |
|-------|--------|
| **Backups dans le dossier** | Firebase deploie TOUT le dossier. Supprimer les `.bak` avant `firebase deploy` sinon ils seront accessibles publiquement |
| **Credentials Firebase** | Expirent regulierement. `firebase login --reauth` pour renouveler |
| **Captcha dynamique** | Le label du captcha n'utilise pas `data-i18n` — il est gere par `captchaLabels` + wrapper `setLanguage`. Si on ajoute une 6eme langue, penser a ajouter l'entree dans `captchaLabels` |
| **setLanguage wrappee** | Le JS ecrase `setLanguage` avec un wrapper qui rafraichit le captcha. Ne pas re-declarer `setLanguage` apres ce point |
| **Formspree en local** | Le fetch vers Formspree echoue en local (CORS). Normal. Tester le formulaire uniquement en prod |
| **Fonts en local** | Si pas de connexion internet, les fonts Google ne chargent pas. Le site reste lisible (fallback sans-serif) |
| **Email reveal one-way** | Une fois l'email revele, pas de bouton pour le re-masquer. C'est voulu — le but est juste d'empecher le scraping automatique |
| **Pas de `placeholder` sur les inputs** | Les placeholders ont ete retires car non traduits par le systeme `data-i18n` (les placeholders sont des attributs, pas du innerHTML). Ajouter un systeme dedie si besoin |

## 15. Historique des modifications

| Date | Modification |
|------|-------------|
| 2026-03 | Creation initiale du site — single-page, design sombre, 5 sections |
| 2026-03 | Ajout Firebase Hosting (migration depuis GitHub Pages) |
| 2026-03 | Ajout i18n 5 langues (EN/FR/DE/ES/IT) — selecteur haut-droite |
| 2026-03-06 | Bloc "Supported by The Ark" rendu visible (etait `display:none`) |
| 2026-03-06 | Bloc Ark + Swiss Foundation branches sur le systeme i18n |
| 2026-03-06 | Anti-spam : honeypot + captcha math + interception JS + email click-to-reveal |
| 2026-03-06 | Labels formulaire traduits dans les 5 langues |
| 2026-03-06 | Email retire du schema JSON-LD (remplace par URL #contact) |
| 2026-03-06 | Placeholders retires des inputs formulaire |
| 2026-04-14 | i18n complet : ~50 cles ajoutees (Solutions, Team bio, Lab, Contact) dans les 5 langues |
