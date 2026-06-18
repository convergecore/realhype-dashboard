# ConvergeLABS Command OS

Business Intelligence & Operations Control Center da ConvergeLABS, com o workspace RealHype para Direct Commerce, Instagram Sales e CTT Portugal.

## Deploy e segurança

- Aplicação principal: `app.py`
- Runtime: Python 3.12
- Banco: Neon PostgreSQL, configurado exclusivamente em Streamlit Secrets
- Autenticação: utilizadores e roles `partner`/`sdr` configurados exclusivamente em Secrets
- Fallback local: SQLite, sem credenciais embutidas

Nunca versione `.streamlit/secrets.toml`. O código não precisa conhecer nem exibir URL, senha, token ou chave. No Streamlit Community Cloud, selecione `app.py` como arquivo principal e configure os Secrets na interface segura da plataforma.

## Execução local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para autenticação local, crie seu arquivo de Secrets a partir do exemplo ignorado pelo Git e use apenas valores de desenvolvimento.

## Perfis

- `partner`: acesso completo a Pulse, Sell, Ship, Stock, Growth, Intel, produtos, alertas e Config.
- `sdr`: Pulse limitado, Sell, Vendas, Ship, Stock operacional e Alertas.

As permissões são verificadas no app antes de ações sensíveis; ocultar um menu não é tratado como controle de acesso suficiente.

## Glossário de BI

- Receita: soma das vendas em status operacional válido.
- CMV: soma de `custo_unitário × quantidade` dos produtos vendidos.
- Lucro bruto estimado: receita menos CMV.
- Margem estimada: lucro bruto estimado dividido pela receita.
- Ticket médio: receita dividida pelo número de vendas válidas.
- Conversão lead → venda: vendas válidas divididas por leads.
- Giro de estoque: unidades vendidas divididas pelo estoque médio; depende de histórico suficiente.
- Stock crítico: unidades menores ou iguais ao mínimo configurado.
- Taxa de devolução: pedidos devolvidos divididos por pedidos enviados.
- CAC estimado: investimento em ads dividido por clientes adquiridos.
- ROAS estimado: receita atribuída dividida pelo investimento em ads.
- Forecast 30 dias: média diária recente multiplicada por 30; é uma projeção simples.
- LTV, churn e NPS: placeholders até existir histórico/recorrência/pesquisa adequados.

## Migrações

`ensure_schema()` executa somente operações aditivas e idempotentes:

- cria tabelas ausentes;
- adiciona colunas ausentes;
- preserva tabelas e dados existentes;
- não executa remoção de tabelas.

## Protótipo visual

`prototype/` contém o MVP frontend “Direct Commerce Intelligence Platform”, explicitamente marcado como DEMO. Usa pt-PT, EUR, `Europe/Lisbon` e dados fictícios sazonais de Instagram DM + CTT Portugal; não acede a Secrets nem liga ao Neon.

```bash
python -m http.server 8765 --directory prototype
```

Abra `http://127.0.0.1:8765`. A arquitetura, modelo de dados, RBAC, endpoints, glossário, segurança, performance e roadmap estão em `prototype/ARCHITECTURE.md`.

## Roadmap

### Fase 0 — MVP atual

Streamlit + Neon + login simples e operação manual.

### Fase 1 — Command OS operacional

Páginas, KPIs, CRM, stock, vendas e CTT integrados.

### Fase 2 — BI e alertas

ABC/Pareto, forecast, heatmap, cohort e anomalias com histórico crescente.

### Fase 3 — Automações

WhatsApp/Instagram oficiais quando viável, relatórios diários e follow-up automático.

### Fase 4 — SaaS premium

Migração para Next.js, Tailwind e shadcn/ui; autenticação profissional, API backend, logs centralizados e RBAC forte.

### Fase 5 — ConvergeLABS AI Layer

Recomendações automáticas, previsão de demanda, priorização de leads, detecção de risco CTT e copiloto SDR.

## Limites atuais

O lucro permanece estimado até confirmar custos finais de CTT, embalagem e ads. O login simples via Secrets é adequado ao MVP interno, mas deve migrar para um provedor de identidade e sessões profissionais na fase SaaS.
