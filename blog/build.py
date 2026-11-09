#!/usr/bin/env python3
"""Генератор сторінок блогу: python3 blog/build.py

Дані статей — blog/blog-data.json (скопійовано зі старого сайту virabalkans.com),
картинки — blog/img/<slug>/, стилі — blog/blog.css + portfolio-products/assets/site.css.
Результат: blog/index.html і blog/<slug>/index.html. Node.js не потрібен.
"""
import importlib.util
import json
from html import escape as _esc
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'blog'

# Шапка, меню, футер і скрипт мов — ті самі, що в каталозі
_spec = importlib.util.spec_from_file_location('catalog_build', ROOT / 'catalog' / 'build.py')
cat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cat)

POSTS = json.loads((OUT / 'blog-data.json').read_text(encoding='utf-8'))
CAT_LABEL = {'export': 'Експорт', 'silhoz': 'Сільськогосподарські технології'}
CAT_OVERRIDE = {'maybutni-kontrakty-na-ripakovu-oliyu-vidkryto-obhovorennya-ta-bronyuva': 'Контракти'}
EN_TITLES = {
    'kompaniya-virabalkans-vzyala-uchast-u-mizhnarodniy-vystavtsi-alimentar': 'Virabalkans took part in the international exhibition Alimentaria 2026',
    'kompaniya-virabalkans-vzyala-uchast-u-mizhnarod': 'Virabalkans at the global conference Fi Europe',
    'maybutni-kontrakty-na-ripakovu-oliyu-vidkryto-obhovorennya-ta-bronyuva': 'Future rapeseed oil contracts: discussion and booking are open',
    'uspishnyy-tyzhden-mizhnarodnykh-prodazhiv': 'A successful week of international sales',
    'novynka-profesiyne-maslo-dlya-frytyuru-pro-horeka': 'New: Pro Horeca professional frying oil',
    'vitannya-z-dnem-peremohy-podyaky-batki': "Congratulations on Victory and Homeland Thanksgiving Day and Croatian Defenders' Day!",
    'oliya-yaka-robyty-smazhennya-pryyemnishym-i-chystishym': 'Oil that makes frying more pleasant and cleaner',
    'choose-proven-rapeseed-products': 'Your business deserves better: choose proven rapeseed products',
    'soyeva-oliya-kraljevski-ukus-universalnyy-inhrediyent-dlya-kukhni': 'Kraljevski Ukus soybean oil — a versatile ingredient for the kitchen',
    'our-products-even-closer-to-you': 'Our products are even closer to you!',
    'uspishna-spivpratsya-z-ntc-yakisnyy-produkt-shche-blyzhche-do-vas': 'Successful cooperation with NTC – quality product even closer to you!',
    'ukrainian-quality-on-the-shelves-of-montenegro': 'Ukrainian quality on the shelves of Montenegro!',
}
EXTRA_EN = {
    'Блог': 'Blog', 'Новини': 'News', 'Виставки, контракти та новинки.': 'Exhibitions, contracts and new products.',
    'Читати': 'Read', 'Усі новини': 'All news', 'Експорт': 'Export', 'Контракти': 'Contracts',
    'Сільськогосподарські технології': 'Agricultural technologies', 'Блог VIRA': 'VIRA blog',
    'Новини та події': 'News and events', 'Перейти до статті': 'Skip to the article',
}
for p in POSTS:
    p['label'] = CAT_OVERRIDE.get(p['slug']) or CAT_LABEL.get(p['cat'], 'Новини')
    EXTRA_EN[p['title']] = EN_TITLES[p['slug']]
cat.EN.update(EXTRA_EN)


def dedupe(body):
    """У старій статті про Alimentaria абзаци повторюються — прибираємо точні дублі всередині <p>."""
    import re

    def fix(m):
        seen, out = set(), []
        for part in re.split(r'(?:<br\s*/?>|\n)', m.group(1)):
            key = re.sub(r'\s+', ' ', part).strip()
            if key and key in seen:
                continue
            seen.add(key)
            out.append(part)
        return '<p>' + '<br>'.join(out) + '</p>'
    return re.sub(r'<p>(.*?)</p>', fix, body, flags=re.S)


for p in POSTS:
    p['body'] = dedupe(p['body'])


def esc(v):
    return _esc(str(v), quote=True)


def head(title, description, extra_class=''):
    return f'''<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0A0A0B">
  <title>{esc(title)}</title><meta name="description" content="{esc(description)}">
  <link rel="icon" type="image/svg+xml" href="/portfolio-products/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/portfolio-products/assets/site.css"><link rel="stylesheet" href="/blog/blog.css">
  <link rel="preload" as="image" href="/portfolio-products/assets/hero-sunflowers.jpg">
</head><body id="top" class="{extra_class}">
  <a class="skip-link" href="#main">Перейти до статті</a>'''


def tail():
    script = cat.MENU_SCRIPT.replace('__DICT__', json.dumps(cat.EN, ensure_ascii=False))
    return f'''  {cat.SITE_FOOTER}
  {cat.MOBILE_MENU}
  <div id="google_translate_element" class="gt-hidden" translate="no"></div>
  <script>window.VIRA_GT = true;</script>
  {script}
</body></html>
'''


def cta():
    return cat.cta(None)


def card(p):
    return f'''<a class="post-card" href="/blog/{p['slug']}/">
    <span class="post-card-img"><img src="{p['thumb']}" alt="" loading="lazy" decoding="async"></span>
    <span class="post-card-body">
      <span class="post-meta"><span class="post-cat">{esc(p['label'])}</span><span>{p['date']}</span></span>
      <strong>{esc(p['title'])}</strong>
      <span class="post-excerpt">{esc(p['excerpt'])}</span>
      <span class="post-more">Читати <span aria-hidden="true">↗</span></span>
    </span>
  </a>'''


def index_page():
    cards = ''.join(card(p) for p in POSTS)
    return head('Блог — VIRA', 'Новини VIRA: виставки, контракти та новинки.') + f'''
  <div class="hero"><div class="hero-shade">
    {cat.SITE_NAV}
    <div class="hero-copy container"><p class="eyebrow light">Блог VIRA</p><h1>Новини та події</h1><p>Виставки, контракти та новинки.</p></div></div></div>
  <main id="main" class="catalog-surface"><div class="container">
    <nav class="breadcrumbs" aria-label="Навігація"><a href="/#about">Головна</a><span aria-hidden="true">/</span><span aria-current="page">Блог</span></nav>
    <div class="post-grid">{cards}</div>
    {cta()}
  </div></main>
''' + tail()


def article_page(p):
    return head(f"{p['title']} — VIRA", p['excerpt'][:200]) + f'''
  <div class="hero hero-article"><div class="hero-shade">
    {cat.SITE_NAV}
    <div class="hero-copy container"><p class="eyebrow light"><span>{esc(p['label'])}</span> · {p['date']}</p><h1>{esc(p['title'])}</h1></div></div></div>
  <main id="main" class="catalog-surface"><div class="container">
    <nav class="breadcrumbs" aria-label="Навігація"><a href="/#about">Головна</a><span aria-hidden="true">/</span><a href="/blog/">Блог</a><span aria-hidden="true">/</span><span aria-current="page">{esc(p['title'])}</span></nav>
    <article class="article">
      <img class="article-hero" src="{p['hero']}" alt="{esc(p['title'])}" fetchpriority="high" decoding="async">
      <div class="article-body">
{p['body']}
      </div>
      <p class="mt-note" translate="no">The article text is translated automatically by Google Translate.</p>
      <a class="back-link" href="/blog/"><span aria-hidden="true">←</span> Усі новини</a>
    </article>
    {cta()}
  </div></main>
''' + tail()


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'index.html').write_text(index_page(), encoding='utf-8')
    for p in POSTS:
        d = OUT / p['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(article_page(p), encoding='utf-8')
    print(f'Built blog index and {len(POSTS)} articles.')


main()
