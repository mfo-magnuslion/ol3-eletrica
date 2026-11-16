# OL3 Elétrica

Site da OL3 Elétrica: eletricista residencial e comercial 24 horas em Jandira e região.
Página de vendas para o Google Ads, com contato pelo WhatsApp.

Site estático (HTML + CSS), sem etapa de build. Para ver localmente:

```bash
python3 -m http.server 8000
```

e abra http://localhost:8000.

## Estrutura

- `index.html`: página principal (gerada)
- `eletricista-<cidade>/`: páginas por cidade (geradas)
- `assets/site.css`: visual compartilhado por todas as páginas
- `assets/medicao.js`: tag do Google Ads e conversão "Clique no WhatsApp"
- `sitemap.xml` e `robots.txt`: gerados

## Editar o conteúdo

Todo o HTML é gerado por `scripts/gerar_site.py`. Textos, serviços, perguntas, cidades,
telefone e endereço do site ficam nas constantes do script. Depois de editar, rode:

```bash
python3 scripts/gerar_site.py
```

## Publicação

Hospedado na Vercel (projeto `ol3-eletrica`), com publicação automática a cada push no ramo `main`.
