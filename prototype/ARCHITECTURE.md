# REALHYPE COMMAND OS 2026 — Arquitetura do MVP

## 1. Visão

Plataforma Direct Commerce para Portugal, orientada ao ciclo **Pergunta → Insight → Ação**. Instagram DM é a origem principal; CTT Portugal é a camada logística. O protótipo usa pt-PT, EUR e `Europe/Lisbon`, com fuso configurável. É um frontend DEMO sem credenciais ou ligação externa.

## 2. Módulos

- **App Shell:** sidebar colapsável, topbar sticky, filtros globais e última atualização.
- **War Room:** caixa, lucro real, margem, risco CTT, stock e escala de ads.
- **IG Lead Command Queue:** fila DM, SLA primeiro toque, temperatura explicável, scripts e ações rápidas.
- **Fulfillment Control:** pedidos, validação de morada/telefone PT, tracking, incidentes, devolução e stock.
- **Intelligence Center:** funil, ABC/Pareto, forecast, heatmap, cohort e custos.
- **Governança:** alertas, audit log, permissão de exportação e RBAC.
- **DataService:** consultas, ações, auditoria e exportações. Deve ser substituído por chamadas autenticadas à API.

### Mapa de ecrãs e filas

| Ecrã | Pergunta principal | Fila/ação |
|---|---|---|
| War Room | Onde ganhar/perder caixa e margem hoje? | Alertas de stock, CTT, margem e escala |
| IG Lead Command Queue | Quem deve o SDR abordar agora? | Leads ordenados por urgência, temperatura e SLA |
| Fulfillment Control | Que pedido pode atrasar ou ser devolvido? | Confirmação → separação → etiqueta → tracking → entrega |
| Intelligence Center | O que explica conversão e lucro? | Drill-down por SDR, script, SKU, campanha e período |
| Leads IG / CRM | Qual é a próxima ação de cada DM? | Responder, criar pedido, follow-up |
| Pedidos | Qual é a margem real e o estado? | Avançar estado, validar dados, abrir detalhe |
| CTT Portugal | Qual tracking exige intervenção? | Morada, telefone, etiqueta, atraso, incidente e devolução |
| Stock | Onde existe campeão, parado ou ruptura? | Entrada, saída, ajuste, perda e reposição |
| Financeiro / Growth | Qual custo impede escala saudável? | Relatório, atribuição e revisão de campanha |
| Alertas / Audit Log | O que exige ação e quem fez o quê? | Resolver, exportar com permissão e auditar |

## 3. Fluxos principais

1. Lead entra pelo Instagram DM e recebe `ownerSDR`, temperatura, script, SLA e próxima ação.
2. SDR qualifica, regista a conversa e cria o pedido de baixo ticket (€29,99–€79,99).
3. Operação valida confirmação textual, morada portuguesa e telefone `+351`.
4. Pedido confirmado reserva/baixa stock numa transação atómica no backend.
5. CTT recebe o pedido; tracking, atraso, incidente, entrega ou devolução alimentam custos e causa raiz.
6. BI atribui COGS, CTT, taxas, imposto, atendimento e ads para calcular lucro real.
7. Alertas convertem exceções em ações rastreáveis no audit log.

## 4. RBAC

| Modo | Escopo | Exportação |
|---|---|---|
| Sócios | Todas as áreas estratégicas e operacionais | Permitida e auditada |
| SDR | IG Lead Command Queue, leads, pedidos, CTT e alertas | Negada no mock |
| Operação | Fulfillment Control, pedidos, CTT, stock e alertas | Negada no mock |
| BI | Intelligence Center, financeiro, Growth e alertas | Permitida e auditada |

Produção deve aplicar RBAC no servidor e escopo por entidade/unidade. Esconder menus não é autorização.

## 5. Modelo de dados sugerido

- `users`, `roles`, `permissions`, `user_units`
- `leads`, `interactions`, `tasks`, `playbooks`
- `customers`, `addresses`, `consents`
- `products`, `skus`, `inventory_balances`, `stock_movements`
- `orders`, `order_items`, `order_status_history`, `payments`
- `shipments`, `ctt_events`, `returns`, `return_costs`
- `campaigns`, `ad_spend`, `attribution_events`
- `expenses`, `tax_estimates`, `cost_allocations`
- `metric_snapshots`, `alerts`, `audit_logs`, `export_jobs`

IDs públicos devem ser opacos. Movimentos financeiros/stock devem ser append-only e reconciliáveis.

## 6. Endpoints sugeridos

- `GET /api/v1/dashboard?period=&unit=&channel=&category=&ownerSDR=&orderStatus=&timezone=`
- `GET/POST/PATCH /api/v1/leads`
- `POST /api/v1/leads/{id}/interactions`
- `GET/POST/PATCH /api/v1/orders`
- `POST /api/v1/orders/{id}/transition`
- `GET /api/v1/inventory`; `POST /api/v1/inventory/movements`
- `GET/PATCH /api/v1/shipments/{id}`
- `GET /api/v1/metrics/{metric}`
- `GET /api/v1/alerts`; `POST /api/v1/alerts/{id}/resolve`
- `POST /api/v1/exports`; `GET /api/v1/exports/{id}`
- `GET /api/v1/audit-logs`

## 7. Glossário de métricas

- **Receita:** soma dos pedidos válidos, sem cancelados.
- **Lucro real:** receita − COGS − CTT − taxas − imposto estimado − devoluções − atendimento − ads atribuídos.
- **Lucro real por pedido/SKU:** mesma fórmula, agregada pela entidade correspondente.
- **Margem real:** lucro real ÷ receita.
- **CAC:** ads atribuídos ÷ novos clientes.
- **LTV proxy:** ticket médio × frequência observada × margem real.
- **Churn:** clientes que deixaram de recomprar na janela definida ÷ clientes elegíveis.
- **Ticket médio:** receita ÷ pedidos válidos.
- **Giro:** unidades vendidas ÷ stock médio.
- **NPS:** promotores% − detratores%.
- **Inadimplência:** valor vencido não recebido ÷ valor vencido.
- **SLA primeiro toque:** mediana do tempo entre entrada da DM e primeira resposta humana.
- **Tempo de resposta:** média e percentis do tempo entre mensagens do cliente e resposta do SDR.
- **Conversão DM → pedido:** pedidos Instagram atribuídos ÷ conversas Instagram qualificadas.
- **Taxa de devolução:** pedidos devolvidos ÷ pedidos enviados.
- **Custo por conversa:** ads atribuídos ÷ conversas Instagram válidas.
- **Custo real por pedido:** COGS + CTT + taxas + imposto + devolução + atendimento + ads atribuídos, dividido por pedidos.
- **Custo de devolução:** CTT de ida/retorno + atendimento + perda/avaria atribuída.
- **Atraso CTT:** tracking acima do SLA configurado sem entrega.
- **Incidente CTT:** evento de exceção classificado por causa raiz.

## 8. Checklist de segurança

- CSP sem scripts/estilos inline, sem CDN e sem `innerHTML`.
- Entradas renderizadas com `textContent`; CSV escapa aspas e fórmulas deve ser neutralizado no backend.
- CSRF: cookie `SameSite`, token por sessão e validação de `Origin` em mutações.
- IDOR: autorização de recurso/unidade em toda consulta e mutação; IDs opacos.
- XSS: validação contextual, CSP com nonce/hash em produção e sanitização server-side.
- Persistência: queries parametrizadas e validação de schema no backend; nunca concatenar input em SQL.
- Sessões: cookies `HttpOnly`, `Secure`, rotação, MFA para Sócios e expiração por risco.
- Exportações: permissão explícita, limite, watermark, expiração e audit log.
- Audit log append-only com ator, role, entidade, antes/depois, IP reduzido e correlation ID.
- Secrets apenas em secret manager; nunca no bundle frontend.
- [x] DEMO sem credenciais, CDN, scripts inline ou `innerHTML`.
- [x] Exportações mock sujeitas a RBAC e audit log.
- [ ] Produção: testes SAST/DAST, revisão de dependências, rate limit e resposta a incidentes.

## 9. Checklist de performance

- Gráficos renderizados sob demanda com `IntersectionObserver`.
- Filtros persistentes e busca com debounce.
- Canvas evita dependência/CDN e reduz peso inicial.
- Atualização de DOM por fragmentos e `replaceChildren`, reduzindo reflow.
- Produção: paginação cursor-based, agregações pré-calculadas, cache por tenant e CDN apenas para assets imutáveis.
- [x] Lazy render, debounce, Canvas e atualização por fragmentos.
- [x] Sem framework, fontes externas ou biblioteca de gráficos no bundle.
- [ ] Produção: budgets de Core Web Vitals, compressão Brotli, RUM e testes de carga.

## 10. Roadmap em cinco fases

### Fase 1 — MVP operacional

App shell, quatro modos, dados DEMO, filas, KPIs, BI principal, Ctrl+K, filtros persistentes, audit/export e acessibilidade base.

### Fase 2 — Integrações v1

API real, PostgreSQL, OIDC/MFA, RBAC server-side, CTT oficial, ingestão Meta/Instagram, jobs de exportação, testes E2E e observabilidade.

### Fase 3 — Controlo e escala

Reconciliação de custos, tracking CTT, atribuição Instagram/ads, alertas de SLA e dashboards por SDR/script/SKU.

### Fase 4 — Inteligência v2

Forecast probabilístico, atribuição multitoque, recomendação de próxima ação, previsão de ruptura e alertas de anomalia explicáveis.

### Fase 5 — AI Operating Layer

Copiloto SDR, resumo seguro de DMs, previsão de risco CTT, recomendação de escala e explicações auditáveis.

## 11. Riscos

- Qualidade/consistência de atribuição entre Instagram Direct, ads e pedido.
- Limitações de APIs oficiais do Instagram e CTT.
- Custos incompletos distorcendo lucro real.
- Adoção operacional se a fila não refletir o processo humano.
- RGPD: base legal, minimização, retenção, transferências, direitos do titular e DPA com fornecedores.
