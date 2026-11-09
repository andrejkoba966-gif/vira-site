#!/usr/bin/env python3
"""Генератор сторінок каталогу: python3 catalog/build.py

Дані — catalog/catalog-data.mjs, стилі — portfolio-products/assets/site.css.
Результат: portfolio-products/index.html і portfolio-products/<slug>/index.html
Node.js не потрібен.
"""
import ast
import re
from html import escape as _esc
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'portfolio-products'


def esc(value):
    return _esc(str(value), quote=True)


# ---------- Дані (JS-модуль читаємо як літерал Python) ----------
def load_data():
    text = (ROOT / 'catalog' / 'catalog-data.mjs').read_text(encoding='utf-8')
    base_path = re.search(r"basePath\s*=\s*'([^']+)'", text).group(1)
    body = re.search(r'export const categories =\s*(\[.*?\n\]);', text, re.S).group(1).rstrip(';')
    body = re.sub(r'^\s*//.*$', '', body, flags=re.M)
    body = re.sub(r'^(\s*)(slug|label|title|group|cover|products):', r"\1'\2':", body, flags=re.M)
    return ast.literal_eval(body), base_path


CATEGORIES, BASE = load_data()


def item_path(item):
    return f'{BASE}assets/products/{item[0]}.{item[2]}'


def category_path(category):
    return f"{BASE}{category['slug']}/"


def quantity(count):
    word = 'позиція' if count == 1 else ('позиції' if count < 5 else 'позицій')
    return f'{count} {word}'


# ---------- Шапка, меню й футер — як на головній сторінці сайту ----------
LOGO = '''<svg viewBox="0 0 40 40" aria-hidden="true"><g fill="none" stroke-width="2.2" stroke-linejoin="round">
            <path d="M20 26C16 18 16 10 20 4c4 6 4 14 0 22Z" stroke="#F5D90A"/>
            <path d="M20 26C13 22 9 16 9 9c6 1 11 7 11 17Z" stroke="#C9DC2B"/>
            <path d="M20 26c7-4 11-10 11-17-6 1-11 7-11 17Z" stroke="#C9DC2B"/>
            <path d="M20 26c-8 1-14-2-17-7 7-2 13 1 17 7Z" stroke="#F5D90A"/>
            <path d="M20 26c8 1 14-2 17-7-7-2-13 1-17 7Z" stroke="#F5D90A"/>
          </g></svg>'''

MENU = [('/#about', 'Про VIRA'), ('/#formats', 'Формати'), ('/portfolio-products/', 'Продукція'),
        ('/#geo', 'Географія'), ('/#faq', 'FAQ'), ('/#contact', 'Контакти')]

_links = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in MENU)

SITE_NAV = f'''<nav id="hero-nav">
      <div class="container">
        <a href="/" class="nav-logo" aria-label="VIRA">{LOGO}VIRA</a>
        <ul class="nav-links">{_links}</ul>
        <div class="nav-right">
          <a href="/#contact" class="nav-cta">Форма зв'язку</a>
          <button type="button" class="nav-burger" id="burger" aria-label="Меню" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
        </div>
      </div>
    </nav>'''

MOBILE_MENU = f'''<div id="mobile-menu" role="dialog" aria-modal="true" aria-label="Меню" aria-hidden="true">
  <div class="mm-top"><a href="/" class="nav-logo" aria-label="VIRA">{LOGO}VIRA</a><button type="button" class="mm-close" id="mm-close" aria-label="Закрити меню"></button></div>
  <ul class="mm-links">{_links}</ul>
  <div class="mm-bottom"><a href="/#contact" class="mm-cta">Форма зв'язку</a></div>
</div>'''

SITE_FOOTER = '''<footer>
  <div class="container">
    <div class="foot">
      <p class="tag">Смак України —<br>на столі в&nbsp;Європі<small>Офіційне представництво Victor &amp; K у Європі</small></p>
      <ul>
        <li><a href="/#about">Про VIRA</a></li><li><a href="/#formats">Формати співпраці</a></li><li><a href="/portfolio-products/">Продукція</a></li><li><a href="/#geo">Географія</a></li><li><a href="/#faq">FAQ</a></li>
      </ul>
      <ul>
        <li><a href="mailto:virabalkans@gmail.com">virabalkans@gmail.com</a></li><li><a href="tel:+385916001094">+385 91 600 1094</a></li><li><a href="https://virabalkans.com/blog-standard/">Блог</a></li><li><a href="https://virabalkans.com/about-viktork/">Про Victor &amp; K</a></li>
      </ul>
      <a class="up" href="#top" aria-label="Нагору"><span class="circle"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 13V3M4 7l4-4 4 4"/></svg></span></a>
    </div>
    <div class="legal"><span>VIRA © 2026. Усі права захищені.</span><a href="https://virabalkans.com/privacy-policy/">Політика конфіденційності</a></div>
  </div>
</footer>'''

MENU_SCRIPT = '''<script>
(function () {
  var m = document.getElementById('mobile-menu'), b = document.getElementById('burger'), c = document.getElementById('mm-close');
  function set(open) {
    m.classList.toggle('open', open); m.setAttribute('aria-hidden', open ? 'false' : 'true');
    b.setAttribute('aria-expanded', open ? 'true' : 'false'); document.documentElement.classList.toggle('menu-open', open);
  }
  b.addEventListener('click', function () { set(true); });
  c.addEventListener('click', function () { set(false); });
  m.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
})();
</script>'''


# ---------- Каталог ----------
def nav_links(selected):
    def group(kind):
        out = []
        for c in CATEGORIES:
            if c['group'] != kind:
                continue
            cur = ' aria-current="page"' if selected == c['slug'] else ''
            out.append(f'<a href="{category_path(c)}"{cur}><span>{esc(c["label"])}</span><span class="nav-count">{len(c["products"])}</span></a>')
        return ''.join(out)
    return (f'<div class="nav-group"><p class="nav-heading">Продукція</p>{group("products")}</div>\n'
            f'    <div class="nav-group"><p class="nav-heading">Спеціальні добірки</p>{group("collections")}</div>')


def navigation(selected):
    cur = '' if selected else ' aria-current="page"'
    return f'''<aside class="sidebar" aria-label="Категорії каталогу">
    <a class="all-link" href="{BASE}"{cur}>Усі категорії <span aria-hidden="true">↗</span></a>
    {nav_links(selected)}
  </aside>
  <details class="mobile-categories"><summary>Категорії <span aria-hidden="true">⌄</span></summary><nav aria-label="Категорії каталогу"><a class="all-link" href="{BASE}"{cur}>Усі категорії</a>{nav_links(selected)}</nav></details>'''


def product_card(item, index):
    title = item[1]
    description = item[3] if len(item) > 3 else None
    note = item[4] if len(item) > 4 else None
    loading = 'loading="lazy"' if index > 2 else 'fetchpriority="high"'
    desc = f'<p class="product-description">{esc(description)}</p>' if description else ''
    pack = f'<p class="package-note">{esc(note)}</p>' if note else ''
    return f'''<article class="product-card">
    <div class="product-image"><img src="{item_path(item)}" alt="{esc(title)}" {loading} decoding="async"></div>
    <div class="product-body"><h3>{esc(title)}</h3>{desc}{pack}</div>
  </article>'''


def category_tile(category):
    cover = next((i for i in category['products'] if i[0] == category.get('cover')), category['products'][0])
    return f'''<a class="category-tile" href="{category_path(category)}">
    <span class="category-image"><img src="{item_path(cover)}" alt="" loading="lazy" decoding="async"></span>
    <span class="category-info"><span><strong>{esc(category['title'])}</strong><small>{quantity(len(category['products']))}</small></span><span class="tile-arrow" aria-hidden="true">↗</span></span>
  </a>'''


def content(category):
    if not category:
        tiles = ''.join(category_tile(c) for c in CATEGORIES)
        return (f'<div class="section-heading"><div><p class="eyebrow dark">Портфоліо VIRA</p><h2>Оберіть категорію</h2>'
                f'<p class="section-intro">Увесь асортимент зібрано за напрямами. У кожної категорії є власна сторінка.</p></div>'
                f'<span class="result-count">{len(CATEGORIES)} категорій</span></div>\n      <div class="category-grid">{tiles}</div>')
    eyebrow = 'Спеціальна добірка' if category['group'] == 'collections' else 'Категорія продукції'
    cards = ''.join(product_card(item, i) for i, item in enumerate(category['products']))
    return (f'<div class="section-heading"><div><p class="eyebrow dark">{eyebrow}</p><h2>{esc(category["title"])}</h2></div>'
            f'<span class="result-count">{quantity(len(category["products"]))}</span></div>\n    <div class="product-grid">{cards}</div>')


def page(category=None):
    if category:
        title = f'{category["title"]} — Каталог VIRA'
        description = f'{category["title"]}: {quantity(len(category["products"]))} у каталозі VIRA.'
        catalog_crumb = f'<a href="{BASE}">Каталог</a><span aria-hidden="true">/</span><span aria-current="page">{esc(category["title"])}</span>'
        label = category['title']
        selected = category['slug']
    else:
        title = 'Каталог продукції — VIRA'
        description = 'Каталог продукції VIRA: олія, шрот, лецитин, етикетки, тара та ексклюзивні добірки.'
        catalog_crumb = '<span aria-current="page">Каталог</span>'
        label = 'Категорії каталогу'
        selected = None
    return f'''<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0A0A0B">
  <title>{esc(title)}</title><meta name="description" content="{esc(description)}">
  <link rel="icon" type="image/svg+xml" href="{BASE}assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{BASE}assets/site.css"><link rel="preload" as="image" href="{BASE}assets/hero-sunflowers.png">
</head><body id="top">
  <a class="skip-link" href="#main">Перейти до каталогу</a>
  <div class="hero"><div class="hero-shade">
    {SITE_NAV}
    <div class="hero-copy container"><p class="eyebrow light">Продукція VIKTOR &amp; K</p><h1>Каталог продукції</h1><p>Асортимент VIRA для міжнародних ринків</p></div></div></div>
  <main id="main" class="catalog-surface"><div class="container">
    <nav class="breadcrumbs" aria-label="Навігація"><a href="/">Головна</a><span aria-hidden="true">/</span>{catalog_crumb}</nav>
    <div class="catalog-layout">{navigation(selected)}<section class="catalog-content" aria-label="{esc(label)}">{content(category)}</section></div>
  </div></main>
  {SITE_FOOTER}
  {MOBILE_MENU}
  {MENU_SCRIPT}
</body></html>
'''


def main():
    ids = set()
    for c in CATEGORIES:
        d = OUT / c['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(page(c), encoding='utf-8')
        for item in c['products']:
            if item[0] in ids:
                raise SystemExit(f'Duplicate product ID: {item[0]}')
            ids.add(item[0])
            if not (OUT / 'assets' / 'products' / f'{item[0]}.{item[2]}').exists():
                raise SystemExit(f'Missing image: {item[0]}.{item[2]}')
    (OUT / 'index.html').write_text(page(), encoding='utf-8')
    print(f'Built {len(CATEGORIES) + 1} catalog pages and {len(ids)} product cards.')


main()
