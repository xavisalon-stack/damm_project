const data = window.DAMM_DATA;

const money = (v, compact = false) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency", currency: "EUR",
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: compact ? 1 : 0
  }).format(v);
const number = (v, compact = false) =>
  new Intl.NumberFormat("es-ES", {
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: compact ? 1 : 0
  }).format(v);
const decimal = v => new Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 }).format(v);

function lineChart(element, rows, key) {
  const width = 760, height = 220, px = 18, py = 25;
  const values = rows.map(r => Number(r[key]));
  const min = Math.min(...values) * .94;
  const max = Math.max(...values) * 1.04;
  const x = i => px + i * (width - px * 2) / (rows.length - 1);
  const y = v => height - py - (v - min) / (max - min || 1) * (height - py * 2);
  const points = values.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  const area = `${px},${height-py} ${points} ${width-px},${height-py}`;
  const labels = rows.map((r, i) =>
    i % 2 === 0 ? `<text x="${x(i)}" y="${height}" text-anchor="middle" class="chart-label">${r.mes.slice(5)}</text>` : ""
  ).join("");
  const grid = [0, 1, 2, 3].map(i => {
    const yy = py + i * (height - py * 2) / 3;
    return `<line x1="${px}" y1="${yy}" x2="${width-px}" y2="${yy}" class="chart-grid"/>`;
  }).join("");
  element.innerHTML = `<svg viewBox="0 0 ${width} ${height+8}" role="img" aria-label="Evolución mensual">
    <defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8b1830"/><stop offset="1" stop-color="#8b1830" stop-opacity="0"/></linearGradient></defs>
    ${grid}<polygon points="${area}" class="chart-area"/><polyline points="${points}" class="chart-line"/>
    ${values.map((v,i) => `<circle cx="${x(i)}" cy="${y(v)}" r="3.5" class="chart-dot"><title>${rows[i].mes}: ${number(v, true)}</title></circle>`).join("")}${labels}
  </svg>`;
}

function bars(element, rows, valueKey, nameKey, formatter = v => number(v, true)) {
  const max = Math.max(...rows.map(r => Number(r[valueKey])));
  element.innerHTML = rows.map(r => `
    <div class="bar-row">
      <div class="bar-name" title="${r[nameKey]}">${r[nameKey]}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${Number(r[valueKey]) / max * 100}%"></div></div>
      <div class="bar-value">${formatter(r[valueKey])}</div>
    </div>`).join("");
}

function initPreventa() {
  const p = data.preventa;
  document.querySelector("#kpi-venta").textContent = money(p.kpis.venta, true);
  document.querySelector("#kpi-margen").textContent = money(p.kpis.margen, true);
  document.querySelector("#kpi-litros").textContent = number(p.kpis.litros, true);
  document.querySelector("#kpi-puntos").textContent = number(p.kpis.establecimientos);
  document.querySelector("#periodo").textContent = data.meta.preventaPeriodo;
  document.querySelector("#cobertura").textContent = `${decimal(p.coberturaDigital)}%`;
  lineChart(document.querySelector("#ventas-chart"), p.tendencia, "venta");
  bars(document.querySelector("#materiales"), p.materiales, "venta", "Material", v => money(v, true));
  bars(document.querySelector("#tipos"), p.tipos, "establecimientos", "tipo");
  document.querySelector("#oportunidades").innerHTML = p.oportunidades.map((o, i) => `
    <tr><td><span class="rank">${i + 1}</span></td><td class="name-cell">${o.nombre}<div class="card-sub">${o.ciudad}</div></td>
    <td><span class="tag">${o.categoria}</span></td><td>${o.tipo}</td><td>${number(o.interior)} + ${number(o.terraza)} terraza</td><td>${o.zona}</td></tr>`).join("");
  const menu = document.querySelector(".mobile-menu");
  const sidebar = document.querySelector(".sales-sidebar");
  menu?.addEventListener("click", () => {
    const open = sidebar.classList.toggle("mobile-open");
    menu.setAttribute("aria-expanded", String(open));
  });
  sidebar?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => sidebar.classList.remove("mobile-open")));
}

function renderBrands(rows) {
  const target = document.querySelector("#marcas-tabla");
  target.innerHTML = rows.map((m, i) => `
    <tr><td><span class="rank">${i + 1}</span></td><td class="name-cell">${m.marca.replaceAll(".", " ")}</td>
    <td>${number(m.litros, true)} L</td><td>${money(m.valor, true)}</td><td>${decimal(m.precio)} €/L</td>
    <td><span class="tag">${decimal(m.promo)}% promo</span></td></tr>`).join("");
}

function initConsumidor() {
  const c = data.consumidor;
  document.querySelector("#kpi-litros").textContent = number(c.kpis.litrosDamm, true);
  document.querySelector("#kpi-valor").textContent = money(c.kpis.valorDamm, true);
  document.querySelector("#kpi-marcas").textContent = number(c.kpis.marcas);
  document.querySelector("#kpi-precio").textContent = `${decimal(c.kpis.precioMedio)} €/L`;
  document.querySelector("#periodo").textContent = data.meta.consumidorPeriodo;
  lineChart(document.querySelector("#consumo-chart"), c.tendencia, "litros");
  bars(document.querySelector("#segmentos"), c.segmentos, "litros", "segmento");
  bars(document.querySelector("#formatos"), c.formatos, "litros", "envase");
  renderBrands(c.marcas);
  document.querySelector("#destacados").innerHTML = c.destacados.map(m => `
    <article class="product-card"><div class="product-icon" aria-hidden="true"></div><div>
      <div class="product-name">${m.marca.replaceAll(".", " ")}</div>
      <div class="product-meta">${number(m.litros, true)} litros en la muestra</div>
      <div class="product-price">${decimal(m.precio)} €/L medio</div>
    </div></article>`).join("");
  document.querySelectorAll(".filter").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    const mode = button.dataset.sort;
    const sorted = [...c.marcas].sort((a,b) => mode === "precio" ? a.precio - b.precio : b[mode] - a[mode]);
    renderBrands(sorted);
  }));
}

if (document.body.dataset.page === "preventa") initPreventa();
if (document.body.dataset.page === "consumidor") initConsumidor();
