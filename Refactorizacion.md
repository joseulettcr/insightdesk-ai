# Refactorización — Plan de cambios

Estado: **plan pendiente de aprobación. No se ha construido nada.**
Stack: React 19 + Vite 8, FastAPI, SQLite, Gemini. No se añade ninguna librería nueva.

---

## Cambio 1 — Modo claro / oscuro

**Objetivo:** el usuario elige entre modo claro y oscuro desde la cabecera.

**Enfoque técnico:**
- `frontend/src/index.css` ya define tokens en `:root` y en `[data-theme="dark"]`. Se reutilizan sin cambiar valores.
- Nuevo hook `hooks/useTema.js` que escribe `data-theme` en `<html>` y guarda la preferencia en `localStorage` (con try/catch).
- Botón de alternancia en `App.jsx` (cabecera). Estado inicial: preferencia guardada, o `prefers-color-scheme` si no hay ninguna.

**Archivos:** `hooks/useTema.js` (nuevo), `App.jsx`, `index.css`.

---

## Cambio 2 — Paneles arrastrables

**Objetivo:** el usuario arrastra cada panel con el mouse y lo suelta en la posición que quiera.

**Enfoque técnico:**
- Usar la API nativa de HTML5 Drag and Drop (`draggable`, `onDragStart`, `onDragOver`, `onDrop`), sin librerías.
- Cada `Panel` recibe un `id`. `App.jsx` mantiene un array de orden de paneles en estado.
- Al soltar, se reordena el array según el `id` destino. Se persiste en `localStorage`.
- Restaurar el orden guardado al cargar; ignorar IDs desconocidos.
- Los paneles siguen en su columna. Solo cambia el orden dentro de la rejilla.

**Archivos:** `components/Panel.jsx`, `App.jsx`, `index.css` (estilo de arrastre), `hooks/useOrdenPaneles.js` (nuevo).

---

## Cambio 3 — Registro de errores del Asistente (`log.md`)

**Objetivo:** guardar en `log.md` los errores del asistente, sin exponer secretos.

**Enfoque técnico:**
- Backend: módulo `app/agente/registro.py` con `logging` de la biblioteca estándar. Añade una línea en Markdown a `log.md` en la raíz del proyecto por cada error.
- Se registra fecha, código HTTP y tipo de error (401/403, 429, 503, 504, respuesta vacía, herramienta fallida).
- No se registran la clave, el cuerpo de la respuesta de Gemini ni el texto del usuario.
- Se llama desde los puntos de error de `app/agente/servicio.py` y de `app/agente/gemini.py`.
- Escritura con `open(..., "a")` y `try/except` para que un fallo de log nunca tumbe la petición.

**Archivos:** `backend/app/agente/registro.py` (nuevo), `backend/app/agente/servicio.py`, `backend/app/agente/gemini.py`, `log.md` (se crea al primer error).

---

## Orden de ejecución propuesto

1. Cambio 1 (tema), es el más aislado.
2. Cambio 3 (log del backend), independiente del frontend.
3. Cambio 2 (arrastre), el más complejo.

Cada fase se verifica con `npm run build`, `pytest` y comprobación en el navegador antes de pasar a la siguiente.

---

## Pendiente de tu aprobación

- ¿Guardar la preferencia de tema y el orden de paneles en `localStorage` (por navegador) o en la base de datos (compartido)? Propongo `localStorage`, que no necesita cambios en la API.
