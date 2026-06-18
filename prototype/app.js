const pages=['Command Center','Leads / CRM','Vendas','CTT / Pedidos','Stock','Produtos','Financeiro','Growth','Alertas','Configurações'];
document.querySelector('#nav').innerHTML=pages.map((p,i)=>`<button class="${i===0?'active':''}">${p}</button>`).join('');
const metrics=[['Receita hoje','R$ 4.850,00'],['Lucro estimado','R$ 2.310,00'],['Leads hoje','28'],['Vendas hoje','7'],['Conversão','25,0%'],['Pedidos pendentes','5'],['Stock crítico','3'],['Risco CTT','2']];
document.querySelector('#metrics').innerHTML=metrics.map(([l,v])=>`<div class="metric"><span>${l}</span><strong>${v}</strong></div>`).join('');
document.querySelector('#actions').innerHTML=['Confirmar dados de 2 pedidos','Repor 3 SKUs críticos','Responder 4 leads quentes'].map(x=>`<div class="item"><span class="badge">ATENÇÃO</span> ${x}</div>`).join('');
document.querySelector('#activity').innerHTML=['Pedido DEMO-104 atualizado','Lead fictício avançou no funil','Entrada demo de stock'].map(x=>`<div class="item">${x}</div>`).join('');
document.querySelector('#rows').innerHTML=[['Lead Demo A','quente','SDR Demo','Enviar catálogo'],['Pedido DEMO-104','aguardando','Operação Demo','Validar morada'],['SKU-DEMO-01','stock baixo','Partner Demo','Repor stock']].map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('');
