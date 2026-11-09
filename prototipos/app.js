const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function showToast(message) {
  const toast = $("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 3200);
}

function openModal(modal) {
  modal?.classList.add("open");
  $("button", modal)?.focus();
}

function closeModal(modal) {
  modal?.classList.remove("open");
}

function initPreventa() {
  const customers = $$(".customer");
  const detail = {
    name: $("#detail-name"),
    meta: $("#detail-meta"),
    date: $("#detail-date"),
    value: $("#detail-value"),
    score: $("#detail-score"),
    bar: $("#confidence-bar"),
    product: $("#detail-product"),
    code: $("#detail-code"),
    units: $("#detail-units"),
    liters: $("#detail-liters")
  };

  customers.forEach(customer => customer.addEventListener("click", () => {
    customers.forEach(item => item.classList.remove("active"));
    customer.classList.add("active");
    const d = customer.dataset;
    detail.name.textContent = d.name;
    detail.meta.innerHTML = `${d.type}<br>${d.zone}`;
    detail.date.textContent = d.date;
    detail.value.textContent = d.value;
    detail.score.textContent = `${d.score} %`;
    detail.bar.style.width = `${d.score}%`;
    detail.bar.style.background = Number(d.score) >= 80 ? "var(--green)" : "#d88a12";
    detail.product.textContent = d.product;
    detail.code.textContent = d.product.slice(0, 4);
    detail.units.textContent = d.units;
    detail.liters.textContent = d.liters;
  }));

  $("#confidence-filter")?.addEventListener("change", event => {
    const selected = event.target.value;
    customers.forEach(customer => {
      customer.hidden = selected !== "all" && customer.dataset.confidence !== selected;
    });
  });

  $("#search-button")?.addEventListener("click", () => showToast("En el MVP, aquí se buscará por cliente, zona o material."));

  const modal = $("#proposal-modal");
  $("#send-proposal")?.addEventListener("click", () => {
    const selected = $(".customer.active")?.dataset;
    if (selected) {
      $("#modal-copy").textContent = `Hola, ${selected.name}. Según vuestro ritmo habitual, os proponemos reponer ${selected.units} de ${selected.product}. Podéis confirmar, modificar o posponer en un clic.`;
    }
    openModal(modal);
  });
  $("#review-detail")?.addEventListener("click", () => showToast("La propuesta está abierta para editar fecha, líneas y cantidades."));
  $$("[data-close-modal]", modal).forEach(button => button.addEventListener("click", () => closeModal(modal)));
  $("#confirm-send")?.addEventListener("click", () => {
    closeModal(modal);
    showToast("Propuesta enviada y registrada para trazabilidad.");
  });
  modal?.addEventListener("click", event => {
    if (event.target === modal) closeModal(modal);
  });
}

function initCliente() {
  const rows = $$(".product-row");
  const euro = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });

  function updateSummary() {
    let products = 0;
    let total = 0;
    let liters = 0;
    rows.forEach(row => {
      const quantity = Number($("output", row).textContent);
      if (quantity > 0) products += 1;
      total += quantity * Number(row.dataset.price);
      liters += quantity * Number(row.dataset.liters);
      row.style.opacity = quantity === 0 ? ".48" : "1";
    });
    $("#summary-products").textContent = String(products);
    $("#summary-liters").textContent = `${Math.round(liters)} L`;
    $("#summary-total").textContent = euro.format(total);
  }

  $$(".stepper button").forEach(button => button.addEventListener("click", () => {
    const output = button.parentElement.querySelector("output");
    output.textContent = String(Math.max(0, Math.min(9, Number(output.textContent) + Number(button.dataset.step))));
    updateSummary();
  }));

  const modal = $("#order-modal");
  $("#confirm-order")?.addEventListener("click", () => openModal(modal));
  $("#postpone-order")?.addEventListener("click", () => showToast("Te lo recordaremos dentro de 48 horas."));
  $$("[data-close-modal]", modal).forEach(button => button.addEventListener("click", () => closeModal(modal)));
  $("#finish-order")?.addEventListener("click", () => {
    closeModal(modal);
    showToast("Propuesta preparada. En producción se abrirá WhatsApp.");
  });
  modal?.addEventListener("click", event => {
    if (event.target === modal) closeModal(modal);
  });
  updateSummary();
}

document.addEventListener("keydown", event => {
  if (event.key === "Escape") $$(".modal.open").forEach(closeModal);
});

if (document.body.dataset.page === "preventa") initPreventa();
if (document.body.dataset.page === "cliente") initCliente();
