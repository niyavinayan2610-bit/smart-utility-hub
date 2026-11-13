const converter = document.querySelector("#converter");
if (converter) {
  const units = JSON.parse(converter.dataset.units);
  const category = document.querySelector("#category");
  const source = document.querySelector("#source");
  const target = document.querySelector("#target");

  category.addEventListener("change", () => {
    const choices = Object.entries(units[category.value]);
    for (const select of [source, target]) {
      select.replaceChildren(...choices.map(([symbol, [label]]) =>
        new Option(`${label} (${symbol})`, symbol)
      ));
    }
    target.selectedIndex = 1;
  });

  document.querySelector("#swap").addEventListener("click", () => {
    [source.value, target.value] = [target.value, source.value];
  });
}

const billing = document.querySelector("#billing");
if (billing) {
  const items = document.querySelector("#items");
  const add = document.querySelector("#add-item");
  const maxItems = Number(billing.dataset.maxItems);

  function updateRows() {
    const rows = [...items.children];
    add.disabled = rows.length >= maxItems;
    rows.forEach((row, index) => {
      row.querySelector("legend").textContent = `Item ${index + 1}`;
      const remove = row.querySelector(".remove-item");
      remove.disabled = rows.length === 1;
      remove.setAttribute("aria-label", `Remove item ${index + 1}`);
    });
  }

  add.addEventListener("click", () => {
    const row = items.firstElementChild.cloneNode(true);
    for (const input of row.querySelectorAll("input")) {
      input.value = input.name === "quantity" ? "1" : "";
    }
    items.append(row);
    updateRows();
    row.querySelector("input").focus();
  });

  items.addEventListener("click", (event) => {
    const remove = event.target.closest(".remove-item");
    if (!remove || items.children.length < 2) return;
    const row = remove.closest(".item");
    const focusRow = row.nextElementSibling || row.previousElementSibling;
    row.remove();
    updateRows();
    focusRow.querySelector("input").focus();
  });

  updateRows();
  const invoice = document.querySelector("#invoice");
  if (invoice) {
    document.querySelector("#print-invoice").addEventListener("click", () => window.print());
    invoice.focus();
  }
}
