"""Gera o site estático (raiz do repositório) a partir das páginas em _build/source.

Uso: python3 _build/export.py [pasta_extra_de_assets ...]
Os assets (/_blob/<id>) são procurados em assets/ e nas pastas extras passadas.
"""
import re, os, sys, glob, shutil, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_build', 'source')
ASSETS = os.path.join(ROOT, 'assets')

names = {'Main': 'index', 'OQueFazemos': 'o-que-fazemos', 'Projetos': 'projetos', 'Palestras': 'palestras',
         'Sobre': 'sobre', 'Contato': 'contato', 'CaseCannes': 'case-cannes', 'CaseEli': 'case-eli-summit',
         'CaseCidade': 'case-cidade-no-cinema', 'CaseRio': 'case-rio-em-cena', 'CaseRecentro': 'case-recentro',
         'CaseJaboatao': 'case-jaboatao'}

# índice de assets disponíveis: id -> caminho
pool = {}
for d in [ASSETS] + sys.argv[1:]:
    for f in glob.glob(os.path.join(d, '*')):
        pool.setdefault(os.path.basename(f).split('.')[0], f)

GX = open(os.path.join(ROOT, '_build', 'gx.js')).read().strip()
DESC = ('Drops and People: projetos de cultura, turismo e educação. Roteiros e experiências turísticas, '
        'curadoria de eventos, imersões e palestras, do planejamento à entrega.')

JS = '''<script>
(function(){
  var cur=document.querySelector('.cur');
  if(cur){document.addEventListener('mousemove',function(e){cur.style.transform='translate('+e.clientX+'px,'+e.clientY+'px)';});}
  document.querySelectorAll('.car-track').forEach(function(t){
    var d=null,moved=false;
    t.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;d={x:e.clientX,s:t.scrollLeft,m:false};});
    t.addEventListener('pointermove',function(e){if(!d)return;var dx=e.clientX-d.x;if(Math.abs(dx)>5){d.m=true;t.classList.add('dragging');}t.scrollLeft=d.s-dx;});
    function up(){if(!d)return;t.classList.remove('dragging');moved=d.m;d=null;}
    t.addEventListener('pointerup',up);t.addEventListener('pointerleave',up);
    t.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation();moved=false;}},true);
  });
  document.querySelectorAll('[data-car]').forEach(function(b){
    b.addEventListener('click',function(){var t=b.closest('.car').querySelector('.car-track');var step=+b.getAttribute('data-step')||320;t.scrollBy({left:b.getAttribute('data-car')==='prev'?-step:step,behavior:'smooth'});});
  });
  document.querySelectorAll('[data-play]').forEach(function(b){b.addEventListener('click',function(){var c=b.closest('.vidcard'),v=c.querySelector('video');v.controls=true;v.play();c.classList.add('playing');});});
  var GX=__GX__;
  document.querySelectorAll('.galx').forEach(function(el){['pointerenter','pointerleave','pointerdown','pointermove','pointerup','pointercancel','scroll'].forEach(function(t){el.addEventListener(t,function(e){GX(el,e);});});GX(el,{type:'init'});});
  var np=document.querySelector('.netpanel');
  document.querySelectorAll('[data-net-toggle]').forEach(function(b){b.addEventListener('click',function(){if(!np)return;var o=!np.classList.contains('open');np.classList.toggle('open',o);np.setAttribute('aria-hidden',o?'false':'true');document.querySelectorAll('button.mem[data-net-toggle]').forEach(function(x){x.setAttribute('aria-expanded',o?'true':'false');});});});
  var fb=document.querySelectorAll('.fbtn[data-f]');
  if(fb.length){
    var cards=document.querySelectorAll('.card[data-k]'),count=document.querySelector('.count');
    fb.forEach(function(b){b.addEventListener('click',function(){
      var f=b.getAttribute('data-f'),n=0;
      fb.forEach(function(x){var on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on?'true':'false');});
      cards.forEach(function(c){var show=f==='todos'||c.getAttribute('data-k').split(' ').indexOf(f)!==-1;c.hidden=!show;if(show)n++;});
      if(count)count.textContent=n+(n===1?' projeto':' projetos');
    });});
  }
})();
</script>'''.replace('__GX__', GX)


def js_objects(src):
    """Converte o array `all` (objetos JS simples) em dicts Python."""
    arr = re.search(r'const all = \[(.*?)\n\s*\];', src, re.S).group(1)
    out = []
    for obj in re.findall(r'\{(.*?)\}\s*(?:,|$)', arr, re.S):
        d = {}
        for k, v in re.findall(r"(\w+):\s*(\[[^\]]*\]|'(?:[^'\\]|\\.)*')", obj):
            d[k] = re.findall(r"'([^']*)'", v) if v.startswith('[') else v[1:-1].replace("\\'", "'")
        out.append(d)
    return out


def projetos(body, script):
    items = js_objects(script)
    defs = re.search(r'const defs = \[(.*?)\];', script, re.S).group(1)
    defs = re.findall(r"\['(\w+)', '([^']*)'\]", defs)
    btns = ''.join(
        f'<button type="button" class="fbtn{" on" if k == "todos" else ""}" data-f="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{html.escape(l)}</button>'
        for k, l in defs)
    body = re.sub(r'<sc-for list="\{\{filters\}\}".*?</sc-for>', btns, body, flags=re.S)
    tpl = re.search(r'<sc-for list="\{\{visible\}\}"[^>]*>(.*?)</sc-for>', body, re.S).group(1)
    cards = ''
    for p in items:
        c = tpl.replace('<a class="card pop" href', f'<a class="card pop" data-k="{" ".join(p["k"])}" href')
        for k, v in p.items():
            if k != 'k':
                c = c.replace('{{p.' + k + '}}', html.escape(v, quote=True))
        cards += c
    body = re.sub(r'<sc-for list="\{\{visible\}\}".*?</sc-for>', lambda m: cards, body, flags=re.S)
    return body.replace('{{countLabel}}', f'{len(items)} projetos')


used = set()
for f in sorted(glob.glob(os.path.join(SRC, '*.dc.html'))):
    base = os.path.basename(f)[:-8]
    s = open(f).read()
    title = re.search(r'<title>(.*?)</title>', s).group(1)
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
    body = re.search(r'</helmet>(.*?)</x-dc>', s, re.S).group(1)
    script = re.search(r'<script type="text/x-dc".*?</script>', s, re.S).group(0)
    if '<sc-for' in body:
        body = projetos(body, script)
    step = re.search(r'scrollBy\(\{ left: -(\d+)', script)
    step = step.group(1) if step else '320'
    body = re.sub(r'onClick="\{\{prev\}\}"', f'data-car="prev" data-step="{step}"', body)
    body = re.sub(r'onClick="\{\{next\}\}"', f'data-car="next" data-step="{step}"', body)
    body = (body.replace('onClick="{{toggleNet}}"', 'data-net-toggle').replace('{{netCls}}', '')
            .replace('{{netExp}}', 'false').replace('{{netHidden}}', 'true')
            .replace('onClick="{{playVid}}"', 'data-play').replace('{{vidCls}}', ''))
    body = re.sub(r'\s+on[A-Z]\w*="\{\{[^}]*\}\}"', '', body)
    body = body.replace('{{motionClass}}', '').replace('{{accent}}', '#DF9330').replace('class="dr "', 'class="dr"')
    left = re.findall(r'\{\{[^}]*\}\}', body)
    assert not left, (base, left[:5])
    doc = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{DESC}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="/_blob/020d5c4914f3109a9aa302a75810c413">
<link rel="icon" type="image/png" href="/assets/favicon.png">
{helmet.strip()}
</head>
<body>
{body.strip()}
{JS}
</body>
</html>
'''
    def asset(m):
        i = m.group(1)
        assert i in pool, f'asset ausente: {i} ({base})'
        used.add(i)
        return '/assets/' + os.path.basename(pool[i])
    doc = re.sub(r'/_blob/([0-9a-f]{32})', asset, doc)
    doc = re.sub(r'href="(\w+)\.dc\.html', lambda m: 'href="/' + ('' if names[m.group(1)] == 'index' else names[m.group(1)]), doc)
    open(os.path.join(ROOT, names[base] + '.html'), 'w').write(doc)

# copia assets novos para assets/ e remove os que não são mais usados
os.makedirs(ASSETS, exist_ok=True)
for i in used:
    dst = os.path.join(ASSETS, os.path.basename(pool[i]))
    if os.path.abspath(pool[i]) != os.path.abspath(dst):
        shutil.copy(pool[i], dst)
for f in glob.glob(os.path.join(ASSETS, '*')):
    b = os.path.basename(f)
    if b != 'favicon.png' and b.split('.')[0] not in used:
        os.remove(f)
open(os.path.join(ROOT, 'vercel.json'), 'w').write(json.dumps({"cleanUrls": True, "trailingSlash": False}, indent=2) + '\n')
print(len(used), 'assets usados')
