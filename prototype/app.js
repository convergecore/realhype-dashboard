"use strict";

/*
  REALHYPE COMMAND OS 2026 — frontend DEMO.
  API sugerida: /api/v1/dashboard, /leads, /orders, /inventory, /campaigns,
  /metrics, /alerts, /exports e /audit-logs. Em produção, toda autorização,
  escopo de entidade, exportação e transição de status deve ser validada no servidor.
*/

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const text = (value) => document.createTextNode(String(value ?? ""));
const node = (tag, options = {}, children = []) => {
  const element = document.createElement(tag);
  Object.entries(options).forEach(([key, value]) => {
    if (key === "class") element.className = value;
    else if (key === "dataset") Object.entries(value).forEach(([dataKey, dataValue]) => { element.dataset[dataKey] = String(dataValue); });
    else if (key === "text") element.textContent = String(value);
    else if (key.startsWith("on") && typeof value === "function") element.addEventListener(key.slice(2), value);
    else if (value !== false && value !== null && value !== undefined) element.setAttribute(key, value === true ? "" : String(value));
  });
  children.forEach((child) => element.append(child instanceof Node ? child : text(child)));
  return element;
};
const clear = (element) => element.replaceChildren();
const eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", minimumFractionDigits: 2 });
const number = new Intl.NumberFormat("pt-PT");
const percent = (value) => `${Number(value || 0).toFixed(1).replace(".", ",")}%`;
const datePT = (value) => new Intl.DateTimeFormat("pt-PT", { dateStyle: "short", timeZone: state?.filters?.timezone || "Europe/Lisbon" }).format(new Date(value));
const debounce = (callback, wait = 220) => { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => callback(...args), wait); }; };

const ROLE_CONFIG = {
  partner: { label: "War Room", pages: ["command", "sdr", "ops", "intelligence", "leads", "sales", "ctt", "stock", "finance", "growth", "alerts", "audit"], export: true },
  sdr: { label: "Sales Command", pages: ["sdr", "leads", "sales", "ctt", "alerts"], export: false },
  ops: { label: "Ops Command", pages: ["ops", "sales", "ctt", "stock", "alerts"], export: false },
  bi: { label: "Intelligence Center", pages: ["intelligence", "finance", "growth", "alerts"], export: true }
};
const PAGES = [
  { id: "command", section: "Comando", icon: "◆", title: "War Room", subtitle: "Caixa, margem real, risco CTT e decisões de escala", action: "Criar pedido" },
  { id: "sdr", section: "Modos", icon: "◎", title: "IG Lead Command Queue", subtitle: "Fila DM priorizada e próxima melhor ação", action: "Novo lead IG" },
  { id: "ops", section: "Modos", icon: "▣", title: "Fulfillment Control", subtitle: "Pedidos, stock e logística CTT Portugal", action: "Movimentar stock" },
  { id: "intelligence", section: "Modos", icon: "⌁", title: "Intelligence Center", subtitle: "Funil, ABC, forecast e lucratividade", action: "Emitir relatório" },
  { id: "leads", section: "Operação", icon: "◉", title: "Leads IG / CRM", subtitle: "DMs, SLA primeiro toque e follow-up", action: "Novo lead IG" },
  { id: "sales", section: "Operação", icon: "◇", title: "Pedidos", subtitle: "Conversão DM e margem real por pedido", action: "Criar pedido" },
  { id: "ctt", section: "Operação", icon: "▤", title: "CTT Portugal", subtitle: "Morada, telefone, tracking e devolução", action: "Reimprimir etiqueta CTT" },
  { id: "stock", section: "Operação", icon: "▦", title: "Stock", subtitle: "Ruptura, giro e capital parado", action: "Movimentar stock" },
  { id: "finance", section: "Inteligência", icon: "◫", title: "Financeiro", subtitle: "Receita, despesas e lucro real", action: "Emitir relatório" },
  { id: "growth", section: "Inteligência", icon: "↗", title: "Anúncios / Growth", subtitle: "Custo por conversa e ads atribuídos", action: "Nova campanha" },
  { id: "alerts", section: "Governança", icon: "△", title: "Alertas", subtitle: "Exceções que exigem decisão", action: "Resolver alertas" },
  { id: "audit", section: "Governança", icon: "≡", title: "Audit Log", subtitle: "Ações, exportações e rastreabilidade", action: "Exportar log" }
];

const seeded = (index) => {
  const x = Math.sin(index * 999.91) * 43758.5453;
  return x - Math.floor(x);
};
const daysAgo = (days, hour = 12) => { const value = new Date(); value.setDate(value.getDate() - days); value.setHours(hour, 0, 0, 0); return value.toISOString(); };

function buildMockData() {
  const products = [
    ["RH-COR-01", "Corrente Cuban 8mm", "Correntes", 17.4, 49.99, 14], ["RH-COR-02", "Corrente Rope 5mm", "Correntes", 12.2, 39.99, 3],
    ["RH-PUL-01", "Pulseira Cuban", "Pulseiras", 10.8, 34.99, 26], ["RH-PIN-01", "Pendente Crown", "Pendentes", 8.1, 29.99, 0],
    ["RH-ANE-01", "Anel Signet", "Anéis", 9.3, 32.99, 19], ["RH-COR-03", "Corrente Tennis", "Correntes", 24.5, 79.99, 7],
    ["RH-PUL-02", "Pulseira Tennis", "Pulseiras", 19.8, 64.99, 11], ["RH-PIN-02", "Pendente Cross", "Pendentes", 11.4, 37.99, 42]
  ].map((item, index) => ({ id: index + 1, sku: item[0], name: item[1], category: item[2], cost: item[3], price: item[4], stock: item[5], min: 8, sold: 0 }));
  const owners = ["Ana", "Bruno", "Carla"];
  const channels = ["Instagram DM", "Instagram DM", "Instagram DM", "Instagram DM", "WhatsApp", "Orgânico"];
  const leads = Array.from({ length: 96 }, (_, index) => {
    const age = index % 72;
    const stage = ["lead", "prospect", "cliente", "perdido"][Math.floor(seeded(index + 3) * 4)];
    const temperature = stage === "cliente" ? "quente" : ["frio", "morno", "quente"][Math.floor(seeded(index + 8) * 3)];
    return { id: 1001 + index, name: `Lead Demo ${String(index + 1).padStart(2, "0")}`, contact: `+351 9${String(10000000 + index * 713).slice(-8)}`, channel: channels[index % channels.length], owner: owners[index % 3], stage, temperature, urgency: temperature === "quente" ? "alta" : age > 2 ? "média" : "baixa", createdAt: daysAgo(age, 9 + (index % 11)), lastInteraction: daysAgo(Math.min(age, index % 5), 10 + (index % 9)), firstTouchMinutes: 4 + (index * 7) % 48, script: ["Prova social", "Urgência stock", "Guia de tamanho"][index % 3], nextAction: ["Enviar catálogo IG", "Confirmar medida", "Follow-up DM", "Validar morada PT"][index % 4] };
  });
  const statuses = ["confirmado", "preparação", "enviado", "entregue", "entregue", "devolvido"];
  const orders = Array.from({ length: 74 }, (_, index) => {
    const product = products[index % products.length];
    const quantity = 1 + (index % 2);
    const seasonality = 1 + Math.sin((index / 74) * Math.PI * 2) * .18;
    const revenue = Number((product.price * quantity * seasonality).toFixed(2));
    const cogs = product.cost * quantity;
    product.sold += quantity;
    return { id: 2401 + index, leadId: leads[(index * 3) % leads.length].id, customer: leads[(index * 3) % leads.length].name, productId: product.id, sku: product.sku, product: product.name, category: product.category, channel: channels[index % channels.length], owner: owners[index % 3], quantity, status: statuses[index % statuses.length], revenue, cogs, shipping: 4.25 + (index % 4) * .35, fees: Number((revenue * .029).toFixed(2)), tax: Number((revenue * .04).toFixed(2)), support: 1.1 + (index % 4) * .25, media: index % 3 === 0 ? 7.2 : 3.4, addressOk: index % 7 !== 0, phoneOk: index % 9 !== 0, textOk: index % 6 !== 0, cttDelay: index % 11 === 0, cttIncident: index % 17 === 0 ? "Atraso no encaminhamento" : "", tracking: `CTT-DEMO-${2401 + index}`, createdAt: daysAgo(index % 72, 8 + (index % 14)) };
  });
  const campaigns = ["Cuban Always On", "Tennis Drop", "Retarget DM", "Creators Urban PT"].map((name, index) => ({ id: index + 1, name, spend: 420 + index * 135, messages: 180 + index * 57, sales: 21 + index * 8, revenue: 1050 + index * 390, channel: "Instagram DM" }));
  return { products, leads, orders, campaigns, audit: [{ at: new Date().toISOString(), actor: "system", role: "system", action: "demo_initialized", entity: "platform", result: "success" }] };
}

const mock = buildMockData();
class DataService {
  async delay() { await new Promise((resolve) => setTimeout(resolve, 90)); }
  async dashboard(filters) { await this.delay(); return calculateDataset(filters); }
  async queue(type, filters) { await this.delay(); return type === "leads" ? filterLeads(filters) : type === "stock" ? filterProducts(filters) : filterOrders(filters); }
  async audit(entry) { mock.audit.unshift({ at: new Date().toISOString(), ...entry }); return true; }
  async quickAction(kind, id) { await this.delay(); await this.audit({ actor: "Operador Demo", role: state.role, action: kind, entity: String(id), result: "success" }); return { ok: true }; }
  async export(resource) {
    if (!ROLE_CONFIG[state.role].export) { await this.audit({ actor: "Operador Demo", role: state.role, action: "export_denied", entity: resource, result: "denied" }); throw new Error("Seu perfil não possui permissão de exportação."); }
    await this.audit({ actor: "Operador Demo", role: state.role, action: "export_created", entity: resource, result: "success" });
    return resource === "audit" ? mock.audit : resource === "leads" ? filterLeads(state.filters) : filterOrders(state.filters);
  }
}
const dataService = new DataService();

const savedFilters = (() => { try { return JSON.parse(localStorage.getItem("realhype.filters") || "{}"); } catch { return {}; } })();
const migratedFilters = { ...savedFilters, unit: savedFilters.unit === "RealHype" ? "RealHype PT" : savedFilters.unit, channel: savedFilters.channel === "Instagram" ? "Instagram DM" : savedFilters.channel, category: savedFilters.category === "Pingentes" ? "Pendentes" : savedFilters.category };
const state = { role: localStorage.getItem("realhype.role") || "partner", page: "command", filters: { period: "30", unit: "RealHype PT", channel: "all", category: "all", owner: "all", status: "all", timezone: "Europe/Lisbon", ...migratedFilters }, updatedAt: new Date(), selectedQueueIndex: 0 };

function withinPeriod(value, days) { return Date.now() - new Date(value).getTime() <= Number(days) * 86400000; }
function filterOrders(filters = state.filters) { return mock.orders.filter((item) => withinPeriod(item.createdAt, filters.period) && (filters.channel === "all" || item.channel === filters.channel) && (filters.category === "all" || item.category === filters.category) && (filters.owner === "all" || item.owner === filters.owner) && (filters.status === "all" || item.status === filters.status)); }
function filterLeads(filters = state.filters) { return mock.leads.filter((item) => withinPeriod(item.createdAt, filters.period) && (filters.channel === "all" || item.channel === filters.channel) && (filters.owner === "all" || item.owner === filters.owner)); }
function filterProducts(filters = state.filters) { return mock.products.filter((item) => filters.category === "all" || item.category === filters.category); }
function orderProfit(order) { return order.revenue - order.cogs - order.shipping - order.fees - order.tax - order.support - order.media - (order.status === "devolvido" ? order.shipping * 1.6 : 0); }
function calculateDataset(filters) {
  const orders = filterOrders(filters), leads = filterLeads(filters), products = filterProducts(filters);
  const revenue = orders.reduce((sum, item) => sum + item.revenue, 0), profit = orders.reduce((sum, item) => sum + orderProfit(item), 0);
  const spend = mock.campaigns.reduce((sum, item) => sum + item.spend, 0), returns = orders.filter((item) => item.status === "devolvido").length;
  const igLeads = leads.filter((item) => item.channel === "Instagram DM"), igOrders = orders.filter((item) => item.channel === "Instagram DM"), slaValues = igLeads.map((item) => item.firstTouchMinutes).sort((a, b) => a - b);
  const medianSLA = slaValues.length ? slaValues[Math.floor(slaValues.length / 2)] : 0;
  const realCosts = orders.reduce((sum, item) => sum + item.cogs + item.shipping + item.fees + item.tax + item.support + item.media + (item.status === "devolvido" ? item.shipping * 1.6 : 0), 0);
  return { orders, leads, products, revenue, profit, margin: revenue ? profit / revenue * 100 : 0, ticket: orders.length ? revenue / orders.length : 0, conversion: igLeads.length ? igOrders.length / igLeads.length * 100 : 0, returns, returnRate: orders.length ? returns / orders.length * 100 : 0, returnCost: orders.filter((item) => item.status === "devolvido").reduce((sum, item) => sum + item.shipping * 1.6 + item.support, 0), cttDelays: orders.filter((item) => item.cttDelay).length, cttIncidents: orders.filter((item) => item.cttIncident).length, medianSLA, responseAverage: slaValues.length ? slaValues.reduce((sum, value) => sum + value, 0) / slaValues.length : 0, costConversation: igLeads.length ? spend / igLeads.length : 0, costOrder: orders.length ? realCosts / orders.length : 0, stockValue: products.reduce((sum, item) => sum + item.stock * item.cost, 0), critical: products.filter((item) => item.stock <= item.min), cac: orders.length ? spend / orders.length : 0 };
}

function badge(label, tone = "cyan") { return node("span", { class: `badge ${tone}`, text: label }); }
function sectionHead(title, subtitle, action) {
  const copy = node("div", {}, [node("h2", { text: title }), node("p", { text: subtitle })]);
  return node("div", { class: "section-head" }, [copy, action || text("")]);
}
function panel(title, subtitle, content, span = "") {
  return node("section", { class: `panel ${span}`.trim() }, [node("div", { class: "panel-head" }, [node("h3", { text: title }), node("span", { text: subtitle })]), content]);
}
function emptyState(title, description) { return node("div", { class: "empty-state" }, [node("div", {}, [node("strong", { text: title }), node("span", { text: description })])]); }

function buildNavigation() {
  const nav = $("#main-nav"); clear(nav);
  const allowed = ROLE_CONFIG[state.role].pages;
  let section = "";
  PAGES.filter((page) => allowed.includes(page.id)).forEach((page) => {
    if (page.section !== section) { section = page.section; nav.append(node("div", { class: "nav-section", text: section })); }
    nav.append(node("button", { class: `nav-button ${state.page === page.id ? "active" : ""}`, dataset: { page: page.id }, "aria-current": state.page === page.id ? "page" : null, onclick: () => navigate(page.id) }, [node("span", { class: "nav-icon", "aria-hidden": "true", text: page.icon }), node("span", { text: page.title })]));
  });
}

function navigate(pageId) {
  if (!ROLE_CONFIG[state.role].pages.includes(pageId)) { toast("Acesso negado para este modo.", "error"); return; }
  state.page = pageId; state.selectedQueueIndex = 0; buildNavigation(); render();
  if (window.innerWidth < 821) $("#sidebar").classList.remove("open");
  $("#main-content").focus();
}

function setPageHeader() {
  const page = PAGES.find((item) => item.id === state.page) || PAGES[0];
  $("#page-title").textContent = page.title; $("#page-subtitle").textContent = page.subtitle; $("#primary-action").textContent = page.action;
  document.title = `${page.title} · REALHYPE COMMAND OS 2026`;
}

async function render() {
  setPageHeader();
  const loading = $("#loading-state"), content = $("#page-content"); loading.classList.remove("hidden"); content.classList.add("hidden");
  try {
    const dataset = await dataService.dashboard(state.filters); clear(content);
    const renderer = { command: renderCommand, sdr: renderSalesCommand, ops: renderOpsCommand, intelligence: renderIntelligence, leads: renderLeads, sales: renderSales, ctt: renderCTT, stock: renderStock, finance: renderFinance, growth: renderGrowth, alerts: renderAlerts, audit: renderAudit }[state.page];
    content.append(renderer ? renderer(dataset) : emptyState("Página indisponível", "Selecione outra área."));
    content.classList.remove("hidden"); lazyRenderCharts(content); state.updatedAt = new Date(); updateTimes();
  } catch (error) {
    clear(content); content.append(emptyState("Não foi possível carregar", "Tente atualizar. Nenhum dado foi alterado.")); content.classList.remove("hidden"); console.error(error);
  } finally { loading.classList.add("hidden"); }
}

function makeSparkline(values, tone = "#d6b25e") {
  const canvas = node("canvas", { class: "sparkline", width: "184", height: "60", "aria-label": "Tendência dos últimos períodos", role: "img" });
  canvas.dataset.chart = "spark"; canvas.dataset.values = values.join(","); canvas.dataset.tone = tone; return canvas;
}
function metricCard(metric) {
  const deltaTone = metric.delta >= 0 ? "trend-up" : "trend-down";
  const card = node("article", { class: "metric-card" }, [
    node("div", { class: "metric-top" }, [node("span", { text: metric.label }), node("span", { text: "ⓘ", title: metric.help })]),
    node("strong", { text: metric.value }),
    node("div", { class: "metric-meta" }, [node("span", { class: deltaTone, text: `${metric.delta >= 0 ? "↑" : "↓"} ${Math.abs(metric.delta).toFixed(1).replace(".", ",")}%` }), node("span", { class: "target", text: `Meta ${metric.target}` })]),
    makeSparkline(metric.spark, metric.delta >= 0 ? "#22c55e" : "#ef4444")
  ]);
  card.append(node("button", { class: "drill-button", "aria-label": `Abrir detalhes de ${metric.label}`, onclick: () => openDrawer(metric.label, [["Valor atual", metric.value], ["Variação", `${metric.delta.toFixed(1)}%`], ["Meta", metric.target], ["Definição", metric.help]]) }));
  return card;
}
function metricsGrid(dataset, mode = "strategic") {
  const metrics = mode === "sales" ? [
    ["Leads IG na fila", number.format(dataset.leads.filter((l) => l.channel === "Instagram DM" && l.stage !== "cliente").length), 12.4, "60", "Leads Instagram DM abertos por prioridade"], ["SLA 1º toque · mediana", `${Math.round(dataset.medianSLA)} min`, -8.2, "≤ 15 min", "Mediana entre entrada da DM e primeira resposta humana"], ["Conversão DM → pedido", percent(dataset.conversion), 4.1, "28%", "Pedidos Instagram divididos por leads Instagram"], ["Custo por conversa", eur.format(dataset.costConversation), -5.4, "≤ € 3,00", "Ads atribuídos divididos por conversas IG"]
  ] : mode === "ops" ? [
    ["Pedidos na fila", number.format(dataset.orders.filter((o) => !["entregue", "devolvido"].includes(o.status)).length), 5.2, "≤ 12", "Pedidos aguardando etapa operacional"], ["Sem confirmação", number.format(dataset.orders.filter((o) => !o.textOk).length), -3.4, "0", "Pedidos sem confirmação textual"], ["Atrasos / incidentes CTT", number.format(dataset.cttDelays + dataset.cttIncidents), -2.1, "0", "Pedidos com atraso ou incidente CTT"], ["Custo devoluções", eur.format(dataset.returnCost), -1.2, "< € 50", "CTT de retorno e atendimento associado"]
  ] : [
    ["Receita", eur.format(dataset.revenue), 14.8, "€ 4.500", "Receita bruta dos pedidos no período"], ["Lucro real", eur.format(dataset.profit), 9.6, "€ 1.650", "Receita menos COGS, CTT, taxas, imposto, atendimento e ads"], ["Margem real", percent(dataset.margin), -1.7, "≥ 35%", "Lucro real dividido pela receita"], ["Caixa projetado 30d", eur.format(dataset.revenue / Number(state.filters.period) * 30), 11.3, "€ 5.500", "Run rate simples do período"], ["Ticket médio", eur.format(dataset.ticket), 3.8, "€ 49,99", "Receita dividida por pedidos"], ["Custo real / pedido", eur.format(dataset.orders.length ? dataset.orders.reduce((sum, order) => sum + order.cogs + order.shipping + order.fees + order.tax + order.support + order.media, 0) / dataset.orders.length : 0), -6.2, "≤ € 30", "COGS + CTT + taxas + devolução + atendimento + ads"], ["Stock em risco", number.format(dataset.critical.length), 0, "0", "SKUs no mínimo ou abaixo"], ["Devolução", percent(dataset.returnRate), -2.3, "< 5%", "Pedidos devolvidos sobre pedidos"]
  ];
  const grid = node("section", { class: "metrics-grid", "aria-label": "Indicadores-chave" });
  metrics.forEach((metric, index) => grid.append(metricCard({ label: metric[0], value: metric[1], delta: metric[2], target: metric[3], help: metric[4], spark: Array.from({ length: 12 }, (_, point) => 35 + seeded(index * 20 + point) * 45 + point * (metric[2] / 10)) })));
  return grid;
}

function insights(dataset) {
  const items = [
    ["△", "Ruptura iminente", `${dataset.critical.length} SKUs exigem decisão de reposição.`, "Abrir stock", "stock"],
    ["↗", "Escala com cautela", `Margem real em ${percent(dataset.margin)} após custos atribuídos.`, "Ver BI", "intelligence"],
    ["◎", "Atacar leads quentes", `${dataset.leads.filter((l) => l.temperature === "quente" && l.stage !== "cliente").length} conversas têm alta propensão.`, "Abrir fila", "sdr"]
  ];
  const list = node("div", { class: "insight-list" });
  items.forEach((item) => list.append(node("div", { class: "insight" }, [node("div", { class: "insight-icon", text: item[0] }), node("div", {}, [node("strong", { text: item[1] }), node("p", { text: item[2] })]), node("button", { text: item[3], onclick: () => navigate(item[4]) })])));
  return list;
}

function renderCommand(dataset) {
  const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Visão executiva", "Perguntas que exigem decisão agora"), metricsGrid(dataset));
  const grid = node("div", { class: "panel-grid" });
  grid.append(panel("Ações recomendadas", "Insight → ação", insights(dataset), "span-4"));
  grid.append(panel("Receita, custos e lucro", "Série diária · EUR", chartCanvas("financial", dataset), "span-8"));
  grid.append(panel("Funil Direct Commerce", "Chat → pedido → entrega", funnel(dataset), "span-4"));
  grid.append(panel("Alertas de risco", "Prioridade operacional", alertList(dataset), "span-4"));
  grid.append(panel("Stock: campeão × parado", "Receita e capital", productAttention(dataset), "span-4"));
  fragment.append(grid); return fragment;
}

function chartCanvas(type, dataset, small = false) {
  const canvas = node("canvas", { class: `chart ${small ? "small" : ""}`, width: "900", height: small ? "300" : "440", role: "img", "aria-label": type === "financial" ? "Gráfico de receita, despesas e lucro" : "Gráfico analítico" });
  canvas.dataset.chart = type; canvas._dataset = dataset; return canvas;
}
function funnel(dataset) {
  const values = [["Conversas", dataset.leads.length], ["Qualificados", dataset.leads.filter((l) => l.temperature !== "frio").length], ["Pedidos", dataset.orders.length], ["Entregues", dataset.orders.filter((o) => o.status === "entregue").length]];
  const max = Math.max(...values.map((item) => item[1]), 1), container = node("div", { class: "funnel" });
  values.forEach(([label, value]) => { const level = Math.max(1, Math.ceil(value / max * 8)); container.append(node("div", { class: "funnel-step" }, [node("strong", { text: number.format(value) }), node("div", { class: `funnel-bar h${level}` }), node("span", { text: label })])); });
  return container;
}
function alertList(dataset) {
  const list = node("div", { class: "insight-list" });
  const alerts = [
    ...dataset.critical.map((product) => [product.stock === 0 ? "crítico" : "atenção", product.sku, `${product.name}: ${product.stock} un.`, "Repor ou pausar oferta"]),
    ...dataset.orders.filter((order) => !order.addressOk || !order.phoneOk).slice(0, 3).map((order) => ["atenção", `Pedido #${order.id}`, "Dados incompletos para CTT", "Validar cliente"]),
    ...dataset.orders.filter((order) => order.cttDelay || order.cttIncident).slice(0, 2).map((order) => ["crítico", `Tracking ${order.tracking}`, order.cttIncident || "CTT acima do SLA", "Investigar causa raiz"]),
    ...dataset.orders.filter((order) => orderProfit(order) / order.revenue < .2).slice(0, 2).map((order) => ["atenção", order.sku, "Margem real inferior a 20%", "Rever ads/custos"])
  ];
  alerts.slice(0, 6).forEach((item) => list.append(node("div", { class: "insight" }, [badge(item[0], item[0] === "crítico" ? "red" : "yellow"), node("div", {}, [node("strong", { text: item[1] }), node("p", { text: item[2] })]), node("button", { text: item[3], onclick: () => toast(`Ação aberta: ${item[3]}`) })])));
  return alerts.length ? list : emptyState("Operação estável", "Nenhum alerta ativo.");
}
function productAttention(dataset) {
  const list = node("div", { class: "insight-list" });
  [...dataset.products].sort((a, b) => (b.sold * b.price) - (a.sold * a.price)).slice(0, 5).forEach((product, index) => list.append(node("div", { class: "insight" }, [node("div", { class: "insight-icon", text: index < 2 ? "A" : "C" }), node("div", {}, [node("strong", { text: product.name }), node("p", { text: `${product.sold} vendidos · ${product.stock} em stock` })]), badge(product.stock <= product.min ? "risco" : "saudável", product.stock <= product.min ? "red" : "green")])))
  return list;
}

function queueTable(rows, type) {
  if (!rows.length) return emptyState("Fila vazia", "Nenhum item corresponde aos filtros atuais.");
  const columns = type === "leads" ? ["Prioridade", "Lead", "Canal", "Temperatura", "Owner SDR", "Última interação", "Próxima ação", "Ações"] : type === "stock" ? ["SKU", "Produto", "Stock", "Mínimo", "Giro", "Capital", "Estado", "Ações"] : ["Pedido", "Cliente", "Produto", "Estado", "Receita", "Lucro real", "Dados", "Ações"];
  const table = node("table", { "aria-label": `Fila de ${type}` }), head = node("thead"), headRow = node("tr"); columns.forEach((column) => headRow.append(node("th", { text: column, scope: "col" }))); head.append(headRow); table.append(head);
  const body = node("tbody");
  rows.slice(0, 30).forEach((item, rowIndex) => {
    const row = node("tr", { tabindex: rowIndex === state.selectedQueueIndex ? "0" : "-1", dataset: { queueRow: rowIndex }, onkeydown: (event) => { if (event.key === "Enter") openDrawer(`${type} · ${item.id || item.sku}`, Object.entries(item).slice(0, 10)); } });
    const cells = type === "leads" ? [badge(item.urgency, item.urgency === "alta" ? "red" : "yellow"), item.name, item.channel, badge(item.temperature, item.temperature === "quente" ? "green" : "cyan"), item.owner, datePT(item.lastInteraction), item.nextAction, quickActions(type, item.id)] : type === "stock" ? [item.sku, item.name, number.format(item.stock), number.format(item.min), `${item.sold} un.`, eur.format(item.stock * item.cost), badge(item.stock === 0 ? "ruptura" : item.stock <= item.min ? "crítico" : "ok", item.stock <= item.min ? "red" : "green"), quickActions(type, item.id)] : [`#${item.id}`, item.customer, item.product, badge(item.status, item.status === "devolvido" ? "red" : item.status === "entregue" ? "green" : "yellow"), eur.format(item.revenue), eur.format(orderProfit(item)), badge(item.addressOk && item.phoneOk && item.textOk ? "validado" : "pendente", item.addressOk && item.phoneOk && item.textOk ? "green" : "red"), quickActions(type, item.id)];
    cells.forEach((cell, index) => row.append(node("td", { class: [4, 5].includes(index) && type !== "leads" ? "numeric" : "" }, [cell instanceof Node ? cell : text(cell)]))); body.append(row);
  });
  table.append(body); return node("div", { class: "table-wrap" }, [table]);
}
function quickActions(type, id) {
  const wrap = node("div", { class: "quick-actions" });
  const actions = type === "leads" ? [["Responder", "lead_reply"], ["Venda", "new_sale"]] : type === "stock" ? [["Movimentar", "stock_move"], ["Detalhes", "open"]] : [["Avançar", "order_advance"], ["Etiqueta", "label_reprint"]];
  actions.forEach(([label, action]) => wrap.append(node("button", { text: label, onclick: async () => { await dataService.quickAction(action, id); toast(`${label}: ação registrada no audit log.`); } })));
  return wrap;
}
function queueToolbar(type, dataset) {
  const wrap = node("div", { class: "queue-toolbar" });
  const search = node("input", { placeholder: "Buscar por nome, ID ou SKU", "aria-label": "Buscar na fila" });
  search.addEventListener("input", debounce(() => { const value = search.value.toLocaleLowerCase("pt-PT"); $$("tbody tr").forEach((row) => row.classList.toggle("hidden", !row.textContent.toLocaleLowerCase("pt-PT").includes(value))); }));
  const count = node("span", { class: "last-update", text: `${type === "leads" ? dataset.leads.length : type === "stock" ? dataset.products.length : dataset.orders.length} itens` });
  const exportButton = node("button", { class: "secondary-button", text: "Exportar CSV", onclick: () => exportResource(type) });
  wrap.append(search, exportButton, count); return wrap;
}

function renderSalesCommand(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Fila de execução Instagram", "Prioridade por temperatura, SLA e próxima ação"), metricsGrid(dataset, "sales")); const grid = node("div", { class: "panel-grid" }); grid.append(panel("Próximas ações do SDR", "Atalhos: J/K navegar · Enter abrir", node("div", {}, [queueToolbar("leads", dataset), queueTable([...dataset.leads].sort((a, b) => ({ alta: 0, média: 1, baixa: 2 }[a.urgency] - { alta: 0, média: 1, baixa: 2 }[b.urgency])), "leads")]), "span-8")); grid.append(panel("Playbook sugerido", `Resposta média ${Math.round(dataset.responseAverage)} min · Scripts contextuais`, playbook(dataset), "span-4")); fragment.append(grid); return fragment; }
function playbook(dataset) { const hot = dataset.leads.filter((lead) => lead.temperature === "quente").length; return node("div", { class: "insight-list" }, [node("div", { class: "insight" }, [node("div", { class: "insight-icon", text: "1" }), node("div", {}, [node("strong", { text: "Fechar intenção alta" }), node("p", { text: `${hot} leads quentes: validar preferência e disponibilidade.` })])]), node("div", { class: "insight" }, [node("div", { class: "insight-icon", text: "2" }), node("div", {}, [node("strong", { text: "Reduzir atrito" }), node("p", { text: "Confirmar preço, medida, morada e telefone no mesmo fluxo." })])]), node("div", { class: "insight" }, [node("div", { class: "insight-icon", text: "3" }), node("div", {}, [node("strong", { text: "Follow-up 24h" }), node("p", { text: "Retomar conversas mornas com prova social e CTA único." })])])]); }
function renderOpsCommand(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Fila operacional", "Pedido confirmado → entrega CTT"), metricsGrid(dataset, "ops")); const grid = node("div", { class: "panel-grid" }); grid.append(panel("Pedidos por status", "Ações rápidas e validações", node("div", {}, [queueToolbar("orders", dataset), queueTable(dataset.orders.filter((order) => order.status !== "entregue"), "orders")]), "span-8")); grid.append(panel("Risco logístico", "Prejuízo evitável", alertList(dataset), "span-4")); fragment.append(grid); return fragment; }

function renderIntelligence(dataset) {
  const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Intelligence Center", "Sinais, causalidade e projeção"), metricsGrid(dataset));
  const grid = node("div", { class: "panel-grid" }); grid.append(panel("Receita × custos × lucro", "Custos completos atribuídos", chartCanvas("financial", dataset), "span-8")); grid.append(panel("Forecast 30 dias", "Cenários conservador, base e agressivo", forecastScenarios(dataset), "span-4")); grid.append(panel("Pareto / ABC por margem", "Classe A concentra lucro real", chartCanvas("pareto", dataset), "span-6")); grid.append(panel("Heatmap dia × hora", "Receita IG por momento", heatmap(dataset), "span-6")); grid.append(panel("Lucro real por SKU", "COGS + CTT + taxas + devolução + atendimento + ads", skuProfitTable(dataset), "span-6")); grid.append(panel("Conversão por SDR / script", "Pedidos por lead atribuído", sdrScriptTable(dataset), "span-6")); grid.append(panel("Cohort simples", "Mês da primeira compra", cohortTable(dataset), "span-6")); grid.append(panel("Funil Instagram", "DM → pedido → entrega", funnel(dataset), "span-6")); grid.append(panel("Alertas e anomalias", "Margem, CTT, devolução e stock", alertList(dataset), "span-12")); fragment.append(grid); return fragment;
}
function forecastScenarios(dataset) { const daily = dataset.revenue / Math.max(1, Number(state.filters.period)), base = daily * 30; return node("div", {}, [chartCanvas("forecast", dataset, true), simpleTable(["Cenário", "Receita 30d"], [["Conservador", eur.format(base * .82)], ["Base", eur.format(base)], ["Agressivo", eur.format(base * 1.22)]])]); }
function skuProfitTable(dataset) { const grouped = new Map(); dataset.orders.forEach((order) => { const current = grouped.get(order.sku) || { sku: order.sku, product: order.product, profit: 0, revenue: 0 }; current.profit += orderProfit(order); current.revenue += order.revenue; grouped.set(order.sku, current); }); const sorted = [...grouped.values()].sort((a, b) => b.profit - a.profit), total = sorted.reduce((sum, item) => sum + Math.max(0, item.profit), 0); let cumulative = 0; return simpleTable(["SKU", "Produto", "Receita", "Lucro real", "ABC margem"], sorted.map((item) => { cumulative += Math.max(0, item.profit); const share = total ? cumulative / total * 100 : 0, abc = share <= 80 ? "A" : share <= 95 ? "B" : "C"; return [item.sku, item.product, eur.format(item.revenue), eur.format(item.profit), badge(abc, abc === "A" ? "green" : abc === "B" ? "yellow" : "cyan")]; })); }
function sdrScriptTable(dataset) { const groups = new Map(); dataset.leads.forEach((lead) => { const key = `${lead.owner} · ${lead.script}`, current = groups.get(key) || { owner: lead.owner, script: lead.script, leads: 0, orders: 0 }; current.leads += 1; current.orders += dataset.orders.filter((order) => order.leadId === lead.id).length; groups.set(key, current); }); return simpleTable(["SDR", "Script", "Leads", "Pedidos", "Conversão"], [...groups.values()].map((item) => [item.owner, item.script, item.leads, item.orders, percent(item.leads ? item.orders / item.leads * 100 : 0)])); }
function heatmap(dataset) { const wrap = node("div", { class: "heatmap", role: "img", "aria-label": "Mapa de calor por dia e hora" }), days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], hours = [8, 10, 12, 14, 16, 18, 20, 22]; wrap.append(node("div", { class: "heatmap-cell label" })); hours.forEach((hour) => wrap.append(node("div", { class: "heatmap-cell label", text: `${hour}h` }))); days.forEach((day, dayIndex) => { wrap.append(node("div", { class: "heatmap-cell label", text: day })); hours.forEach((hour, hourIndex) => { const intensity = .08 + seeded(dayIndex * 10 + hourIndex) * .75, level = Math.max(1, Math.ceil(intensity * 8)); wrap.append(node("div", { class: `heatmap-cell i${level}`, title: `${day}, ${hour}h`, text: number.format(Math.round(dataset.revenue / 56 * (.4 + intensity))) })); }); }); return wrap; }
function cohortTable(dataset) { const rows = Array.from({ length: 6 }, (_, index) => ({ cohort: new Intl.DateTimeFormat("pt-PT", { month: "short", year: "2-digit" }).format(new Date(Date.now() - index * 30 * 86400000)), customers: 18 + index * 4, m0: 100, m1: Math.round(36 - index * 2), m2: Math.max(8, Math.round(23 - index * 2)), revenue: dataset.revenue / 6 * (1 - index * .07) })); return simpleTable(["Coorte", "Clientes", "M0", "M1", "M2", "Receita"], rows.map((row) => [row.cohort, row.customers, percent(row.m0), percent(row.m1), percent(row.m2), eur.format(row.revenue)])); }

function simpleTable(headers, rows) { const table = node("table"), head = node("thead"), hr = node("tr"); headers.forEach((header) => hr.append(node("th", { text: header }))); head.append(hr); table.append(head); const body = node("tbody"); rows.forEach((values) => { const row = node("tr"); values.forEach((value) => row.append(node("td", {}, [value instanceof Node ? value : text(value)]))); body.append(row); }); table.append(body); return node("div", { class: "table-wrap" }, [table]); }
function renderLeads(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("CRM operacional", "SLA, temperatura e dono"), metricsGrid(dataset, "sales")); fragment.append(panel("Leads priorizados", "Busca e ação rápida", node("div", {}, [queueToolbar("leads", dataset), queueTable(dataset.leads, "leads")]), "span-12")); return fragment; }
function renderSales(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Pedidos e margem", "Venda com custos completos")); fragment.append(panel("Pedidos", "Receita e lucro real por pedido", node("div", {}, [queueToolbar("orders", dataset), queueTable(dataset.orders, "orders")]), "span-12")); return fragment; }
function cttTable(rows) { if (!rows.length) return emptyState("Fila CTT vazia", "Não existem pedidos com risco nos filtros atuais."); return simpleTable(["Pedido", "Cliente", "Tracking", "Confirmação", "Morada PT", "Telefone", "Estado", "Atraso", "Incidente / causa raiz", "Ação"], rows.map((order) => [`#${order.id}`, order.customer, order.tracking, badge(order.textOk ? "sim" : "não", order.textOk ? "green" : "red"), badge(order.addressOk ? "válida" : "pendente", order.addressOk ? "green" : "red"), badge(order.phoneOk ? "válido" : "pendente", order.phoneOk ? "green" : "red"), badge(order.status, order.status === "devolvido" ? "red" : "yellow"), order.cttDelay ? badge("atraso", "red") : badge("no prazo", "green"), order.cttIncident || "—", quickActions("orders", order.id)])); }
function renderCTT(dataset) { const risky = dataset.orders.filter((order) => !order.addressOk || !order.phoneOk || !order.textOk || order.status === "devolvido" || order.cttDelay || order.cttIncident); const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Fulfillment CTT", "Confirmação, tracking, incidente e causa raiz"), metricsGrid(dataset, "ops")); fragment.append(panel("Fila de risco CTT Portugal", "J/K navegar · Enter abrir · ações rápidas", node("div", {}, [queueToolbar("orders", { ...dataset, orders: risky }), cttTable(risky)]), "span-12")); return fragment; }
function renderStock(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Inventário e capital", "Giro, ruptura e oportunidade")); const grid = node("div", { class: "panel-grid" }); grid.append(panel("Stock por SKU", "Nunca permitir saldo negativo", node("div", {}, [queueToolbar("stock", dataset), queueTable(dataset.products, "stock")]), "span-8")); grid.append(panel("Capital parado", eur.format(dataset.products.filter((p) => p.sold < 5).reduce((sum, p) => sum + p.stock * p.cost, 0)), productAttention(dataset), "span-4")); fragment.append(grid); return fragment; }
function renderFinance(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Controlo financeiro", "Lucro real com custos atribuídos"), metricsGrid(dataset)); const grid = node("div", { class: "panel-grid" }); grid.append(panel("Receita × custos × lucro", "EUR · período selecionado", chartCanvas("financial", dataset), "span-8")); grid.append(panel("Estrutura de custos", "COGS, CTT, taxas, imposto, ads", chartCanvas("costs", dataset), "span-4")); grid.append(panel("Pedidos", "Valores auditáveis", queueTable(dataset.orders, "orders"), "span-12")); fragment.append(grid); return fragment; }
function renderGrowth(dataset) { const rows = mock.campaigns.map((campaign) => [campaign.name, campaign.channel, eur.format(campaign.spend), number.format(campaign.messages), eur.format(campaign.spend / campaign.messages), campaign.sales, percent(campaign.sales / campaign.messages * 100), eur.format(campaign.revenue), `${(campaign.revenue / campaign.spend).toFixed(2)}x`]); const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Ads e atribuição", "Custo real por conversa e pedido")); fragment.append(panel("Campanhas Instagram", "Dados DEMO atribuídos", simpleTable(["Campanha", "Canal", "Investimento", "Conversas", "Custo/conversa", "Pedidos", "Conversão", "Receita", "ROAS"], rows), "span-12")); return fragment; }
function renderAlerts(dataset) { const fragment = document.createDocumentFragment(); fragment.append(sectionHead("Central de alertas", "Severidade, entidade e ação recomendada")); fragment.append(panel("Alertas ativos", "Ordenados por impacto", alertList(dataset), "span-12")); return fragment; }
function renderAudit() { const rows = mock.audit.map((entry) => [new Intl.DateTimeFormat("pt-PT", { dateStyle: "short", timeStyle: "medium", timeZone: state.filters.timezone }).format(new Date(entry.at)), entry.actor, entry.role, entry.action, entry.entity, badge(entry.result, entry.result === "success" ? "green" : "red")]); const fragment = document.createDocumentFragment(); const exportButton = node("button", { class: "secondary-button", text: "Exportar audit log", onclick: () => exportResource("audit") }); fragment.append(sectionHead("Rastreabilidade", "Ações, exportações e recusas", exportButton)); fragment.append(panel("Eventos", `${rows.length} registos na sessão`, simpleTable(["Data", "Ator", "Role", "Ação", "Entidade", "Resultado"], rows), "span-12")); return fragment; }

function lazyRenderCharts(root) {
  const observer = new IntersectionObserver((entries, currentObserver) => entries.forEach((entry) => { if (entry.isIntersecting) { drawChart(entry.target); currentObserver.unobserve(entry.target); } }), { rootMargin: "80px" });
  $$(`canvas[data-chart]`, root).forEach((canvas) => observer.observe(canvas));
}
function canvasContext(canvas) { const ratio = window.devicePixelRatio || 1, box = canvas.getBoundingClientRect(); canvas.width = Math.max(200, box.width * ratio); canvas.height = Math.max(80, box.height * ratio); const ctx = canvas.getContext("2d"); ctx.scale(ratio, ratio); return { ctx, width: box.width, height: box.height }; }
function drawChart(canvas) {
  const { ctx, width, height } = canvasContext(canvas); ctx.clearRect(0, 0, width, height);
  if (canvas.dataset.chart === "spark") { drawLine(ctx, width, height, canvas.dataset.values.split(",").map(Number), canvas.dataset.tone, false); return; }
  const dataset = canvas._dataset || calculateDataset(state.filters), type = canvas.dataset.chart;
  if (type === "financial") { const revenue = Array.from({ length: 14 }, (_, i) => dataset.revenue / 14 * (.62 + i * .035 + seeded(i) * .35)); const costs = revenue.map((value, i) => value * (.55 + seeded(i + 20) * .12)); drawAxes(ctx, width, height); drawLine(ctx, width, height, revenue, "#d6b25e", true); drawLine(ctx, width, height, costs, "#64748b", true); drawLegend(ctx, [["Receita", "#d6b25e"], ["Despesas", "#64748b"]]); }
  else if (type === "forecast") { const history = Array.from({ length: 12 }, (_, i) => dataset.revenue / 12 * (.7 + i * .04 + seeded(i + 60) * .25)); const projection = history.concat(Array.from({ length: 6 }, (_, i) => history.at(-1) * (1 + (i + 1) * .025))); drawAxes(ctx, width, height); drawLine(ctx, width, height, projection, "#22d3ee", true); drawLegend(ctx, [["Forecast simples", "#22d3ee"]]); }
  else if (type === "pareto") { const margins = new Map(); dataset.orders.forEach((order) => margins.set(order.sku, (margins.get(order.sku) || 0) + Math.max(0, orderProfit(order)))); const products = [...dataset.products].sort((a, b) => (margins.get(b.sku) || 0) - (margins.get(a.sku) || 0)); drawBars(ctx, width, height, products.map((product) => margins.get(product.sku) || 0), "#d6b25e", products.map((product) => product.sku)); }
  else if (type === "costs") { const orders = dataset.orders, values = [orders.reduce((s, o) => s + o.cogs, 0), orders.reduce((s, o) => s + o.shipping, 0), orders.reduce((s, o) => s + o.fees + o.tax, 0), orders.reduce((s, o) => s + o.media, 0), orders.reduce((s, o) => s + o.support, 0)]; drawBars(ctx, width, height, values, "#22d3ee", ["COGS", "Frete", "Taxas", "Mídia", "Atend."]); }
}
function drawAxes(ctx, width, height) { ctx.strokeStyle = "#252b36"; ctx.lineWidth = 1; for (let i = 1; i < 5; i += 1) { const y = i * height / 5; ctx.beginPath(); ctx.moveTo(30, y); ctx.lineTo(width - 10, y); ctx.stroke(); } }
function drawLine(ctx, width, height, values, color, padded) { const pad = padded ? 32 : 2, min = Math.min(...values), max = Math.max(...values), range = max - min || 1; ctx.strokeStyle = color; ctx.lineWidth = padded ? 2 : 3; ctx.lineJoin = "round"; ctx.beginPath(); values.forEach((value, index) => { const x = pad + index / Math.max(1, values.length - 1) * (width - pad * 1.4), y = height - pad - (value - min) / range * (height - pad * 1.7); if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke(); }
function drawBars(ctx, width, height, values, color, labels) { const pad = 28, max = Math.max(...values, 1), gap = 8, barWidth = Math.max(12, (width - pad * 2) / values.length - gap); ctx.font = "9px system-ui"; values.forEach((value, index) => { const x = pad + index * (barWidth + gap), barHeight = value / max * (height - 70), y = height - 34 - barHeight; ctx.fillStyle = color; ctx.fillRect(x, y, barWidth, barHeight); ctx.fillStyle = "#94a3b8"; ctx.save(); ctx.translate(x + barWidth / 2, height - 27); ctx.rotate(-.35); ctx.fillText(labels[index], -10, 0); ctx.restore(); }); }
function drawLegend(ctx, items) { ctx.font = "10px system-ui"; items.forEach(([label, color], index) => { ctx.fillStyle = color; ctx.fillRect(35 + index * 100, 8, 9, 9); ctx.fillStyle = "#94a3b8"; ctx.fillText(label, 49 + index * 100, 16); }); }

function openDrawer(title, rows) { $("#drawer-title").textContent = title; const content = $("#drawer-content"); clear(content); rows.forEach(([label, value]) => content.append(node("div", { class: "detail-row" }, [node("span", { text: label }), node("strong", { text: value })]))); content.append(node("p", { class: "last-update", text: "Dados DEMO. Em produção, o painel lateral consultará o endpoint de detalhe com autorização por entidade (IDOR)." })); $("#detail-drawer").showModal(); }
function field(label, type = "text", options = []) { const id = `field-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`; let input; if (options.length) { input = node("select", { id }); options.forEach((option) => input.append(node("option", { text: option, value: option }))); } else input = node("input", { id, type, required: true, autocomplete: "off" }); return node("label", {}, [text(label), input]); }
function openAction(action = $("#primary-action").textContent) { $("#action-title").textContent = action; const fields = $("#action-fields"); clear(fields); fields.className = "form-grid"; const normalized = action.toLocaleLowerCase("pt-PT"); const definitions = normalized.includes("lead") ? [["Nome"], ["Instagram / telefone PT"], ["Temperatura", "text", ["frio", "morno", "quente"]], ["Próxima ação"]] : normalized.includes("stock") ? [["SKU"], ["Tipo", "text", ["entrada", "saída", "ajuste", "perda"]], ["Quantidade", "number"], ["Motivo"]] : [["Lead / cliente"], ["SKU"], ["Quantidade", "number"], ["Estado", "text", ["reservado", "confirmado", "preparação", "enviado"]]]; definitions.forEach((definition) => fields.append(field(...definition))); $("#action-dialog").showModal(); }

const COMMANDS = [
  ["Criar pedido", "Pedido IG com baixa segura", () => openAction("Criar pedido")], ["Emitir relatório", "Exportação auditada", () => exportResource("orders")], ["Ver inadimplência / devoluções", "Pedidos CTT com prejuízo", () => navigate("ctt")], ["Alertas de stock", "Ruptura e mínimo", () => navigate("stock")], ["Reimprimir etiqueta CTT", "Operação CTT Portugal", () => openAction("Reimprimir etiqueta CTT")], ["Novo lead IG", "Registar contacto do Direct", () => openAction("Novo lead IG")], ["Abrir lead #", "Introduza o ID após o comando", () => navigate("leads")], ["Abrir pedido #", "Introduza o ID após o comando", () => navigate("sales")]
];
function openCommand() { $("#command-dialog").showModal(); $("#command-input").value = ""; renderCommandResults(""); requestAnimationFrame(() => $("#command-input").focus()); }
function renderCommandResults(query) { const results = $("#command-results"); clear(results); const normalized = query.toLocaleLowerCase("pt-PT"), filtered = COMMANDS.filter((command) => `${command[0]} ${command[1]}`.toLocaleLowerCase("pt-PT").includes(normalized)); filtered.forEach((command, index) => results.append(node("button", { class: `command-result ${index === 0 ? "selected" : ""}`, role: "option", onclick: () => { $("#command-dialog").close(); command[2](); } }, [node("span", { text: command[0] }), node("span", { text: command[1] })]))); }

async function exportResource(resource) { try { const rows = await dataService.export(resource); const csv = toCSV(rows), blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }), url = URL.createObjectURL(blob), link = node("a", { href: url, download: `realhype-${resource}-demo.csv` }); document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url); toast("Exportação DEMO criada e registrada no audit log."); } catch (error) { toast(error.message, "error"); } }
function toCSV(rows) { if (!rows.length) return ""; const keys = Object.keys(rows[0]); const escape = (value) => { const raw = String(value ?? ""), safe = /^[=+\-@]/.test(raw) ? `'${raw}` : raw; return `"${safe.replaceAll('"', '""')}"`; }; return [keys.map(escape).join(","), ...rows.map((row) => keys.map((key) => escape(row[key])).join(","))].join("\r\n"); }
function toast(message, tone = "success") { const item = node("div", { class: `toast ${tone === "error" ? "error" : ""}`, role: "status", text: message }); $("#toast-region").append(item); setTimeout(() => item.remove(), 4200); }
function updateTimes() { const label = `Atualizado ${new Intl.DateTimeFormat("pt-PT", { hour: "2-digit", minute: "2-digit", second: "2-digit", timeZone: state.filters.timezone }).format(state.updatedAt)}`; $("#last-update").textContent = label; $("#sidebar-updated").textContent = label; }

function bindFilters() {
  const mapping = { "filter-period": "period", "filter-unit": "unit", "filter-channel": "channel", "filter-category": "category", "filter-owner": "owner", "filter-status": "status", "filter-timezone": "timezone" };
  Object.entries(mapping).forEach(([id, key]) => { const input = $(`#${id}`); input.value = state.filters[key]; input.addEventListener("change", () => { state.filters[key] = input.value; localStorage.setItem("realhype.filters", JSON.stringify(state.filters)); render(); }); });
  $("#reset-filters").addEventListener("click", () => { state.filters = { period: "30", unit: "RealHype PT", channel: "all", category: "all", owner: "all", status: "all", timezone: "Europe/Lisbon" }; localStorage.setItem("realhype.filters", JSON.stringify(state.filters)); bindFilterValues(); render(); });
}
function bindFilterValues() { const ids = { "filter-period": "period", "filter-unit": "unit", "filter-channel": "channel", "filter-category": "category", "filter-owner": "owner", "filter-status": "status", "filter-timezone": "timezone" }; Object.entries(ids).forEach(([id, key]) => { $(`#${id}`).value = state.filters[key]; }); }
function changeRole(role) { state.role = role; localStorage.setItem("realhype.role", role); $("#role-label").textContent = ROLE_CONFIG[role].label; if (!ROLE_CONFIG[role].pages.includes(state.page)) state.page = ROLE_CONFIG[role].pages[0]; $("#owner-filter-wrap").classList.toggle("hidden", role === "ops"); buildNavigation(); render(); dataService.audit({ actor: "Operador Demo", role, action: "role_demo_changed", entity: role, result: "success" }); }

function bindEvents() {
  $("#toggle-sidebar").addEventListener("click", () => { const collapsed = $("#app-shell").classList.toggle("collapsed"); $("#toggle-sidebar").setAttribute("aria-expanded", String(!collapsed)); });
  $("#open-sidebar").addEventListener("click", () => $("#sidebar").classList.add("open")); $("#close-sidebar").addEventListener("click", () => $("#sidebar").classList.remove("open"));
  $("#open-command").addEventListener("click", openCommand); $("#command-input").addEventListener("input", (event) => renderCommandResults(event.target.value));
  $("#command-input").addEventListener("keydown", (event) => { const results = $$(".command-result", $("#command-results")); if (!results.length) return; let selected = results.findIndex((item) => item.classList.contains("selected")); if (["ArrowDown", "ArrowUp"].includes(event.key)) { event.preventDefault(); results[selected]?.classList.remove("selected"); selected = (selected + (event.key === "ArrowDown" ? 1 : -1) + results.length) % results.length; results[selected].classList.add("selected"); results[selected].scrollIntoView({ block: "nearest" }); } else if (event.key === "Enter") { event.preventDefault(); results[Math.max(0, selected)].click(); } });
  $("#close-drawer").addEventListener("click", () => $("#detail-drawer").close()); $("#primary-action").addEventListener("click", () => openAction());
  $("#role-select").value = state.role; $("#role-select").addEventListener("change", (event) => changeRole(event.target.value));
  $("#action-form").addEventListener("submit", async (event) => { event.preventDefault(); if (event.submitter?.value === "cancel") { $("#action-dialog").close(); return; } const action = $("#action-title").textContent; await dataService.quickAction(action.toLowerCase().replaceAll(" ", "_"), "demo"); $("#action-dialog").close(); toast(`${action}: ação DEMO registrada.`); });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openCommand(); }
    if (event.altKey && event.key.toLowerCase() === "n") { event.preventDefault(); openAction(); }
    if (event.altKey && event.key.toLowerCase() === "r") { event.preventDefault(); render(); }
    if (!["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName) && ["j", "k"].includes(event.key.toLowerCase())) { const rows = $$("[data-queue-row]"); if (!rows.length) return; event.preventDefault(); state.selectedQueueIndex = Math.max(0, Math.min(rows.length - 1, state.selectedQueueIndex + (event.key.toLowerCase() === "j" ? 1 : -1))); rows.forEach((row, index) => row.tabIndex = index === state.selectedQueueIndex ? 0 : -1); rows[state.selectedQueueIndex].focus(); }
  });
  window.addEventListener("resize", debounce(() => $$(`canvas[data-chart]`).forEach(drawChart), 180));
}

function startClock() { const tick = () => { $("#clock").textContent = new Intl.DateTimeFormat("pt-PT", { dateStyle: "short", timeStyle: "short", timeZone: state.filters.timezone }).format(new Date()); }; tick(); setInterval(tick, 30000); }
function init() { bindEvents(); bindFilters(); changeRole(state.role); startClock(); }
init();
