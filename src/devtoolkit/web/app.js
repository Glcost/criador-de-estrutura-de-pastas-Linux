const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = {
  files: [],
  selectedFile: null,
  toastTimeout: null,
};

const templateLabels = {
  python: "Python",
  node: "Node.js",
  web: "Web",
  api: "API",
  react: "React",
};

function getFormData() {
  return {
    name: $("#project-name").value.trim(),
    template: $('input[name="template"]:checked').value,
    destination: $("#project-destination").value.trim(),
  };
}

function showToast(message, type = "") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast visible ${type}`.trim();
  clearTimeout(state.toastTimeout);
  state.toastTimeout = setTimeout(() => {
    toast.className = "toast";
  }, 4200);
}

function setMessage(message, type = "") {
  const element = $("#form-message");
  element.textContent = message;
  element.className = `form-message ${type}`.trim();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string"
      ? payload.detail
      : "Não foi possível concluir a solicitação.";
    throw new Error(detail);
  }
  return payload;
}

function setView(viewName) {
  $$(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `view-${viewName}`);
  });
  $$(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  $("#breadcrumb-current").textContent = viewName === "create"
    ? "Criar projeto"
    : "Visão geral";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function chooseTemplate(template) {
  const radio = $(`input[name="template"][value="${template}"]`);
  if (!radio) return;
  radio.checked = true;
  $$(".template-option").forEach((option) => {
    option.classList.toggle("selected", option.contains(radio));
  });
  setView("create");
  $("#project-name").focus();
  clearPreview();
}

function clearPreview() {
  state.files = [];
  state.selectedFile = null;
  $("#preview-empty").classList.remove("hidden");
  $("#file-preview").classList.add("hidden");
  $("#preview-count").textContent = "0 arquivos";
}

function renderPreview(payload) {
  state.files = payload.files;
  state.selectedFile = state.files[0]?.path ?? null;
  $("#preview-root-name").textContent = payload.name;
  $("#preview-count").textContent = `${state.files.length} arquivo${state.files.length === 1 ? "" : "s"}`;
  $("#preview-empty").classList.add("hidden");
  $("#file-preview").classList.remove("hidden");

  const fileList = $("#file-list");
  fileList.replaceChildren();
  state.files.forEach((file) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `file-row${file.path === state.selectedFile ? " selected" : ""}`;
    const icon = document.createElement("span");
    icon.className = "file-icon";
    icon.textContent = file.path.startsWith(".") ? "·" : "⌑";
    const name = document.createElement("span");
    name.textContent = file.path;
    button.append(icon, name);
    button.addEventListener("click", () => selectPreviewFile(file.path));
    fileList.append(button);
  });
  selectPreviewFile(state.selectedFile);
}

function selectPreviewFile(path) {
  const file = state.files.find((item) => item.path === path);
  if (!file) return;
  state.selectedFile = path;
  $$(".file-row").forEach((button) => {
    button.classList.toggle("selected", button.textContent.trim() === path);
  });
  $("#selected-file-name").textContent = file.path;
  $("#selected-file-content").textContent = file.content;
}

async function previewProject() {
  const form = $("#project-form");
  if (!form.reportValidity()) return;
  setMessage("Preparando pré-visualização...");
  $("#preview-button").disabled = true;
  try {
    const payload = await apiRequest("/api/preview", {
      method: "POST",
      body: JSON.stringify(getFormData()),
    });
    renderPreview(payload);
    setMessage("Pré-visualização atualizada. Nenhum arquivo foi criado.");
  } catch (error) {
    setMessage(error.message, "error");
    showToast(error.message, "error");
  } finally {
    $("#preview-button").disabled = false;
  }
}

async function createProject(event) {
  event.preventDefault();
  const form = $("#project-form");
  if (!form.reportValidity()) return;
  const button = $("#create-button");
  button.disabled = true;
  button.innerHTML = "Criando...";
  setMessage("Criando os arquivos no sistema local...");
  try {
    const payload = await apiRequest("/api/create", {
      method: "POST",
      body: JSON.stringify(getFormData()),
    });
    setMessage(`${payload.message} Caminho: ${payload.path}`, "success");
    showToast(`Projeto criado em ${payload.path}`);
    await previewProject();
    setMessage(`Projeto criado com sucesso em: ${payload.path}`, "success");
  } catch (error) {
    setMessage(error.message, "error");
    showToast(error.message, "error");
  } finally {
    button.disabled = false;
    button.innerHTML = 'Criar projeto <span>→</span>';
  }
}

function renderDiagnostics(payload) {
  const checks = payload.checks;
  const os = checks.find((item) => item.name === "Sistema operacional");
  const disk = checks.find((item) => item.name === "Espaço em disco");
  const tools = checks.filter((item) => ["git", "python3", "node", "npm"].includes(item.name));
  const installed = tools.filter((item) => item.available).length;
  const cards = [
    {
      label: "Sistema operacional",
      value: os?.available ? "Detectado" : "Verificar",
      detail: os?.details ?? "Não foi possível identificar o sistema",
      icon: "⌘",
      tone: os?.available ? "good" : "warn",
    },
    {
      label: "Ferramentas instaladas",
      value: `${installed} / ${tools.length}`,
      detail: tools.map((item) => `${item.name}: ${item.available ? "OK" : "ausente"}`).join(" · "),
      icon: "⌁",
      tone: installed === tools.length ? "good" : "warn",
    },
    {
      label: "Espaço em disco",
      value: disk?.details.match(/[\d.]+\s*GiB/)?.[0] ?? "Indisponível",
      detail: disk?.available ? "Espaço livre suficiente" : "Verifique o espaço disponível",
      icon: "▤",
      tone: disk?.available ? "good" : "warn",
    },
  ];

  const summary = $("#diagnostic-summary");
  summary.replaceChildren();
  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "stat-card";
    const top = document.createElement("div");
    top.className = "stat-top";
    const label = document.createElement("span");
    label.textContent = card.label;
    const icon = document.createElement("span");
    icon.className = "stat-icon";
    icon.textContent = card.icon;
    top.append(label, icon);
    const value = document.createElement("strong");
    value.className = "stat-value";
    value.textContent = card.value;
    value.style.color = card.tone === "warn" ? "var(--red)" : "var(--text)";
    const detail = document.createElement("small");
    detail.textContent = card.detail;
    article.append(top, value, detail);
    summary.append(article);
  });
}

async function loadDiagnostics() {
  $("#refresh-diagnostics").disabled = true;
  try {
    renderDiagnostics(await apiRequest("/api/diagnostics"));
  } catch (error) {
    showToast(`Falha no diagnóstico: ${error.message}`, "error");
  } finally {
    $("#refresh-diagnostics").disabled = false;
  }
}

function init() {
  $("#project-destination").value = `${window.location.origin ? "~" : ""}/Projetos`;
  // Use the home directory as a friendly default. The backend expands "~".
  $("#project-destination").value = "~/Projetos";

  $$(".nav-item").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });
  $("#go-create").addEventListener("click", () => setView("create"));
  $("#welcome-create").addEventListener("click", () => setView("create"));
  $("#all-templates").addEventListener("click", () => setView("create"));
  $$(".template-card").forEach((button) => {
    button.addEventListener("click", () => chooseTemplate(button.dataset.template));
  });
  $$(".template-option input").forEach((radio) => {
    radio.addEventListener("change", () => {
      $$(".template-option").forEach((option) => {
        option.classList.toggle("selected", option.contains(radio) && radio.checked);
      });
      clearPreview();
    });
  });
  $("#preview-button").addEventListener("click", previewProject);
  $("#project-form").addEventListener("submit", createProject);
  $("#refresh-diagnostics").addEventListener("click", loadDiagnostics);
  $("#project-name").addEventListener("input", () => setMessage(""));
  loadDiagnostics();
}

document.addEventListener("DOMContentLoaded", init);
