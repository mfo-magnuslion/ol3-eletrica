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
    {"id": "quadro", "titulo": "Quadro de distribuição",
     "texto": "O quadro controla e protege todos os circuitos do imóvel. Quadro antigo, disjuntor que desarma toda hora ou aquecendo são sinais de que precisa de revisão.",
     "itens": ["Montagem de quadro novo", "Troca de disjuntores", "Instalação de DR e DPS", "Organização e identificação dos circuitos", "Divisão de circuitos sobrecarregados"],
     "wa": "Olá! Quero um orçamento para quadro de distribuição."},
    {"id": "instalacoes", "titulo": "Instalações elétricas",
     "texto": "Do ponto novo à instalação completa da casa ou do comércio, com material adequado e acabamento limpo.",
     "itens": ["Tomadas, interruptores e novos pontos", "Iluminação, spots e fitas de LED", "Chuveiro elétrico e troca de resistência", "Ventilador de teto e luminárias", "Troca de fiação antiga"],
     "wa": "Olá! Quero um orçamento de instalação elétrica."},
    {"id": "reparos", "titulo": "Reparos e emergências",
     "texto": "Falta de energia, curto-circuito, cheiro de queimado ou disjuntor que não volta. Atendemos 24 horas para deixar tudo seguro de novo.",
     "itens": ["Falta de energia em parte da casa", "Curto-circuito e fios aquecendo", "Tomada ou interruptor derretido", "Disjuntor que desarma sem parar", "Localização de defeitos"],
     "wa": "Olá! Preciso de um eletricista para um reparo."},
    {"id": "padrao", "titulo": "Padrão de entrada e aterramento",
     "texto": "Adequação do padrão de energia, aumento de carga e aterramento para proteger pessoas e aparelhos.",
     "itens": ["Padrão de entrada novo ou reforma", "Aumento de carga", "Sistema de aterramento", "Tomadas no padrão de três pinos", "Laudo e revisão da instalação"],
     "wa": "Olá! Quero um orçamento para padrão de entrada ou aterramento."},
]

PERGUNTAS = [
    ("Vocês atendem à noite e no fim de semana?",
     "Sim. Atendemos 24 horas, inclusive no fim de semana. Em emergência, chame no WhatsApp e conte o que aconteceu."),
    ("Faltou energia só em parte da casa. O que pode ser?",
     "Normalmente é um disjuntor desarmado, um DR atuando ou um defeito no circuito. Confira o quadro. Se o disjuntor desarmar de novo ao religar, não insista: há um problema no circuito e é hora de chamar um eletricista."),
    ("Estou sentindo cheiro de queimado. O que eu faço?",
     "Desligue o disjuntor do circuito (ou o geral, se não souber qual é), não mexa em fios e chame um eletricista. Cheiro de queimado indica aquecimento e risco de incêndio."),
    ("O que é DR e DPS? Preciso ter no meu quadro?",
     "O DR desliga o circuito quando há fuga de corrente e protege as pessoas contra choque. O DPS protege os aparelhos contra surtos, como os causados por raios. A norma NBR 5410 exige o DR nas áreas molhadas, e os dois são recomendados para toda casa."),
    ("Vocês atendem comércio e condomínio?",
     "Sim. Atendemos casas, apartamentos, lojas, escritórios e áreas comuns de condomínios."),
    ("Como é feito o orçamento?",
     "Pelo WhatsApp. Conte o que precisa e mande fotos do local ou do quadro. Para serviços maiores, agendamos uma visita. Você só aprova depois de ver o que está incluso."),
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
        "description": "Eletricista 24 horas em Jandira e região: quadro de distribuição, instalações, reparos, padrão de entrada e aterramento, conforme a ABNT NBR 5410.",
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


ICONES = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <symbol id="i-wa" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 1-13.5 7.8L3 21l1.3-4.4A9 9 0 1 1 21 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5" fill="none" stroke="#15803D" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-logo" viewBox="0 0 64 64"><path d="M37 4 13 37h16l-4 23 26-35H35z" fill="#FACC15"/></symbol>
    <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-cal" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></g></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/></g></symbol>
    <symbol id="i-alert" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></g></symbol>
  </defs>
</svg>"""

NAV = [("servicos", "Serviços"), ("emergencia", "Emergência 24h"), ("como-funciona", "Como funciona"),
       ("quem-somos", "Quem somos"), ("regioes", "Onde atendemos"), ("duvidas", "Dúvidas")]

BOLT_BG = '<svg class="hero-flame" viewBox="0 0 64 64" aria-hidden="true"><path d="M37 4 13 37h16l-4 23 26-35H35z"/></svg>'


def check(texto):
    return f'<li><svg width="20" height="20" aria-hidden="true"><use href="#i-check"/></svg>{esc(texto)}</li>'


def wa_icon():
    return '<svg width="20" height="20" aria-hidden="true"><use href="#i-wa"/></svg>'


def tags_compartilhar(alt):
    return (f'<meta property="og:image" content="{SITE_URL}assets/og-image.jpg">\n'
            '<meta property="og:image:width" content="1200">\n'
            '<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{esc(alt)}">\n'
            '<meta property="og:locale" content="pt_BR">\n'
            f'<meta property="og:site_name" content="{NOME}">\n'
            '<meta name="twitter:card" content="summary_large_image">')


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
{tags_compartilhar('OL3 Elétrica: eletricista 24 horas em Jandira e região')}
<meta name="theme-color" content="#12263A">
<link rel="icon" href="{prefixo}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100,700;100,800;100,900;112,800;112,900&amp;family=IBM+Plex+Mono:wght@500&amp;family=Source+Sans+3:wght@400;600;700&amp;display=swap">
<link rel="stylesheet" href="{prefixo}assets/site.css">
{extras}
</head>
<body>

{ICONES}
"""


def cabecalho(prefixo, texto_wa):
    ancora = "" if prefixo == "" else "../"
    nav = "\n".join(f'      <a href="{ancora}#{a}">{t}</a>' for a, t in NAV)
    return f"""
<header class="top">
  <div class="wrap top-bar">
    <a class="brand" href="{prefixo or '#inicio'}" aria-label="OL3 Elétrica, início">
      <span class="brand-mark"><svg width="26" height="26" aria-hidden="true"><use href="#i-logo"/></svg></span>
      <span class="brand-name"><b>OL3</b><small>ELÉTRICA</small></span>
    </a>
    <nav class="nav" aria-label="Principal">
{nav}
    </nav>
    <a class="btn btn--whats" href="{wa(texto_wa)}" aria-label="WhatsApp {TELEFONE_VISIVEL}">
      {wa_icon()}<span>{TELEFONE_VISIVEL}</span>
    </a>
  </div>
  <nav class="subnav" aria-label="Seções">
    <div class="wrap">
{nav}
    </div>
  </nav>
</header>
"""


def rodape(texto_wa):
    legal = f'\n    <span class="legal">CNPJ {CNPJ}</span>' if CNPJ else ""
    return f"""
<footer>
  <div class="wrap foot">
    <span>{NOME} · Eletricista residencial e comercial em Jandira e região</span>
    <a href="https://wa.me/{WHATSAPP}">WhatsApp {TELEFONE_VISIVEL}</a>{legal}
  </div>
</footer>

<a class="float" href="{wa(texto_wa)}" aria-label="Falar com a OL3 Elétrica no WhatsApp"><svg width="30" height="30" aria-hidden="true"><use href="#i-wa"/></svg></a>
<div class="mbar"><a class="btn btn--whats" href="{wa(texto_wa)}">{wa_icon()}Chamar eletricista no WhatsApp · 24h</a></div>
{ANALYTICS}
{MEDICAO}
</body>
</html>
"""


def proof():
    return f"""      <ul class="proof">
        <li><svg width="20" height="20" aria-hidden="true"><use href="#i-bolt"/></svg>Emergência 24 horas</li>
        <li><svg width="20" height="20" aria-hidden="true"><use href="#i-cal"/></svg>Inclusive fim de semana</li>
        <li><svg width="20" height="20" aria-hidden="true"><use href="#i-shield"/></svg>Serviço com garantia</li>
        <li>{wa_icon()}Orçamento sem compromisso</li>
      </ul>"""


def cards_servicos(cidade=None):
    out = []
    for s in SERVICOS:
        texto = s["wa"] if not cidade else s["wa"].replace("orçamento", f"orçamento em {cidade}", 1).replace("eletricista para", f"eletricista em {cidade} para", 1)
        itens = "\n".join("          " + check(i) for i in s["itens"])
        out.append(f"""      <article class="panel" id="{s['id']}">
        <h3>{esc(s['titulo'])}</h3>
        <p class="muted">{esc(s['texto'])}</p>
        <ul class="list">
{itens}
        </ul>
        <a class="btn btn--whats" href="{wa(texto)}">{wa_icon()}Pedir orçamento</a>
      </article>""")
    return "\n".join(out)


def bloco_emergencia(texto_wa):
    return f"""<section id="emergencia" class="band band--dark">
  <div class="wrap">
    <div class="head">
      <span class="label">Emergência 24 horas</span>
      <h2>Faísca, cheiro de queimado ou falta de energia?</h2>
      <p class="lead lead--dark">Não mexa em fios e disjuntores sem preparo: o risco de choque e de incêndio é real. Desligue o disjuntor geral se puder e chame a OL3. Atendemos a qualquer hora, inclusive no fim de semana.</p>
    </div>
    <ul class="symptoms symptoms--dark">
      <li class="symptom"><b>Cheiro de queimado</b><span>Em tomadas, interruptores ou no quadro.</span></li>
      <li class="symptom"><b>Faíscas ou estalos</b><span>Ao ligar um aparelho ou na parede.</span></li>
      <li class="symptom"><b>Disjuntor desarmando</b><span>Desliga de novo logo depois de religar.</span></li>
      <li class="symptom"><b>Choque ao encostar</b><span>Em torneira, chuveiro ou eletrodoméstico.</span></li>
    </ul>
    <div class="actions" style="margin-top:32px">
      <a class="btn btn--flame" href="{wa(texto_wa)}">{wa_icon()}Chamar eletricista agora</a>
    </div>
  </div>
</section>"""


def passos(local="no local"):
    return f"""    <ol class="steps">
      <li class="step"><h3>Chame no WhatsApp</h3><p>Conte o que precisa e mande fotos do local ou do quadro.</p></li>
      <li class="step"><h3>Receba o orçamento</h3><p>Valor claro, com o que está incluso. Em emergência, saímos na hora.</p></li>
      <li class="step"><h3>Serviço {esc(local)}</h3><p>Executamos com segurança, material adequado e testamos cada circuito.</p></li>
      <li class="step"><h3>Pronto e garantido</h3><p>Você recebe as orientações, e o serviço tem garantia.</p></li>
    </ol>"""


def faq_html(perguntas):
    return "\n".join(f"      <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in perguntas)


def chips(prefixo, excluir=None):
    linhas = []
    for c in CIDADES:
        if c is excluir:
            continue
        if c["pagina"]:
            linhas.append(f'      <li><a href="{prefixo}{pasta(c)}/">{esc(c["nome"])}</a></li>')
        else:
            linhas.append(f"      <li>{esc(c['nome'])}</li>")
    return "\n".join(linhas)


def pagina_home():
    texto_wa = "Olá! Vim pelo site e preciso de um eletricista."
    titulo = "Eletricista 24h em Jandira e Região | OL3 Elétrica"
    descricao = ("Eletricista em Jandira, Barueri, Itapevi, Osasco, Cotia e região. Quadro de distribuição, "
                 "instalações, reparos e emergência 24h, inclusive fim de semana. Orçamento no WhatsApp.")
    extras = jsonld(empresa_schema()) + "\n" + jsonld(faq_schema(PERGUNTAS))
    return head(titulo, descricao, SITE_URL, "OL3 Elétrica: eletricista 24h em Jandira e região", "", extras) + cabecalho("", texto_wa) + f"""
<main>

<section id="inicio" class="hero">
  {BOLT_BG}
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <span class="status"><i aria-hidden="true"></i>Eletricista 24 horas · Jandira e região</span>
      <h1>Eletricista para casa e comércio <em>em Jandira e região.</em></h1>
      <p class="lead">Quadro de distribuição, instalações, reparos e emergências. Serviço seguro, conforme a norma ABNT NBR 5410. Você recebe o orçamento pelo WhatsApp e só aprova depois de ver o que está incluso.</p>
      <div class="actions">
        <a class="btn btn--flame" href="{wa(texto_wa)}">{wa_icon()}Pedir orçamento no WhatsApp</a>
        <a class="btn btn--ghost" href="#servicos">Ver serviços</a>
      </div>
{proof()}
    </div>
    <aside class="sheet" aria-label="Resumo do atendimento">
      <div class="sheet-title"><h2>Ficha do atendimento</h2><span class="label">OL3</span></div>
      <dl>
        <div class="row"><dt>Atende</dt><dd>Casas, apartamentos, comércios e condomínios</dd></div>
        <div class="row"><dt>Norma</dt><dd>ABNT NBR 5410</dd></div>
        <div class="row"><dt>Horário</dt><dd>24 horas, inclusive fim de semana</dd></div>
        <div class="row"><dt>Região</dt><dd>Jandira e cidades vizinhas, até 30 km</dd></div>
        <div class="row"><dt>Pagamento</dt><dd>{PAGAMENTO}</dd></div>
      </dl>
    </aside>
  </div>
</section>

<section id="servicos" class="band">
  <div class="wrap">
    <div class="head">
      <span class="label">Serviços</span>
      <h2>Do ponto novo ao quadro completo</h2>
      <p class="lead">Atendemos desde ajustes simples até instalações completas em casas, comércios e prédios.</p>
    </div>
    <div class="grid2">
{cards_servicos()}
    </div>
  </div>
</section>

{bloco_emergencia("Olá! Estou com uma emergência elétrica e preciso de atendimento.")}

<section id="como-funciona" class="band band--mist">
  <div class="wrap">
    <div class="head">
      <span class="label">Como funciona</span>
      <h2>Do primeiro contato à energia de volta</h2>
    </div>
{passos()}
  </div>
</section>

<section id="quem-somos" class="band">
  <div class="wrap about">
    <div class="badge-card">
      <span class="monogram" aria-hidden="true">OL3</span>
      <p><strong>OL3 Elétrica</strong>Da mesma equipe da OL3 Aquecedores, com atendimento direto pelo WhatsApp em Jandira e região.</p>
    </div>
    <div class="about-copy">
      <span class="label">Quem somos</span>
      <h2>Segurança em primeiro lugar em cada serviço</h2>
      <p class="lead">A OL3 Elétrica executa serviços elétricos residenciais e comerciais com foco em segurança, agilidade e acabamento limpo. Explicamos o problema, mostramos a solução e deixamos tudo funcionando.</p>
      <ul class="checks">
        {check('Serviço conforme a NBR 5410')}
        {check('Atendimento 24 horas')}
        {check('Orçamento claro antes de começar')}
        {check('Serviço com garantia')}
      </ul>
    </div>
  </div>
</section>

<section id="regioes" class="band band--dark">
  <div class="wrap regions">
    <div>
      <div class="head">
        <span class="label">Onde atendemos</span>
        <h2>Jandira e região, até 30 km</h2>
      </div>
      <p class="muted">Não achou sua cidade? <a href="{wa('Olá! Vocês atendem na minha cidade?')}">Pergunte no WhatsApp</a>.</p>
    </div>
    <ul class="cities">
{chips('')}
    </ul>
  </div>
</section>

<section id="duvidas" class="band band--mist">
  <div class="wrap faq">
    <div class="head">
      <span class="label">Dúvidas</span>
      <h2>Perguntas frequentes</h2>
    </div>
    <div class="qa">
{faq_html(PERGUNTAS)}
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap cta">
    <div>
      <h2>Precisa de um eletricista?</h2>
      <p class="lead">Atendemos 24 horas, inclusive no fim de semana. Mande uma mensagem e receba o orçamento sem compromisso.</p>
    </div>
    <a class="btn btn--whats" href="{wa(texto_wa)}">{wa_icon()}WhatsApp {TELEFONE_VISIVEL}</a>
  </div>
</section>

</main>
""" + rodape(texto_wa)


def pagina_cidade(c):
    nome = c["nome"]
    url = SITE_URL + pasta(c) + "/"
    texto_wa = f"Olá! Preciso de um eletricista em {nome}."
    distancia = (f"A cerca de {c['tempo']} de Jandira, sem trânsito." if c["tempo"]
                 else "Nossa base: atendimento mais rápido da região.")
    titulo = f"Eletricista em {nome} 24h | OL3 Elétrica"
    descricao = (f"Eletricista em {nome}: quadro de distribuição, instalações, reparos e emergência 24h, "
                 "inclusive fim de semana. Orçamento sem compromisso no WhatsApp.")
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

<section class="hero">
  {BOLT_BG}
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <nav class="crumbs" aria-label="Você está em"><a href="../">Início</a> <span aria-hidden="true">/</span> {esc(nome)}</nav>
      <h1>Eletricista em {esc(nome)}: <em>atendimento 24 horas.</em></h1>
      <p class="lead">{esc(c['intro'])} Quadro de distribuição, instalações, reparos e emergências, com serviço conforme a ABNT NBR 5410.</p>
      <div class="actions">
        <a class="btn btn--flame" href="{wa(texto_wa)}">{wa_icon()}Chamar eletricista em {esc(nome)}</a>
        <a class="btn btn--ghost" href="#servicos">Ver serviços</a>
      </div>
{proof()}
    </div>
    <aside class="sheet" aria-label="Resumo do atendimento em {esc(nome)}">
      <div class="sheet-title"><h2>Atendimento em {esc(nome)}</h2><span class="label">OL3</span></div>
      <dl>
        <div class="row"><dt>Deslocamento</dt><dd>{esc(distancia)}</dd></div>
        <div class="row"><dt>Atende</dt><dd>Casas, apartamentos, comércios e condomínios</dd></div>
        <div class="row"><dt>Norma</dt><dd>ABNT NBR 5410</dd></div>
        <div class="row"><dt>Horário</dt><dd>24 horas, inclusive fim de semana</dd></div>
        <div class="row"><dt>Pagamento</dt><dd>{PAGAMENTO}</dd></div>
      </dl>
    </aside>
  </div>
</section>

<section id="servicos" class="band">
  <div class="wrap">
    <div class="head">
      <span class="label">Serviços em {esc(nome)}</span>
      <h2>O que fazemos em {esc(nome)}</h2>
      <p class="lead">{esc(c['detalhe'])}</p>
    </div>
    <div class="grid2">
{cards_servicos(nome)}
    </div>
  </div>
</section>

{bloco_emergencia(f"Olá! Estou com uma emergência elétrica em {nome}.")}

<section id="como-funciona" class="band band--mist">
  <div class="wrap">
    <div class="head">
      <span class="label">Como funciona</span>
      <h2>Do primeiro contato à energia de volta</h2>
    </div>
{passos(f"em {nome}")}
  </div>
</section>

<section id="duvidas" class="band">
  <div class="wrap faq">
    <div class="head">
      <span class="label">Dúvidas</span>
      <h2>Perguntas sobre o atendimento em {esc(nome)}</h2>
    </div>
    <div class="qa">
{faq_html(perguntas)}
    </div>
  </div>
</section>

<section id="regioes" class="band band--dark">
  <div class="wrap regions">
    <div class="head">
      <span class="label">Outras cidades</span>
      <h2>Também atendemos</h2>
    </div>
    <ul class="cities">
{chips('../', excluir=c)}
    </ul>
  </div>
</section>

<section class="band">
  <div class="wrap cta">
    <div>
      <h2>Precisa de eletricista em {esc(nome)}?</h2>
      <p class="lead">Atendemos 24 horas, inclusive no fim de semana. Mande uma mensagem e receba o orçamento sem compromisso.</p>
    </div>
    <a class="btn btn--whats" href="{wa(texto_wa)}">{wa_icon()}WhatsApp {TELEFONE_VISIVEL}</a>
  </div>
</section>

</main>
""" + rodape(texto_wa)


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
