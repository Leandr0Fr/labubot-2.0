// Genera las maquetas NN-*.html (una por pantalla) y la galería ../index.html.
// Uso: node docs/telegram/capturas/src/build.mjs  (capturar.sh lo corre antes de capturar)
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

// ---------- textos de src/telegram/constants.py, con los nombres de diseno.md §4 ----------
const T = {
  WELCOME_PENDING:
    "👋 Hola {first_name}. Soy labubot: busco ofertas en 11 portales y te mando las que encajan con tu perfil.\nTu solicitud quedó pendiente: te aviso cuando la apruebe el admin.",
  STILL_PENDING: "⏳ Tu solicitud sigue pendiente.",
  ADMIN_REQUEST: "🆕 Solicitud de acceso\n{first_name} (@{username})\nchat_id {chat_id}",
  ADMIN_APPROVED: "✅ Aprobada: {first_name} (@{username})",
  APPROVED:
    "✅ ¡Listo, ya tenés acceso!\nMandame tu CV con /perfil: lo uso para decidir qué ofertas te sirven.",
  ASK_PROFILE: "📄 Mandame tu perfil como texto o como archivo .md / .txt. Reemplaza al anterior.",
  PROFILE_SAVED: "📄 Perfil guardado ({chars} caracteres). Desde la próxima corrida te mando ofertas.",
  SETTINGS_PANEL:
    "⚙️ Tu configuración\nTérminos: {terms} · Bloqueadas: {blocked} · Perfil: {profile_mark} · Alertas: {alerts}",
  // El ASK_LIST del contrato da "los palabras separados": va concordado, como en diseno.md §4.
  ASK_LIST: "Mandame {what} por coma.",
  // El encabezado con el conteo es inventado: el contrato solo pide la lista separada por " · ".
  TERMS_LIST: "🔎 Términos ({count})\n{items}",
  BLOCKED_LIST: "🚫 Bloqueadas ({count})\n{items}",
  ADDED: "Agregados: {items}. Ahora tenés {count}.",
  PAUSED: "⏸ Alertas pausadas. Usá /reanudar cuando quieras volver.",
  RESUMED: "▶️ Alertas activas de nuevo.",
  OFFER: "{emoji} {title}\n{url}",
  KEYWORD_HEADER: 'Búsqueda palabra "{term}":',
  NO_MATCHES: "No se encontraron coincidencias.",
  OTHER_PORTALS_HEADER: "Otros portales:",
  OTHER_PORTALS: "Otros portales",
  SUMMARY_TITLE: "Resumen corrida ({start} - {end}):",
  SUMMARY_LINE: "{term}: {counts}",
  SUMMARY_GREENS: ["{count} verde encontrado", "{count} verdes encontrados"],
  SUMMARY_YELLOWS: ["{count} amarillo encontrado", "{count} amarillos encontrados"],
  SUMMARY_EMPTY: "{term}: No encontramos coincidencias",
  USERS_HEADER: "👥 Usuarios ({count})",
  USER_LINE: "{first_name}{username}\n{status} · {chat_id}",
};

const fill = (template, values) =>
  template.replace(/\{(\w+)\}/g, (_, key) => String(values[key]));

// ---------- datos de la historia ----------
const LUCIA = { first_name: "Lucía", username: "lucia_dev", chat_id: 6203418857 };

// Semilla real: DEFAULT_TERMS y DEFAULT_BLOCKED_TITLE_WORDS (hoy TERMS y BLOCKED_TITLE_WORDS
// de src/config/search.py), en el orden en que las devuelve SQLite por la PK.
const DEFAULT_TERMS = [
  "python", "fastapi", "desarrollador python", "python developer", "backend",
  "desarrollador backend", "backend developer", "desarrollador", "programador", "developer",
  "software engineer", "ingeniero de software", "analista programador", "desarrollador jr",
  "desarrollador junior", "programador jr", "programador junior", "junior developer",
  "desarrollador semi senior", "ssr developer", "web scraping", "integraciones",
].sort();
const DEFAULT_BLOCKED = [
  "sap", "abap", "salesforce", "cobol", "sharepoint", ".net", "c#", "php", "recruiter",
  "reclutador", "comercial", "ventas", "vendedor", "marketing", "contable", "rrhh", "frontend",
  "front-end", "front end", "angular", "vue", "director", "head of", "manager", "lead", "líder",
  "lider", "jefe", "soporte", "support", "helpdesk", "mesa de ayuda",
].sort();

// La corrida de las 11:00, la primera de Lucía: sus 🟢🟡 bajo la primera de sus palabras
// (en orden alfabético) que las trajo; null = otros portales. Bumeran, EmpleosIT y Jobicy
// no buscan: su palabra sale del título. Las palabras compuestas no se quedan con nada,
// porque la más corta va antes y su búsqueda ya trajo esas ofertas.
const RUN_11 = new Map([
  ["analista programador", [
    ["🟡", "Analista Programador Python Jr",
      "https://ar.linkedin.com/jobs/view/analista-programador-python-jr-4485402917"],
  ]],
  ["backend", [
    ["🟢", "Desarrollador/a Python Backend (FastAPI) - Remoto",
      "https://ar.linkedin.com/jobs/view/desarrollador-python-backend-fastapi-remoto-4485437208"],
    ["🟡", "Backend Developer Ssr (Python / Django)", "https://ar.indeed.com/viewjob?jk=5d2e8a1b47c0f39e"],
  ]],
  ["desarrollador", [
    ["🟡", "Desarrollador Python Jr - Automatizaciones", "https://www.bumeran.com.ar/empleos/1118489713.html"],
    ["🟢", "Desarrollador Python Semi Senior (Web Scraping)", "https://ar.talent.com/view?id=643889417520386615"],
  ]],
  ["developer", [
    ["🟢", "Python Developer - Integraciones y APIs",
      "https://www.getonbrd.com/jobs/python-developer-integraciones-apis-remote"],
  ]],
  ["ingeniero de software", [
    ["🟡", "Ingeniero/a de Software Jr (Python)",
      "https://ar.linkedin.com/jobs/view/ingeniero-a-de-software-jr-python-4485519364"],
  ]],
  ["programador", [
    ["🟡", "Programador Python Jr - Automatización de procesos",
      "https://ar.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-programador-python-jr-en-capital-federal-0C4F7A92E1D35B8661373E686DCF3405"],
    ["🟡", "Programador/a Backend Python (Flask)", "https://ar.indeed.com/viewjob?jk=c40f2b9e18d7a356"],
  ]],
  ["python", [
    ["🟡", "Data Analyst (Python, SQL)", "https://jobicy.com/jobs/157218-data-analyst-python-sql"],
    ["🟢", "Python Jr - Scraping y ETL (Remoto)", "https://ar.indeed.com/viewjob?jk=a71c3e09b4d28f65"],
    ["🟢", "Python Developer - Bots y Automatización",
      "https://www.getonbrd.com/jobs/python-developer-bots-automatizacion-remote"],
  ]],
  ["software engineer", [
    ["🟡", "Software Engineer Jr - LATAM", "https://ar.talent.com/view?id=643896032718845190"],
  ]],
  ["web scraping", [
    ["🟢", "Especialista en Web Scraping",
      "https://www.getonbrd.com/jobs/especialista-web-scraping-remote"],
  ]],
  [null, [
    ["🟢", "Ingeniero/a Back-end Django", "https://www.empleosit.com.ar/display-job/131652/"],
    ["🟡", "Automatización con RPA (Jr)", "https://www.bumeran.com.ar/empleos/1118494182.html"],
  ]],
]);

const offer = ([emoji, title, url], time) => inn(fill(T.OFFER, { emoji, title, url }), time);

function offersOf(offers, time, term) {
  const items = [];
  for (const light of ["🟢", "🟡"]) {
    for (const o of offers) {
      if (o[0] === light) items.push({ ...offer(o, time), term });
    }
  }
  return items;
}

// Como _send_by_keyword: cada palabra en orden alfabético, con sus 🟢🟡 (verdes primero) o un
// aviso sin sonido; Otros portales al final y solo si trajo algo. term marca el bloque.
function byKeyword(keywords, groups, time) {
  const items = [];
  for (const term of keywords) {
    const offers = groups.get(term);
    const header = fill(T.KEYWORD_HEADER, { term });
    if (!offers) {
      items.push(inn(`${header}\n${T.NO_MATCHES}`, time, { term }));
      continue;
    }
    items.push(inn(header, time, { term }));
    items.push(...offersOf(offers, time, term));
  }
  if (groups.has(null)) {
    items.push(inn(T.OTHER_PORTALS_HEADER, time, { term: null }));
    items.push(...offersOf(groups.get(null), time, null));
  }
  return items;
}

// Como _count_text: la plantilla en singular o en plural.
const countText = ([singular, plural], count) => fill(count === 1 ? singular : plural, { count });

function summaryLine(term, offers) {
  const greens = offers.filter((o) => o[0] === "🟢").length;
  const yellows = offers.length - greens;
  const counts = [];
  if (greens) counts.push(countText(T.SUMMARY_GREENS, greens));
  if (yellows) counts.push(countText(T.SUMMARY_YELLOWS, yellows));
  if (!counts.length) return fill(T.SUMMARY_EMPTY, { term });
  return fill(T.SUMMARY_LINE, { term, counts: counts.join(" - ") });
}

// Como _send_summary: siempre, sin sonido; start es cuando arrancó ese usuario y end, el envío.
function summary(start, end, keywords, groups) {
  const lines = [fill(T.SUMMARY_TITLE, { start, end })];
  for (const term of keywords) lines.push(summaryLine(term, groups.get(term) ?? []));
  if (groups.has(null)) lines.push(summaryLine(T.OTHER_PORTALS, groups.get(null)));
  return inn(lines.join("\n"), end);
}

// La corrida completa de un usuario: los bloques por palabra y el resumen.
const run = (groups, start, end) => [
  ...byKeyword(DEFAULT_TERMS, groups, end),
  summary(start, end, DEFAULT_TERMS, groups),
];

// Los mensajes de la corrida hasta el bloque de term, incluido.
const upTo = (items, term) => items.slice(0, items.findLastIndex((it) => it.term === term) + 1);

// ---------- piezas de la conversación ----------
function date(text) {
  return { kind: "date", text };
}
function info(title, text) {
  return { kind: "info", title, text };
}
function inn(text, time, extra = {}) {
  return { kind: "msg", dir: "in", text, time, ...extra };
}
function out(text, time, extra = {}) {
  return { kind: "msg", dir: "out", text, time, ...extra };
}

const settingsPanel = (terms, blocked) =>
  fill(T.SETTINGS_PANEL, { terms, blocked, profile_mark: "✅", alerts: "activas" });
const listText = (template, items) => fill(template, { count: items.length, items: items.join(" · ") });
const SETTINGS_KB = [["🔎 Términos", "🚫 Bloqueadas"], ["📄 Perfil", "⏸ Pausar"]];
const LIST_KB = [["➕ Agregar", "➖ Quitar"], ["⬅ Volver"]];

// La historia de Lucía es acumulativa: cada pantalla arrastra lo anterior y el
// chat (anclado abajo) corta arriba lo que no entra, como al scrollear.
// BOT_INFO es la descripción de setMyDescription: inventada, no está en el contrato.
const BOT_INFO = info(
  "¿Qué puede hacer este bot?",
  "Cada hora busco ofertas de trabajo en 11 portales y te mando por acá las que encajan con tu CV.\n🟢 encaja · 🟡 puede servir\nEl acceso lo aprueba el admin.",
);
const lucia01 = [
  BOT_INFO,
  date("30 de octubre"),
  out("/start", "10:12"),
  inn(fill(T.WELCOME_PENDING, LUCIA), "10:12"),
  out("/settings", "10:13"),
  inn(T.STILL_PENDING, "10:13"),
];
const lucia03 = [
  ...lucia01,
  inn(T.APPROVED, "10:19"),
  out("/perfil", "10:21"),
  inn(T.ASK_PROFILE, "10:21"),
  out("", "10:22", { doc: { name: "perfil.md", size: "8.0 KB" } }),
  inn(fill(T.PROFILE_SAVED, { chars: 7986 }), "10:22"),
  out("/settings", "10:25"),
];
const lucia06 = [
  ...lucia03,
  inn(fill(T.ASK_LIST, { what: "las palabras separadas" }), "10:25", { kb: [["✖ Cancelar"]], edited: true }),
  out("wordpress, laravel", "10:26"),
  inn(fill(T.ADDED, { items: "wordpress, laravel", count: DEFAULT_BLOCKED.length + 2 }), "10:26"),
];
const lucia07 = [
  ...lucia06,
  out("/settings", "10:27"),
  inn(listText(T.TERMS_LIST, DEFAULT_TERMS), "10:27", { kb: LIST_KB, edited: true }),
];
// Lucía es la segunda por orden de alta: arranca cuando Leandro terminó (11:19) y clasifica
// sus ~445 de las últimas 24 h antes de mandar nada.
const lucia08 = [...lucia07, ...run(RUN_11, "11:19", "11:24")];
// Pausa antes de la corrida de las 12: si no, faltarían las corridas de la tarde.
const lucia09 = [
  ...lucia08,
  out("/pausa", "11:41"),
  inn(T.PAUSED, "11:41"),
  date("31 de octubre"),
  out("/reanudar", "08:15"),
  inn(T.RESUMED, "08:15"),
];

// El admin también es usuario, con la misma semilla: su chat ya trae la corrida de las 9.
const ADMIN_RUN_09 = new Map([
  ["analista programador", [
    ["🟡", "Analista Programador Python Ssr (Híbrido)",
      "https://ar.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-analista-programador-python-ssr-en-belgrano-3B9D6E0F12A47C5861373E686DCF3405"],
  ]],
  ["backend", [
    ["🟢", "Backend Developer Python (Remoto)",
      "https://ar.linkedin.com/jobs/view/backend-developer-python-remoto-4485206731"],
    ["🟡", "Desarrollador Backend Python (Remoto LATAM)",
      "https://ar.linkedin.com/jobs/view/desarrollador-backend-python-remoto-latam-4485288460"],
  ]],
  ["desarrollador", [
    ["🟡", "Desarrollador Python - Datos e Integraciones",
      "https://www.getonbrd.com/jobs/desarrollador-python-datos-integraciones-remote"],
  ]],
  ["developer", [
    ["🟢", "Python Developer Jr - Automatizaciones",
      "https://www.getonbrd.com/jobs/python-developer-jr-automatizaciones-remote"],
  ]],
  ["python", [
    ["🟡", "Python Ssr - Bots y Automatización", "https://ar.indeed.com/viewjob?jk=9b16e3d0a47f2c58"],
  ]],
  ["web scraping", [
    ["🟢", "Desarrollador/a Web Scraping (Python)",
      "https://www.getonbrd.com/jobs/desarrollador-web-scraping-python-remote"],
  ]],
]);
// La última antes de /usuarios. Leandro es el primero: su corrida arranca a la hora en punto.
const ADMIN_RUN_12 = new Map([
  ["python", [
    ["🟢", "Python Ssr - APIs REST (Remoto)", "https://ar.indeed.com/viewjob?jk=3e8b0d71c95a2f46"],
    ["🟢", "Python Developer - Scraping y Datos",
      "https://www.getonbrd.com/jobs/python-developer-scraping-datos-remote"],
  ]],
]);
const adminHistory = [date("30 de octubre"), ...run(ADMIN_RUN_09, "09:00", "09:17")];

// Las descripciones de COMMANDS de diseno.md §4 (el contrato no las fija); cortas para que entren en una línea.
const COMMANDS = [
  ["/start", "Pedir acceso o reactivar el bot"],
  ["/settings", "Términos, bloqueadas y perfil"],
  ["/perfil", "Cargar o reemplazar tu CV"],
  ["/pausa", "Pausar las alertas"],
  ["/reanudar", "Volver a recibir alertas"],
  ["/ayuda", "Qué hace el bot y cómo usarlo"],
];

// Users.all(): por orden de alta. USER_LINE en dos renglones para que no se parta en el
// celular; el @ se omite si no hay username y el status va en castellano (STATUS_LABELS).
const STATUS_LABELS = {
  active: "✅ activo",
  paused: "⏸ pausado",
  pending: "⏳ pendiente",
  rejected: "❌ rechazado",
  blocked: "🚫 bloqueó el bot",
};
const ALL_USERS = [
  { first_name: "Leandro", username: "", status: "active", chat_id: 1048876312 },
  { ...LUCIA, status: "active" },
  { first_name: "Martín", username: "mgarcia_py", status: "paused", chat_id: 5571209934 },
  { first_name: "Diego", username: "diegodev", status: "blocked", chat_id: 6650092217 },
  { first_name: "Carla", username: "carla_rrhh", status: "rejected", chat_id: 7123004451 },
  { first_name: "Sofía", username: "sofi_backend", status: "pending", chat_id: 7012345968 },
];
const userLines = [];
for (const u of ALL_USERS) {
  const username = u.username ? ` @${u.username}` : "";
  userLines.push(fill(T.USER_LINE, { ...u, username, status: STATUS_LABELS[u.status] }));
}
const usersList = [fill(T.USERS_HEADER, { count: ALL_USERS.length }), ...userLines].join("\n\n");

// ---------- pantallas ----------
const SCREENS = [
  {
    id: "01-start-pendiente",
    title: "Alta pendiente",
    caption:
      "Lucía manda /start: queda pending y el bot le explica qué hace. Mientras espera, todo lo demás contesta STILL_PENDING.",
    clock: "10:13",
    items: lucia01,
  },
  {
    id: "02a-admin-aprobacion",
    title: "Solicitud al admin",
    caption:
      "En el chat del admin (ADMIN_CHAT_ID) llega ADMIN_REQUEST con los botones approve:{chat_id} y reject:{chat_id}. Arriba, el final del resumen de su corrida de las 9:00.",
    clock: "10:12",
    items: [
      ...adminHistory,
      inn(fill(T.ADMIN_REQUEST, LUCIA), "10:12", { kb: [["✅ Aprobar", "❌ Rechazar"]] }),
    ],
  },
  {
    id: "02b-admin-aprobada",
    title: "Solicitud aprobada",
    caption:
      "El admin toca Aprobar: editMessageText reemplaza el mismo mensaje (sin botones) y Lucía pasa a active.",
    clock: "10:19",
    items: [...adminHistory, inn(fill(T.ADMIN_APPROVED, LUCIA), "10:12", { edited: true })],
  },
  {
    id: "03-perfil",
    title: "Carga del perfil",
    caption:
      "Le llega APPROVED; con /perfil el bot pasa a awaiting_profile y Lucía manda su CV como perfil.md (se baja con getFile).",
    clock: "10:22",
    items: lucia03.slice(0, -1),
  },
  {
    id: "04-settings",
    title: "Panel /settings",
    caption:
      "Un solo mensaje con contadores y cuatro botones; navegar lo edita en lugar de mandar mensajes nuevos.",
    clock: "10:25",
    items: [
      ...lucia03,
      inn(settingsPanel(DEFAULT_TERMS.length, DEFAULT_BLOCKED.length), "10:25", { kb: SETTINGS_KB }),
    ],
  },
  {
    id: "05-bloqueadas",
    title: "Palabras bloqueadas",
    caption:
      "Botón 🚫 Bloqueadas (callback blocked): el panel se edita a la lista, con la semilla DEFAULT_BLOCKED_TITLE_WORDS.",
    clock: "10:25",
    items: [
      ...lucia03,
      inn(listText(T.BLOCKED_LIST, DEFAULT_BLOCKED), "10:25", { kb: LIST_KB, edited: true }),
    ],
  },
  {
    id: "06-agregar-bloqueadas",
    title: "Agregar bloqueadas",
    caption:
      "➕ Agregar deja awaiting_blocked_add y el panel pide las palabras. Lucía manda «wordpress, laravel»: pasa de 32 a 34 bloqueadas.",
    clock: "10:26",
    items: lucia06,
  },
  {
    id: "07-terminos",
    title: "Términos de búsqueda",
    caption:
      "Botón 🔎 Términos (callback terms): las palabras clave de Lucía, en orden alfabético. La corrida las busca de a una y agrupa cada oferta bajo la primera que la trajo.",
    clock: "10:27",
    items: lucia07,
  },
  {
    id: "08a-ofertas-por-palabra",
    title: "Ofertas por palabra",
    caption:
      "La corrida de las 11:00 le llega a las 11:24, después de la de Leandro. Sus 22 palabras, en orden alfabético: si trajo 🟢🟡, KEYWORD_HEADER («Búsqueda palabra \"…\":») y un OFFER por oferta, verdes primero; si no, un solo mensaje con NO_MATCHES («No se encontraron coincidencias.»), sin sonido (disable_notification). Las compuestas casi nunca traen nada: sus ofertas ya las trajo la palabra más corta. Supone link_preview_options desactivado.",
    clock: "11:24",
    items: upTo(lucia08, "desarrollador semi senior"),
  },
  {
    id: "08b-resumen",
    title: "Fin de la corrida",
    caption:
      "El final de la corrida, con el chat desplazado hacia arriba: el resumen no entra en una pantalla. Las últimas palabras y «Otros portales:», que aparece solo porque trajo algo (portales sin búsqueda y ninguna palabra en el título). Después, siempre y sin sonido, el resumen: de 11:19, cuando arrancó la corrida de Lucía, a 11:24, cuando se manda.",
    clock: "11:24",
    items: lucia08,
    lastTop: 370,
  },
  {
    id: "08c-resumen-final",
    title: "Resumen de la corrida",
    caption:
      "El resto del resumen. Una línea por palabra, en el mismo orden: las 🟢🟡 que se le mandaron («1 verde encontrado - 1 amarillo encontrado», «2 amarillos encontrados») o «No encontramos coincidencias». «Otros portales» va al final y solo si trajo algo.",
    clock: "11:24",
    items: lucia08,
  },
  {
    id: "09-pausa",
    title: "Pausar y reanudar",
    caption:
      "/pausa deja a Lucía en paused y las corridas la saltean, resumen incluido: no le llega nada; a la mañana siguiente, /reanudar la vuelve a active.",
    clock: "08:15",
    items: lucia09,
  },
  {
    id: "10-menu-comandos",
    title: "Menú de comandos",
    caption:
      "Al escribir «/» aparecen los comandos de setMyCommands. /usuarios no figura: solo se registra en el chat del admin.",
    clock: "08:16",
    items: lucia09,
    typed: "/",
    commands: COMMANDS,
  },
  {
    id: "11-admin-usuarios",
    title: "Usuarios (admin)",
    caption:
      "En el chat del admin, /usuarios lista a todos por orden de alta, pendientes y rechazados incluidos: nombre y @usuario arriba, estado y chat_id abajo. Desde otro chat contesta UNKNOWN.",
    clock: "12:40",
    items: [
      ...adminHistory,
      inn(fill(T.ADMIN_APPROVED, LUCIA), "10:12", { edited: true }),
      date("31 de octubre"),
      ...run(ADMIN_RUN_12, "12:00", "12:15"),
      out("/usuarios", "12:40"),
      inn(usersList, "12:40"),
    ],
  },
];

// ---------- HTML ----------
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const EMOJI = /\p{Extended_Pictographic}️?/gu;
const emoji = (s) => s.replace(EMOJI, '<span class="e">$&</span>');
const plain = (s) => emoji(esc(s)).replace(/\n/g, "<br>");

// Telegram resalta urls, /comandos y @menciones.
const ENTITY = /(https?:\/\/\S+)|((?<![\w/.])\/[a-z_]+)|(@\w{3,})/g;
function fmt(text) {
  let html = "";
  let last = 0;
  for (const m of text.matchAll(ENTITY)) {
    html += plain(text.slice(last, m.index));
    html += `<span class="link">${esc(m[0])}</span>`;
    last = m.index + m[0].length;
  }
  return html + plain(text.slice(last));
}

const ICON = {
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12H4.5M11 5l-7 7 7 7"/></svg>',
  more: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.9"/><circle cx="12" cy="12" r="1.9"/><circle cx="12" cy="19" r="1.9"/></svg>',
  smile: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9.2"/><path d="M8 14.2c1 1.6 2.4 2.4 4 2.4s3-.8 4-2.4"/><circle cx="9" cy="9.6" r="1.1" fill="currentColor" stroke="none"/><circle cx="15" cy="9.6" r="1.1" fill="currentColor" stroke="none"/></svg>',
  clip: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 11.2l-8.3 8.3a5.3 5.3 0 0 1-7.5-7.5l8.6-8.6a3.6 3.6 0 0 1 5.1 5.1l-8.6 8.6a1.8 1.8 0 0 1-2.6-2.6l7.9-7.9"/></svg>',
  mic: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="9" y="3" width="6" height="11.5" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.4 20.4l17.4-7.5a1 1 0 0 0 0-1.8L3.4 3.6a1 1 0 0 0-1.4.9V9.1c0 .5.4.9.9 1L16 12 2.9 13.9c-.5.1-.9.5-.9 1v4.6a1 1 0 0 0 1.4.9z"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M5 7h14M5 12h14M5 17h9"/></svg>',
  file: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
  down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9.5l6 6 6-6"/></svg>',
  checks: '<svg class="checks" viewBox="0 0 18 11" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M1 6l3 3 6.5-7.5M8 8.6l.9.9 6.6-8"/></svg>',
  signal: '<svg viewBox="0 0 16 13" fill="currentColor"><rect x="0" y="9" width="3" height="4" rx=".6"/><rect x="4.3" y="6" width="3" height="7" rx=".6"/><rect x="8.6" y="3" width="3" height="10" rx=".6"/><rect x="12.9" y="0" width="3" height="13" rx=".6"/></svg>',
  wifi: '<svg viewBox="0 0 18 13" fill="currentColor"><path d="M9 13L0 3.4A13 13 0 0 1 18 3.4z"/></svg>',
  battery: '<svg viewBox="0 0 26 13" fill="none" stroke="currentColor"><rect x=".6" y=".6" width="22" height="11.8" rx="3"/><rect x="2.4" y="2.4" width="15" height="8.2" rx="1.6" fill="currentColor" stroke="none"/><path d="M24.4 4.5v4" stroke-width="1.6" stroke-linecap="round"/></svg>',
};

const WALL = `<svg class="wall" aria-hidden="true"><defs><pattern id="wall" width="160" height="160" patternUnits="userSpaceOnUse"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="26" r="6"/><path d="M96 18v14M89 25h14"/><path d="M130 60l4 8 9 1-7 6 2 9-8-5-8 5 2-9-7-6 9-1z"/><path d="M14 100c8-8 16 8 24 0s16 8 24 0"/><rect x="92" y="104" width="26" height="18" rx="4"/><path d="M100 104v-4h10v4"/><path d="M52 64l24-10-9 24-4-10z"/><circle cx="142" cy="142" r="3"/><path d="M30 140l6-6 6 6-6 6z"/></g></pattern></defs><rect width="100%" height="100%" fill="url(#wall)"/></svg>`;

function meta(m) {
  const label = `${m.edited ? "editado " : ""}${m.time}${m.dir === "out" ? ICON.checks : ""}`;
  return { ghost: `<span class="meta ghost">${label}</span>`, real: `<span class="meta real">${label}</span>` };
}

function bubble(m) {
  const { ghost, real } = meta(m);
  if (m.doc) {
    return `<div class="bubble doc"><div class="doc-icon">${ICON.file}</div><div class="doc-info"><span class="doc-name">${esc(m.doc.name)}</span><span class="doc-size">${esc(m.doc.size)}</span></div>${real}</div>`;
  }
  return `<div class="bubble">${fmt(m.text)}${ghost}${real}</div>`;
}

function keyboard(rows) {
  const html = rows
    .map((row) => `<div class="kb-row">${row.map((b) => `<div class="btn">${plain(b)}</div>`).join("")}</div>`)
    .join("");
  return `<div class="kb">${html}</div>`;
}

const minutes = (time) => Number(time.slice(0, 2)) * 60 + Number(time.slice(3));
// Telegram Android agrupa los mensajes seguidos del mismo lado con hasta 5 min entre sí.
const together = (a, b) =>
  a?.kind === "msg" && b?.kind === "msg" && a.dir === b.dir && Math.abs(minutes(a.time) - minutes(b.time)) <= 5;

function renderItems(items) {
  return items
    .map((it, i) => {
      if (it.kind === "date") return `<div class="date">${esc(it.text)}</div>`;
      if (it.kind === "info") {
        return `<div class="botinfo"><div class="botinfo-title">${esc(it.title)}</div>${fmt(it.text)}</div>`;
      }
      const first = !together(items[i - 1], it);
      const tail = !together(it, items[i + 1]);
      const cls = ["row", it.dir, first && "first", tail && "tail"].filter(Boolean).join(" ");
      const body = it.kb ? `<div class="kbmsg">${bubble(it)}${keyboard(it.kb)}</div>` : bubble(it);
      return `<div class="${cls}">${body}</div>`;
    })
    .join("\n        ");
}

// El logo elegido, que Telegram recorta en círculo.
const avatar = (size = "") => `<img class="avatar ${size}" src="../../logo/labubot.svg" alt="">`;

function commandsPopup(commands) {
  const rows = commands
    .map(
      ([name, desc]) =>
        `<div class="cmd">${avatar("sm")}<div class="cmd-text"><span class="cmd-name">${esc(name)}</span><span class="cmd-desc">${esc(desc)}</span></div></div>`,
    )
    .join("");
  return `<div class="cmds">${rows}</div>`;
}

const THEME_SCRIPT = `<script>
    function applyTheme() {
      const theme = location.hash.slice(1);
      if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
      else delete document.documentElement.dataset.theme;
    }
    applyTheme();
    addEventListener("hashchange", applyTheme);
  </script>`;

const FONTS =
  '<link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap">';

function page(s) {
  const field = s.typed
    ? `<div class="field typed">${esc(s.typed)}<span class="caret"></span></div>`
    : '<div class="field">Mensaje</div>';
  const right = s.typed
    ? `<div class="ico send">${ICON.send}</div>`
    : `<div class="ico">${ICON.clip}</div><div class="ico">${ICON.mic}</div>`;
  // Con texto escrito, Telegram Android achica el botón Menú a solo el ícono.
  const menu = s.typed
    ? `<div class="menu-btn collapsed">${ICON.menu}</div>`
    : `<div class="menu-btn">${ICON.menu}Menú</div>`;
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=390">
  <title>labubot · ${esc(s.title)}</title>
  ${FONTS}
  <link rel="stylesheet" href="telegram.css">
  ${THEME_SCRIPT}
</head>
<body>
  <div class="phone">
    <div class="statusbar"><span>${s.clock}</span><span class="sb-icons">${ICON.signal}${ICON.wifi}${ICON.battery}</span></div>
    <div class="topbar">
      <div class="ico back">${ICON.back}</div>
      ${avatar()}
      <div class="who"><span class="name">labubot</span><span class="sub">bot</span></div>
      <div class="ico">${ICON.more}</div>
    </div>
    <main class="chat">
      ${WALL}
      <div class="stream"${s.lastTop ? ` data-last-top="${s.lastTop}"` : ""}>
        ${renderItems(s.items)}
      </div>
      ${s.commands ? commandsPopup(s.commands) : ""}
      ${s.lastTop ? `<div class="fab-down">${ICON.down}</div>` : ""}
    </main>
    <div class="composer">
      ${menu}
      <div class="ico">${ICON.smile}</div>
      ${field}
      ${right}
    </div>
    <div class="navbar"><i></i></div>
  </div>
  <script>
    // Un borde de burbuja sin texto bajo la cabecera o sobre el menú parece un error de dibujo: se oculta.
    document.fonts.ready.then(() => {
      const chat = document.querySelector(".chat").getBoundingClientRect();
      const stream = document.querySelector(".stream");
      // Chat desplazado hacia arriba: el último mensaje arranca a data-last-top px del borde.
      if (stream.dataset.lastTop) {
        const last = stream.lastElementChild.getBoundingClientRect().top;
        stream.style.bottom = last - chat.top - Number(stream.dataset.lastTop) + "px";
      }
      const top = chat.top;
      const popup = document.querySelector(".cmds");
      const bottom = popup ? popup.getBoundingClientRect().top : chat.bottom;
      for (const el of document.querySelectorAll(".stream > *")) {
        const box = el.getBoundingClientRect();
        const peeksTop = box.top < top && box.bottom - top < 16;
        const peeksBottom = box.bottom > bottom && bottom - box.top < 16;
        if (peeksTop || peeksBottom) el.style.visibility = "hidden";
      }
    });
  </script>
</body>
</html>
`;
}

for (const s of SCREENS) {
  writeFileSync(join(HERE, `${s.id}.html`), page(s));
}

// ---------- galería ----------
function gallery() {
  const cards = SCREENS.map((s) => {
    const n = s.id.split("-")[0];
    return `      <figure class="card">
        <a href="${s.id}.png"><img src="${s.id}.png" alt="${esc(s.title)}" width="390" height="844" loading="lazy"></a>
        <figcaption>
          <span class="num">${n}</span>
          <h2>${esc(s.title)}</h2>
          <p>${emoji(esc(s.caption)).replace(/\w{21,}/g, (w) => w.replace(/_/g, "_<wbr>"))}</p>
          <a class="src" href="src/${s.id}.html">maqueta HTML</a>
        </figcaption>
      </figure>`;
  }).join("\n");
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Capturas del bot</title>
  ${THEME_SCRIPT}
  <style>
    :root {
      --bg: #f4f6f8;
      --card: #ffffff;
      --fg: #17212b;
      --muted: #5b6b7a;
      --line: #dfe5ea;
      --accent: #2a7ab9;
      --shot-bg: #0e1621;
    }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) {
        --bg: #0b1119;
        --card: #17212b;
        --fg: #e9eef3;
        --muted: #8a9bab;
        --line: #243444;
        --accent: #6ab3f3;
      }
    }
    :root[data-theme="dark"] {
      --bg: #0b1119;
      --card: #17212b;
      --fg: #e9eef3;
      --muted: #8a9bab;
      --line: #243444;
      --accent: #6ab3f3;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      line-height: 1.45;
    }
    .e { font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif; }
    main { max-width: 1240px; margin: 0 auto; padding: 32px 16px 48px; }
    h1 { margin: 0 0 6px; font-size: 26px; }
    .lead { margin: 0 0 28px; color: var(--muted); max-width: 72ch; }
    .lead a { color: var(--accent); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 22px;
    }
    .card {
      margin: 0;
      display: flex;
      flex-direction: column;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: hidden;
    }
    .card img {
      display: block;
      width: 100%;
      height: auto;
      aspect-ratio: 390 / 844;
      background: var(--shot-bg);
      border-bottom: 1px solid var(--line);
    }
    figcaption { padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 4px; flex: 1; }
    .num { font-size: 12px; font-weight: 600; letter-spacing: .04em; color: var(--muted); }
    h2 { margin: 0; font-size: 16px; }
    p { margin: 0; font-size: 14px; color: var(--muted); flex: 1; overflow-wrap: anywhere; }
    .src { margin-top: 6px; font-size: 13px; color: var(--accent); text-decoration: none; }
    .src:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <main>
    <h1>Así se va a ver labubot en Telegram</h1>
    <p class="lead">Maquetas del bot multiusuario en el tema oscuro de Telegram (Android, 390×844). Lucía (@lucia_dev) es una usuaria ficticia. Los textos son los canónicos del contrato, salvo ASK_LIST, que en 06 va concordado («las palabras separadas»); los mensajes por palabra y el resumen son los de la revisión del 1/11 (diseno.md §4). El avatar es el logo de <a href="../logo/">logo/</a>. Tocá una captura para verla en tamaño real.</p>
    <div class="grid">
${cards}
    </div>
  </main>
</body>
</html>
`;
}

writeFileSync(join(HERE, "..", "index.html"), gallery());
console.log(`${SCREENS.length} maquetas + index.html`);
