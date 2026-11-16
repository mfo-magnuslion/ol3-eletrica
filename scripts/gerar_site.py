#!/usr/bin/env python3
"""Gera o site da OL3 Elétrica (HTML estático).

- index.html: página principal (página de vendas para o Google Ads)
- eletricista-<cidade>/index.html: uma página por cidade principal
- sitemap.xml e robots.txt

Para mudar telefone, cidades ou o endereço do site (ex.: quando o domínio
próprio estiver pronto), edite as constantes abaixo e rode:
    python3 scripts/gerar_site.py
"""
import html
import json
from pathlib import Path
from urllib.parse import quote

SITE_URL = "https://ol3-eletrica.vercel.app/"
ROOT = Path(__file__).resolve().parent.parent

NOME = "OL3 Elétrica"
WHATSAPP = "5511972360424"
TELEFONE_VISIVEL = "(11) 97236-0424"
TELEFONE_SCHEMA = "+55-11-97236-0424"
CNPJ = ""  # preencher quando confirmado; vazio = não aparece no rodapé
PAGAMENTO = "Crédito, débito, Pix e dinheiro"
ANALYTICS = '<script defer src="/_vercel/insights/script.js"></script>'
MEDICAO = '<script defer src="/assets/medicao.js"></script>'
HORARIO_SCHEMA = {"@type": "OpeningHoursSpecification",
                  "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                  "opens": "00:00", "closes": "23:59"}

# Ordem = da mais próxima para a mais distante de Jandira.
CIDADES = [
    {"nome": "Jandira", "slug": "jandira", "pagina": True, "tempo": None,
     "intro": "Jandira é a base da OL3. É onde chegamos mais rápido, inclusive nas emergências.",
     "detalhe": "Atendemos todos os bairros de Jandira, em casas, apartamentos e comércios."},
    {"nome": "Barueri", "slug": "barueri", "pagina": True, "tempo": "10 minutos",
     "intro": "Barueri faz divisa com Jandira, então o deslocamento é curto.",
     "detalhe": "Atendemos todo o município, incluindo Alphaville e Tamboré, em casas, apartamentos e comércios."},
    {"nome": "Itapevi", "slug": "itapevi", "pagina": True, "tempo": "10 minutos",
     "intro": "Itapevi faz divisa com Jandira, então o deslocamento é curto.",
     "detalhe": "Atendemos todos os bairros de Itapevi, em casas, apartamentos e comércios."},
    {"nome": "Carapicuíba", "slug": "carapicuiba", "pagina": True, "tempo": "15 minutos",
     "intro": "Carapicuíba fica a poucos minutos de Jandira.",
     "detalhe": "Atendemos todos os bairros de Carapicuíba, em casas, apartamentos e comércios."},
    {"nome": "Santana de Parnaíba", "slug": "santana-de-parnaiba", "pagina": True, "tempo": "20 minutos",
     "intro": "Chegamos a Santana de Parnaíba pela Castello Branco.",
     "detalhe": "Atendemos o município, incluindo os residenciais de Alphaville."},
    {"nome": "Osasco", "slug": "osasco", "pagina": True, "tempo": "20 minutos",
     "intro": "Chegamos a Osasco pela Castello Branco.",
     "detalhe": "Atendemos todos os bairros de Osasco, em casas, apartamentos e comércios."},
    {"nome": "Cotia", "slug": "cotia", "pagina": True, "tempo": "20 minutos",
     "intro": "Cotia fica a cerca de 20 minutos de Jandira.",
     "detalhe": "Atendemos o município, incluindo a Granja Viana."},
    {"nome": "Araçariguama", "slug": "aracariguama", "pagina": False},
    {"nome": "Vargem Grande Paulista", "slug": "vargem-grande-paulista", "pagina": False},
    {"nome": "São Paulo", "slug": "sao-paulo", "pagina": True, "tempo": "25 a 30 minutos",
     "intro": "Atendemos a capital. A zona oeste (Butantã, Jaguaré, Rio Pequeno e Lapa) fica a cerca de 25 a 30 minutos de Jandira.",
     "detalhe": "Para outras regiões da cidade, consulte a disponibilidade pelo WhatsApp."},
    {"nome": "Embu das Artes", "slug": "embu-das-artes", "pagina": False},
    {"nome": "Taboão da Serra", "slug": "taboao-da-serra", "pagina": False},
    {"nome": "Cajamar", "slug": "cajamar", "pagina": False},
    {"nome": "Pirapora do Bom Jesus", "slug": "pirapora-do-bom-jesus", "pagina": False},
    {"nome": "São Roque", "slug": "sao-roque", "pagina": False},
    {"nome": "Itapecerica da Serra", "slug": "itapecerica-da-serra", "pagina": False},
]

SERVICOS = [
    {"id": "quadro", "titulo": "Quadro de Distribuição", "arte": "quadro",
     "paragrafos": [
         "É no quadro que ficam os disjuntores que protegem cada circuito do imóvel. Quando ele está velho, mal dimensionado ou desorganizado, aparecem os disjuntores que desarmam sozinhos, os fios aquecendo e o risco de curto.",
         "Montamos quadros novos, trocamos disjuntores, instalamos DR e DPS e separamos os circuitos sobrecarregados. No final, tudo fica identificado para você saber exatamente o que cada disjuntor liga.",
     ],
     "tags": ["Quadro novo", "Disjuntores", "DR e DPS", "Divisão de circuitos"],
     "wa": "Olá! Quero um orçamento para quadro de distribuição."},
    {"id": "gerais", "titulo": "Serviços Gerais", "arte": "gerais",
     "paragrafos": [
         "Tomada que não funciona, ponto de luz novo, chuveiro queimando a resistência, ventilador de teto para instalar: são os serviços do dia a dia que pedem um eletricista de confiança.",
         "Fazemos desde o pequeno reparo até a instalação elétrica completa, em casas, apartamentos, comércios e condomínios, sempre com material adequado, cuidado com o acabamento e o local limpo ao terminar.",
     ],
     "tags": ["Tomadas e interruptores", "Iluminação e LED", "Chuveiro", "Troca de fiação", "Padrão e aterramento"],
     "wa": "Olá! Quero um orçamento de serviço elétrico."},
]

PERGUNTAS = [
    ("Vocês atendem à noite e no fim de semana?",
     "Sim. Atendemos 24 horas, inclusive no fim de semana. Em emergência, chame no WhatsApp e conte o que aconteceu."),
    ("Como é feito o orçamento?",
     "Pelo WhatsApp. Conte o que precisa e mande fotos do local ou do quadro. Para serviços maiores, agendamos uma visita."),
    ("Quais as formas de pagamento?", "Cartão de crédito, cartão de débito, Pix e dinheiro."),
]


def pasta(c):
    return f"eletricista-{c['slug']}"


def wa(texto):
    return f"https://wa.me/{WHATSAPP}?text={quote(texto)}"


def esc(t):
    return html.escape(t, quote=True)


def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"


EMPRESA_ID = SITE_URL + "#empresa"


def empresa_schema():
    e = {
        "@context": "https://schema.org",
        "@type": "Electrician",
        "@id": EMPRESA_ID,
        "name": NOME,
        "description": "Eletricista 24 horas em Jandira e região: quadro de distribuição e serviços elétricos em casas, comércios e prédios.",
        "url": SITE_URL,
        "logo": SITE_URL + "favicon.svg",
        "image": SITE_URL + "assets/og-image.jpg",
        "telephone": TELEFONE_SCHEMA,
        "address": {"@type": "PostalAddress", "addressLocality": "Jandira", "addressRegion": "SP", "addressCountry": "BR"},
        "areaServed": [{"@type": "City", "name": c["nome"]} for c in CIDADES],
        "paymentAccepted": "Cartão de crédito, cartão de débito, Pix, dinheiro",
        "openingHoursSpecification": HORARIO_SCHEMA,
        "contactPoint": {"@type": "ContactPoint", "telephone": TELEFONE_SCHEMA, "contactType": "customer service",
                         "availableLanguage": "Portuguese", "contactOption": "WhatsApp"},
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["titulo"]}} for s in SERVICOS],
    }
    if CNPJ:
        e["taxID"] = CNPJ
    return e


def faq_schema(perguntas):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in perguntas],
    }


RAIO = "M37 4 13 37h16l-4 23 26-35H35z"
WA_PATH = ('<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2.1 1-2.4c.3-.3.6-.3.8-.3h.6c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.4.6-.4.5c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l2 1c.3.1.5.2.5.3.1.2.1.7-.1 1.3z" fill="currentColor"/>')


def icone_wa(tam=20):
    return f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" aria-hidden="true">{WA_PATH}</svg>'


def marca(tam=26):
    return f'<svg width="{tam}" height="{tam}" viewBox="0 0 64 64" aria-hidden="true"><path d="{RAIO}" fill="#FACC15"/></svg>'


def raio_fundo():
    return f'<svg class="hero-bolt" viewBox="0 0 64 64" aria-hidden="true"><path d="{RAIO}" fill="#fff"/></svg>'


ARTE = {
    # Ilustração: quadro de distribuição aberto com fileiras de disjuntores
    "quadro": """<svg viewBox="0 0 570 280" role="img" aria-label="Ilustração de quadro de distribuição">
  <rect width="570" height="280" fill="#E9ECF5"/>
  <rect x="175" y="22" width="220" height="236" rx="10" fill="#C9CEDD"/>
  <rect x="187" y="34" width="196" height="212" rx="6" fill="#F7F8FB"/>
  <g fill="#0F1B4C">
    <rect x="203" y="54" width="164" height="10" rx="3"/><rect x="203" y="118" width="164" height="10" rx="3"/><rect x="203" y="182" width="164" height="10" rx="3"/>
  </g>
  <g fill="#fff" stroke="#9AA2BA" stroke-width="2">
    <rect x="207" y="68" width="22" height="40" rx="3"/><rect x="235" y="68" width="22" height="40" rx="3"/><rect x="263" y="68" width="22" height="40" rx="3"/><rect x="291" y="68" width="22" height="40" rx="3"/><rect x="319" y="68" width="44" height="40" rx="3"/>
    <rect x="207" y="132" width="22" height="40" rx="3"/><rect x="235" y="132" width="22" height="40" rx="3"/><rect x="263" y="132" width="22" height="40" rx="3"/><rect x="291" y="132" width="22" height="40" rx="3"/><rect x="319" y="132" width="22" height="40" rx="3"/><rect x="347" y="132" width="16" height="40" rx="3"/>
    <rect x="207" y="196" width="44" height="40" rx="3"/><rect x="257" y="196" width="22" height="40" rx="3"/><rect x="285" y="196" width="22" height="40" rx="3"/><rect x="313" y="196" width="22" height="40" rx="3"/>
  </g>
  <g fill="#0F1B4C"><rect x="214" y="78" width="8" height="12" rx="2"/><rect x="242" y="78" width="8" height="12" rx="2"/><rect x="270" y="78" width="8" height="12" rx="2"/><rect x="298" y="78" width="8" height="12" rx="2"/><rect x="214" y="142" width="8" height="12" rx="2"/><rect x="242" y="142" width="8" height="12" rx="2"/><rect x="270" y="142" width="8" height="12" rx="2"/><rect x="298" y="142" width="8" height="12" rx="2"/><rect x="326" y="142" width="8" height="12" rx="2"/><rect x="264" y="206" width="8" height="12" rx="2"/><rect x="292" y="206" width="8" height="12" rx="2"/><rect x="320" y="206" width="8" height="12" rx="2"/></g>
  <g fill="#E3141B"><rect x="328" y="76" width="26" height="14" rx="2"/><rect x="214" y="204" width="30" height="14" rx="2"/></g>
  <g fill="none" stroke-width="5" stroke-linecap="round"><path d="M120 280c0-60 30-80 60-90" stroke="#2F6FDB"/><path d="M95 280c0-70 40-100 82-110" stroke="#E3141B"/><path d="M70 280c0-80 50-120 107-130" stroke="#25A244"/><path d="M450 280c0-60-30-80-58-90" stroke="#FACC15"/><path d="M475 280c0-70-40-100-80-110" stroke="#0F1B4C"/></g>
  <circle cx="470" cy="70" r="34" fill="#0F1B4C"/><path d="M475 46 458 74h12l-3 20 18-27h-12z" fill="#FACC15"/>
</svg>""",
    # Ilustração: lâmpada, tomada e ferramentas
    "gerais": """<svg viewBox="0 0 570 280" role="img" aria-label="Ilustração de lâmpada, tomada e ferramentas">
  <rect width="570" height="280" fill="#E9ECF5"/>
  <g transform="translate(110 30)">
    <circle cx="70" cy="80" r="62" fill="#FACC15"/>
    <circle cx="70" cy="80" r="80" fill="none" stroke="#FACC15" stroke-width="4" stroke-dasharray="8 14" opacity=".7"/>
    <rect x="46" y="140" width="48" height="16" rx="4" fill="#9AA2BA"/><rect x="50" y="160" width="40" height="12" rx="4" fill="#7D86A1"/><rect x="58" y="176" width="24" height="10" rx="4" fill="#0F1B4C"/>
    <path d="M55 120c0-18-10-22-10-40a25 25 0 0 1 50 0c0 18-10 22-10 40" fill="none" stroke="#B88A00" stroke-width="4" stroke-linecap="round"/>
  </g>
  <g transform="translate(300 52)">
    <rect width="150" height="150" rx="18" fill="#fff" stroke="#C9CEDD" stroke-width="3"/>
    <circle cx="75" cy="75" r="46" fill="#F1F3F8" stroke="#C9CEDD" stroke-width="3"/>
    <rect x="52" y="56" width="10" height="26" rx="5" fill="#0F1B4C"/><rect x="88" y="56" width="10" height="26" rx="5" fill="#0F1B4C"/><circle cx="75" cy="98" r="6" fill="#0F1B4C"/>
  </g>
  <g transform="translate(470 120) rotate(35)"><rect x="-6" y="-70" width="12" height="80" rx="3" fill="#9AA2BA"/><rect x="-14" y="10" width="28" height="70" rx="10" fill="#E3141B"/></g>
  <g transform="translate(80 230) rotate(-20)"><rect width="110" height="14" rx="7" fill="#0F1B4C"/><rect x="100" y="-6" width="26" height="26" rx="6" fill="#FACC15"/></g>
</svg>""",
}

RELOGIO = """<svg class="clock" viewBox="0 0 260 260" role="img" aria-label="Atendimento 24 horas">
  <g stroke="#1D2433" stroke-width="6" stroke-linecap="round">
    <path d="M130 8v26M130 226v26M8 130h26M226 130h26M44 44l18 18M198 198l18 18M44 216l18-18"/>
  </g>
  <path d="M206 92a84 84 0 1 0 6 70" fill="none" stroke="#E3141B" stroke-width="16" stroke-linecap="round"/>
  <path d="M188 52l40 24-44 18z" fill="#E3141B"/>
  <text x="130" y="152" text-anchor="middle" font-family="Montserrat, Arial Black, sans-serif" font-weight="800" font-size="70" fill="#E3141B" font-style="italic">24h</text>
</svg>"""

HERO_ARTE = f"""<svg class="hero-art" viewBox="0 0 420 340" aria-hidden="true">
  <circle cx="210" cy="170" r="150" fill="rgba(255,255,255,.06)"/>
  <circle cx="210" cy="170" r="110" fill="rgba(255,255,255,.08)"/>
  <circle cx="210" cy="170" r="74" fill="#E3141B"/>
  <g transform="translate(166 120) scale(1.4)"><path d="{RAIO}" fill="#FACC15"/></g>
  <g fill="#fff"><rect x="40" y="70" width="70" height="40" rx="10"/><rect x="296" y="230" width="108" height="40" rx="10"/></g>
  <text x="75" y="96" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="16" fill="#0F1B4C">24h</text>
  <text x="350" y="256" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="14" fill="#25A244">WhatsApp</text>
</svg>"""

MENU = [("inicio", "Home"), ("quem-somos", "Quem somos"), ("servicos", "Serviços"), ("contato", "Contato")]


def head(titulo, descricao, url, og_titulo, prefixo, extras):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descricao)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(og_titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="OL3 Elétrica: eletricista 24 horas em Jandira e região">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{NOME}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F1B4C">
<link rel="icon" href="{prefixo}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&amp;family=Open+Sans:wght@400;600;700&amp;display=swap">
<link rel="stylesheet" href="{prefixo}assets/site.css">
{extras}
</head>
<body>
"""


def cabecalho(prefixo, texto_wa):
    base = prefixo  # "" na home, "../" nas cidades
    nav = "\n".join(f'      <a href="{base}#{a}">{t}</a>' for a, t in MENU)
    return f"""
<div class="topline">
  <div class="wrap">
    <span class="city">Eletricista 24 horas · Jandira e região</span>
    <a href="{wa(texto_wa)}">{TELEFONE_VISIVEL}</a>
  </div>
</div>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{base or '#inicio'}" aria-label="OL3 Elétrica, início">
      <span class="brand-mark">{marca()}</span>
      <span class="brand-name"><b>OL3</b><small>ELÉTRICA</small></span>
    </a>
    <nav class="nav" aria-label="Principal">
{nav}
      <a class="pill pill--red" href="{wa('Olá! Preciso de atendimento 24 horas.')}">Atendimento 24h</a>
    </nav>
    <a class="pill pill--red menu-btn" href="{wa('Olá! Preciso de atendimento 24 horas.')}">Atendimento 24h</a>
  </div>
</header>
"""


def cards(cidade=None):
    out = []
    for s in SERVICOS:
        texto = s["wa"] if not cidade else s["wa"].replace("orçamento", f"orçamento em {cidade}", 1)
        pars = "\n".join(f"        <p>{esc(p)}</p>" for p in s["paragrafos"])
        tags = "".join(f"<li>{esc(t)}</li>" for t in s["tags"])
        out.append(f"""    <article class="card" id="{s['id']}">
      <h3>{esc(s['titulo'])}</h3>
      <div class="card-art">{ARTE[s['arte']]}</div>
      <div class="card-body">
{pars}
        <ul>{tags}</ul>
      </div>
      <a class="card-cta" href="{wa(texto)}">Pedir orçamento</a>
    </article>""")
    return "\n".join(out)


def bloco_24h(texto_wa, cidade=None):
    onde = f"em {cidade}" if cidade else "em Jandira e região"
    return f"""<section class="band24" id="emergencia">
  {raio_fundo()}
  <div class="wrap">
    <h2>Precisa de Eletricista 24 Horas {esc(onde)}?</h2>
    <p class="sub">Emergência elétrica não escolhe hora. A OL3 atende de dia, de noite e no fim de semana.</p>
  </div>
</section>

<section class="urgent">
  <div class="wrap">
    {RELOGIO}
    <div class="lines">
      <p>Faltou energia de repente, apareceram faíscas ou está sentindo cheiro de queimado? Não espere o problema piorar.</p>
      <p>Mexer no quadro ou em fios sem preparo expõe você a choque elétrico e a risco de incêndio.</p>
      <p>Nosso eletricista vai até você, encontra a causa e deixa a instalação segura de novo, com rapidez.</p>
      <p>Desligue o disjuntor geral, se puder, e fale com a OL3 agora mesmo.</p>
      <a class="btn-whats" href="{wa(texto_wa)}">{icone_wa()}Chame pelo WhatsApp</a>
    </div>
  </div>
</section>"""


def bloco_areas(prefixo, excluir=None, titulo="Onde atendemos"):
    itens = []
    for c in CIDADES:
        if c is excluir:
            continue
        if c["pagina"]:
            itens.append(f'<li><a href="{prefixo}{pasta(c)}/">{esc(c["nome"])}</a></li>')
        else:
            itens.append(f"<li>{esc(c['nome'])}</li>")
    return f"""<section class="areas" id="regioes">
  <div class="wrap">
    <h2>{esc(titulo)}</h2>
    <p>Jandira e cidades vizinhas, até 30 km. Não achou a sua? <a href="{wa('Olá! Vocês atendem na minha cidade?')}">Pergunte no WhatsApp</a>.</p>
    <ul class="chips">{''.join(itens)}</ul>
  </div>
</section>"""


def rodape(prefixo, texto_wa):
    base = prefixo
    menu = "".join(f'<li><a href="{base}#{a}">{t}</a></li>' for a, t in MENU[:3])
    menu += f'<li><a href="{base}#quadro">Quadro de Distribuição</a></li><li><a href="{base}#gerais">Serviços Gerais</a></li>'
    menu += f'<li><a href="{base}#regioes">Onde atendemos</a></li><li><a href="{base}#contato">Contato</a></li>'
    cnpj = f" · CNPJ {CNPJ}" if CNPJ else ""
    return f"""
<section class="contact" id="contato">
  <div class="wrap">
    <div>
      <h2>Fale com a OL3 Elétrica</h2>
      <p>Mande sua mensagem e receba o orçamento sem compromisso.</p>
    </div>
    <a class="btn-box" href="{wa(texto_wa)}">Envie sua Mensagem</a>
  </div>
</section>

<footer>
  <div class="wrap foot">
    <div>
      <h3>Entre em contato</h3>
      <dl>
        <div><dt>Atendimento:</dt><dd><a href="{wa(texto_wa)}">{TELEFONE_VISIVEL}</a></dd></div>
        <div><dt>WhatsApp:</dt><dd><a href="{wa(texto_wa)}">{TELEFONE_VISIVEL}</a></dd></div>
        <div><dt>Horário:</dt><dd>24 horas, todos os dias</dd></div>
      </dl>
    </div>
    <div>
      <h3>Menu</h3>
      <ul>{menu}</ul>
    </div>
    <div class="foot-brand">
      <span class="brand"><span class="brand-mark">{marca(30)}</span><span class="brand-name"><b>OL3</b><small>ELÉTRICA</small></span></span>
      <a class="btn-box" href="{wa('Olá! Quero solicitar um orçamento.')}">Solicitar um Orçamento</a>
    </div>
  </div>
  <div class="copy">
    <div class="wrap"><span>© 2026 {NOME}. Todos os direitos reservados{cnpj}.</span><span>Jandira · SP</span></div>
  </div>
</footer>

<a class="float" href="{wa(texto_wa)}" aria-label="Falar com a OL3 Elétrica no WhatsApp"><span>Clique aqui e envie<br>sua mensagem</span><i>{icone_wa(32).replace('aria-hidden="true"', 'aria-hidden="true" style="color:#fff"')}</i></a>
{ANALYTICS}
{MEDICAO}
</body>
</html>
"""


def pagina_home():
    texto_wa = "Olá! Vim pelo site e preciso de um eletricista."
    titulo = "Eletricista 24h em Jandira e Região | OL3 Elétrica"
    descricao = ("Eletricista 24 horas em Jandira, Barueri, Itapevi, Osasco, Cotia e região. Quadro de distribuição "
                 "e serviços elétricos em casas, comércios e prédios. Orçamento no WhatsApp.")
    extras = jsonld(empresa_schema()) + "\n" + jsonld(faq_schema(PERGUNTAS))
    return head(titulo, descricao, SITE_URL, "OL3 Elétrica: eletricista 24h em Jandira e região", "", extras) + cabecalho("", texto_wa) + f"""
<main>

<section class="hero" id="inicio">
  {raio_fundo()}
  <div class="wrap">
    <div>
      <h1>Eletricista 24 horas <span>em Jandira e região</span></h1>
      <p>Casas, comércios e prédios. Do reparo rápido à instalação completa, com segurança e orçamento pelo WhatsApp.</p>
      <div class="actions">
        <a class="btn-whats" href="{wa(texto_wa)}">{icone_wa()}Chame pelo WhatsApp</a>
        <a class="btn-line" href="#servicos">Nossos serviços</a>
      </div>
    </div>
    {HERO_ARTE}
  </div>
</section>

<section class="intro" id="quem-somos">
  <div class="wrap">
    <div class="intro-head">
      <h2>OL3 Elétrica<br>Jandira e Região</h2>
      <p>Cuidamos da parte elétrica de residências, lojas e condomínios, do conserto pontual ao projeto mais completo.</p>
      <p>Trabalhamos com segurança, rapidez e soluções que resolvem de vez, para a sua instalação funcionar sem sustos.</p>
    </div>
    <div class="cards" id="servicos">
{cards()}
    </div>
  </div>
</section>

{bloco_24h("Olá! Estou com uma emergência elétrica e preciso de atendimento.")}

{bloco_areas("")}

</main>
""" + rodape("", texto_wa)


def pagina_cidade(c):
    nome = c["nome"]
    url = SITE_URL + pasta(c) + "/"
    texto_wa = f"Olá! Preciso de um eletricista em {nome}."
    distancia = (f"Ficamos a cerca de {c['tempo']} de {nome}." if c["tempo"]
                 else "Jandira é a nossa base, então chegamos rápido.")
    titulo = f"Eletricista em {nome} 24h | OL3 Elétrica"
    descricao = (f"Eletricista 24 horas em {nome}: quadro de distribuição e serviços elétricos em casas, "
                 "comércios e prédios. Orçamento sem compromisso no WhatsApp.")
    perguntas = [(f"Vocês atendem em {nome}?", f"Sim. {c['detalhe']} {distancia}")] + PERGUNTAS
    servico = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"Eletricista em {nome}",
        "serviceType": "Serviços elétricos residenciais e comerciais",
        "provider": {"@id": EMPRESA_ID, "@type": "Electrician", "name": NOME, "telephone": TELEFONE_SCHEMA, "url": SITE_URL},
        "areaServed": {"@type": "City", "name": nome},
        "hoursAvailable": HORARIO_SCHEMA,
        "url": url,
    }
    trilha = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": f"Eletricista em {nome}", "item": url},
        ],
    }
    extras = "\n".join([jsonld(servico), jsonld(trilha), jsonld(faq_schema(perguntas))])
    return head(titulo, descricao, url, f"Eletricista em {nome} | OL3 Elétrica", "../", extras) + cabecalho("../", texto_wa) + f"""
<main>

<section class="hero" id="inicio">
  {raio_fundo()}
  <div class="wrap">
    <div>
      <nav class="crumbs" aria-label="Você está em"><a href="../">Início</a> / {esc(nome)}</nav>
      <h1>Eletricista 24 horas <span>em {esc(nome)}</span></h1>
      <p>{esc(c['intro'])} Atendemos casas, comércios e prédios, com orçamento pelo WhatsApp.</p>
      <div class="actions">
        <a class="btn-whats" href="{wa(texto_wa)}">{icone_wa()}Chame pelo WhatsApp</a>
        <a class="btn-line" href="#servicos">Nossos serviços</a>
      </div>
    </div>
    {HERO_ARTE}
  </div>
</section>

<section class="intro" id="quem-somos">
  <div class="wrap">
    <div class="intro-head">
      <h2>OL3 Elétrica<br>{esc(nome)}</h2>
      <p>{esc(c['detalhe'])} {esc(distancia)}</p>
      <p>Trabalhamos com segurança, rapidez e soluções que resolvem de vez, para a sua instalação funcionar sem sustos.</p>
    </div>
    <div class="cards" id="servicos">
{cards(nome)}
    </div>
  </div>
</section>

{bloco_24h(f"Olá! Estou com uma emergência elétrica em {nome}.", nome)}

{bloco_areas("../", excluir=c, titulo="Também atendemos")}

</main>
""" + rodape("../", texto_wa)


def main():
    (ROOT / "index.html").write_text(pagina_home(), encoding="utf-8")
    urls = [SITE_URL]
    for c in CIDADES:
        if not c["pagina"]:
            continue
        destino = ROOT / pasta(c)
        destino.mkdir(exist_ok=True)
        (destino / "index.html").write_text(pagina_cidade(c), encoding="utf-8")
        urls.append(SITE_URL + pasta(c) + "/")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    print(f"{len(urls)} páginas no sitemap")


if __name__ == "__main__":
    main()
