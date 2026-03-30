// Eski xato manzilni o'chirib, buni yozing:
const API_URL = window.location.origin;
function el(id) {
  return document.getElementById(id);
}

function showError(boxId, message) {
  const box = el(boxId);
  if (!box) return;
  box.textContent = message;
  box.style.display = "block";
}

function hideError(boxId) {
  const box = el(boxId);
  if (!box) return;
  box.textContent = "";
  box.style.display = "none";
}

// --- BU QISMNI NUSXALAB, ESKI apiPost/apiGet LARNI O'RNIGA QO'YING ---

async function apiPostMultipart(path, formData) {
  // Boshiga ${API_URL} qo'shildi, shunda so'rov Renderga ketadi
  const resp = await fetch(`${API_URL}${path}`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(resp);
}

async function apiPost(path, payload) {
  const resp = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(resp);
}

async function apiGet(path) {
  const resp = await fetch(`${API_URL}${path}`);
  return handleResponse(resp);
}

// Barcha xatolarni bir joyda tekshirish uchun yordamchi funksiya
async function handleResponse(resp) {
  const text = await resp.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }

  if (!resp.ok) {
    const msg = data && data.detail ? data.detail : `Xato: ${resp.status}`;
    throw new Error(msg);
  }
  return data;
}
  return data;

async function apiGet(path) {
  const resp = await fetch(path);
  const text = await resp.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null; 
  } catch (_) {
    data = text;
  }
  if (!resp.ok) {
    const msg = data && data.detail ? data.detail : `Request failed: ${resp.status}`;
    throw new Error(msg);
  }
  return data;
}

function setupLoginPage() {
  const loginForm = el("loginForm");
  const registerForm = el("registerForm");
  if (!loginForm && !registerForm) return;

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideError("loginError");

      const login = el("loginInput").value.trim();
      const password = el("passwordInput").value;

      try {
        const data = await apiPost("/students/login", { login, password });
        localStorage.setItem("studentId", String(data.student_id));
        localStorage.setItem("studentEmail", data.email || "");
        window.location.href = "/frontend/dashboard.html";
      } catch (err) {
        showError("loginError", err.message);
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideError("registerError");

      const payload = {
        first_name: el("regFirstName").value.trim(),
        last_name: el("regLastName").value.trim(),
        email: el("regEmail").value.trim(),
        login: el("regLogin").value.trim(),
        password: el("regPassword").value,
        grades: [],
      };

      try {
        // POST /students/
        await apiPost("/students/", payload);
        // Auto-fill login with the same credentials
        el("loginInput").value = payload.login;
        el("passwordInput").value = payload.password;
        alert("Student yaratildi. Endi login bilan kirib ko'ring.");
      } catch (err) {
        showError("registerError", err.message);
      }
    });
  }
}

function renderEvents(events) {
  const box = el("eventsBox");
  if (!box) return;

  if (!events || events.length === 0) {
    box.innerHTML = '<div class="muted">Hozircha eventlar yo\'q.</div>';
    return;
  }

  box.innerHTML = "";

  events.forEach((ev) => {
    const imgPart = ev.image_url
      ? `<img class="image" src="${ev.image_url}" alt="${ev.name || "image"}" />`
      : `<div class="muted">Rasm yo\'q</div>`;

    const card = document.createElement("div");
    card.className = "card";
    card.style.width = "320px";
    card.innerHTML = `
      <div style="font-weight: 700; margin-bottom: 6px">${ev.name || "Event"}</div>
      <div class="muted" style="margin-bottom: 8px">score: ${ev.score ?? ""}</div>
      <div>${imgPart}</div>
    `;
    box.appendChild(card);
  });
}

async function loadEvidenceSummary() {
  const sid = localStorage.getItem("studentId");
  const box = el("evidenceSummaryBox");
  if (!box) return;
  if (!sid) {
    box.innerHTML = '<div class="muted">Kirish talab qilinadi.</div>';
    return;
  }
  try {
    const data = await apiGet(`/students/${sid}/evidence-summary`);
    const rows = (data.sections || [])
      .map((s) => {
        const prefix =
          s.grant_criterion_id != null ? `${s.grant_criterion_id}. ` : "";
        return `<li>${prefix}${escapeHtml(s.name)}: <b>${s.image_count}</b>/${s.max_images} (qoldiq: ${s.remaining_slots})</li>`;
      })
      .join("");
    box.innerHTML = `
      <div><b>Jami yig‘ilgan rasmlar:</b> ${data.total_images}</div>
      <div class="muted" style="margin-top: 6px">Har bo‘limda maks. ${data.max_images_per_section} ta; rasm hajmi maks. ${data.max_image_size_mb} MB.</div>
      <ul style="margin-top: 8px; padding-left: 18px">${rows || "<li class='muted'>Hozircha section yo‘q.</li>"}</ul>
    `;
  } catch (e) {
    box.innerHTML = `<div class="error" style="display:block">${escapeHtml(e.message)}</div>`;
  }
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function updateSelectedSectionHint() {
  const select = el("sectionSelect");
  const hint = el("selectedSectionHint");
  if (!select || !hint) return;
  const id = select.value;
  if (!id) {
    hint.textContent =
      "Bo‘lim tanlang — stats, tadbirlar va yangi rasm yuklash shu tanlangan bo‘lim uchun ishlaydi.";
    return;
  }
  const opt = select.options[select.selectedIndex];
  hint.textContent = `Tanlangan bo‘lim: ${opt ? opt.textContent : "#" + id} — ko‘rsatiladigan va qo‘shiladigan tadbir/rasmlar faqat shu bo‘limga tegishli.`;
}

function renderSections(sections) {
  const select = el("sectionSelect");
  if (!select) return;
  select.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Bo‘limni tanlang...";
  select.appendChild(placeholder);

  (sections || []).forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    const label =
      s.grant_criterion_id != null
        ? `${s.grant_criterion_id}. ${s.name}`
        : `${s.name} (#${s.id})`;
    opt.textContent = label;
    select.appendChild(opt);
  });
  updateSelectedSectionHint();
}

function setupDashboardPage() {
  const studentId = localStorage.getItem("studentId");
  const welcomeLine = el("welcomeLine");
  if (welcomeLine && studentId) {
    welcomeLine.textContent = `student_id: ${studentId}`;
  }

  const sectionSelect = el("sectionSelect");
  const statsBox = el("statsBox");
  const eventsBox = el("eventsBox");
  if (!sectionSelect || !statsBox || !eventsBox) return;

  if (!studentId) {
    window.location.href = "/frontend/login.html";
    return;
  }

  async function loadSections() {
    const sections = await apiGet(`/students/${studentId}/sections`);
    renderSections(sections);
  }

  sectionSelect.addEventListener("change", updateSelectedSectionHint);

  el("loadStatsBtn").addEventListener("click", async () => {
    const sectionId = sectionSelect.value;
    if (!sectionId) {
      statsBox.innerHTML = '<div class="muted">Section tanlang.</div>';
      return;
    }
    statsBox.innerHTML = '<div class="muted">Loading...</div>';
    const stats = await apiGet(`/students/sections/${sectionId}/stats`);
    statsBox.innerHTML = `
      <div><b>${stats.section_name}</b></div>
      <div class="muted" style="margin-top: 6px">total_events: ${stats.total_events}</div>
      <div class="muted" style="margin-top: 6px">total_images: ${stats.total_images}</div>
      <div class="muted" style="margin-top: 6px">participation entries: ${stats.participation.length}</div>
    `;
  });

  el("loadEventsBtn").addEventListener("click", async () => {
    const sectionId = sectionSelect.value;
    if (!sectionId) {
      eventsBox.innerHTML = '<div class="muted">Section tanlang.</div>';
      return;
    }
    eventsBox.innerHTML = '<div class="muted">Loading...</div>';
    const events = await apiGet(`/students/sections/${sectionId}/events`);
    renderEvents(events);
  });

  el("createEventForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError("eventCreateError");

    const sectionId = sectionSelect.value;
    if (!sectionId) {
      showError("eventCreateError", "Section tanlang.");
      return;
    }

    const name = el("newEventName").value.trim();
    const score_100 = Number(el("newEventScore").value);
    const fileInput = el("newEventImageFile");
    const urlVal = el("newEventImageUrl").value.trim();

    try {
      if (fileInput && fileInput.files && fileInput.files[0]) {
        const fd = new FormData();
        fd.append("name", name);
        fd.append("score_100", String(score_100));
        fd.append("image", fileInput.files[0]);
        await apiPostMultipart(`/students/sections/${sectionId}/events/upload`, fd);
        fileInput.value = "";
      } else {
        const payload = { name, score_100, image_url: urlVal || null };
        await apiPost(`/students/sections/${sectionId}/events`, payload);
      }
      el("newEventName").value = "Event 1";
      el("newEventScore").value = 90;
      el("newEventImageUrl").value = "";
      const events = await apiGet(`/students/sections/${sectionId}/events`);
      renderEvents(events);
      await loadEvidenceSummary();
    } catch (err) {
      showError("eventCreateError", err.message);
    }
  });

  loadEvidenceSummary().catch(() => {});
  loadSections().catch((err) => {
    statsBox.innerHTML = `<div class="error" style="display:block">${err.message}</div>`;
  });
}

setupLoginPage();
setupDashboardPage();

