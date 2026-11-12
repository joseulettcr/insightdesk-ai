# plan.md — Plan de implementación

## Estado
- Fase 1: completada y verificada.
- Fase 2: completada y verificada (21 pruebas pytest, API en vivo comprobada).
- Fase 3: completada y verificada con build y render del lado del servidor. Falta comprobación visual en navegador.
- Fase 4: completada y verificada (58 pruebas pytest; llamadas reales del SDK contra un Gemini simulado local).
- Fase 5: no iniciada. Requiere autorización explícita.

## Dependencias
Instaladas (autorizadas):
- `uvicorn==0.54.0`: servidor ASGI para ejecutar FastAPI. Autorizada por el usuario en la fase 1.
- `httpx==0.28.1`: cliente para `TestClient`. Autorizada por el usuario en la fase 1.
- `SQLAlchemy==2.1.6`: ORM y SQLite. Está en spec.md y se instaló en la fase 2.
- `recharts@3.10.1`: gráficos del dashboard. Está en spec.md y se instaló en la fase 3.
- `google-genai==2.33.0`: SDK oficial de Gemini. Está en spec.md y se instaló en la fase 4.
- `pydantic`: no se instala de forma directa. Ya llega como dependencia de FastAPI y se usa para las validaciones de la fase 2.

## Decisiones de la fase 2
- Importes: se guardan como céntimos enteros (`TypeDecorator` `Dinero`), así que no hay `float` en la base de datos. En JSON se devuelven como número con 2 decimales.
- Fechas: formato ISO `YYYY-MM-DD`. No se aceptan fechas futuras.
- `categoria` se usa sin tilde en los campos JSON y en el código. El valor de la categoría sí conserva la tilde (p. ej. "Electrónica").
- `precio_unitario` en `POST /api/ventas` es opcional. Si no se envía, toma el precio actual del producto. `fecha` es opcional y por defecto es hoy.
- Seed: 10 productos fijos y 50 ventas generadas con semilla `2026`. Fechas entre 2026-01-01 y 2026-03-31. Es idempotente: si ya hay productos, no inserta nada. Se ejecuta con `python -m app.seed` desde `backend/`.
- Ticket promedio: ingresos totales / número de ventas, redondeado a 2 decimales.

## Verificación de la fase 2
- `pytest`: 21 pruebas pasando.
  - Seed: 10 productos y 50 ventas, idempotente, reproducible entre bases distintas y precios iguales al catálogo.
  - Indicadores: caso con valores calculados a mano, y comparación contra un recálculo independiente en Python sobre los datos demo.
  - API: validaciones con Pydantic (422), producto inexistente (404), precio y fecha por defecto, y actualización de indicadores tras una venta nueva.
  - Persistencia: las ventas sobreviven a reiniciar la aplicación (base de datos en fichero).
- Prueba de sensibilidad: se introdujo un error en la fórmula del ticket promedio y 3 pruebas fallaron. Tras restaurar el código, vuelven a pasar las 21.
- En vivo con `uvicorn`: `GET /api/productos` y `GET /api/ventas` devuelven 200. `GET /api/indicadores` devuelve ingresos 6647.35, 50 ventas y ticket promedio 132.95. `POST /api/ventas` con cantidad 0 devuelve 422, y con producto inexistente devuelve 404.

No instaladas (no autorizadas):
- `@vitejs/plugin-react`: Vite compila el JSX de forma nativa (verificado con `npm run build`).
- `eslint`: no está en spec.md.

## Revisión inicial (coherencia, dependencias, riesgos)
Riesgos y ambigüedades abiertos:
- Warning de Starlette: `Using httpx with starlette.testclient is deprecated; install httpx2 instead`. Sustituir `httpx` por `httpx2` requiere autorización, porque no está en spec.md.

Riesgos y ambigüedades:
- Autenticación: el rol "Administrador del sistema" no tiene reglas de acceso definidas en spec.md.
- Modelo de datos: falta definir el tipo monetario de `precio` y `precio_unitario` (recomendado: `Decimal` o céntimos enteros, no `float`), el formato de `fecha` y si `categoría` es libre o una lista cerrada.
- Secretos: la clave de Gemini debe ir en variables de entorno. `.env` está ignorado en Git; `backend/.env.example` se creó en la fase 4.
- Versiones: Python 3.15 es muy reciente. Las dependencias instaladas funcionaron, pero si aparecen incompatibilidades conviene usar Python 3.12 o 3.13.
- Proxy: el proxy de Vite (`/api` → `127.0.0.1:8000`) solo aplica en desarrollo. Falta decidir cómo se servirá en producción.

## Fase 1 — Inicialización
- [x] Crear frontend React + Vite. (`frontend/`: react 19, react-dom, vite 8; build verificado)
- [x] Crear backend FastAPI. (`backend/`: `app/main.py`, fastapi 0.162.0)
- [x] Configurar Git y .gitignore. (repositorio inicializado sin commits; `.gitignore` en raíz)
- [x] Instalar dependencias autorizadas. (react, react-dom, vite, fastapi, pytest, más uvicorn y httpx autorizadas)

Verificación de la fase 1:
- `pytest`: 3 pruebas pasando (una de ellas hace una petición HTTP a `/openapi.json` con `TestClient`).
- `uvicorn app.main:app`: `/openapi.json` responde HTTP 200 con JSON válido.
- `npm run build`: compila sin errores.
- Vite dev server: `localhost:5173` responde HTTP 200.
- Proxy `/api`: la respuesta de Vite coincide con la de FastAPI directo (404 JSON en una ruta inexistente).

## Fase 2 — Datos
- [x] Crear modelos Producto y Venta. (`backend/app/models.py`)
- [x] Configurar SQLite. (SQLAlchemy 2.1.6; `INSIGHTDESK_DATABASE_URL`, por defecto `sqlite:///./insightdesk.db`)
- [x] Generar datos de demostración. (`backend/app/seed.py`: 10 productos y 50 ventas reproducibles)
- [x] Implementar endpoints REST. (`GET/POST /api/productos`, `GET/POST /api/ventas`, `GET /api/indicadores`)
- [x] Verificar indicadores con pruebas. (`tests/test_indicadores.py`, validado con sensibilidad)

## Fase 3 — Frontend
- [x] Construir dashboard. (`frontend/src/App.jsx`: KPIs, gráfico, ventas recientes, formulario y panel lateral)
- [x] Mostrar indicadores y gráficos. (KPI de ingresos, unidades y ticket promedio; gráfico de ventas por categoría con Recharts, cargado con `lazy`)
- [x] Crear formulario de ventas. (`components/FormularioVenta.jsx`: POST a `/api/ventas`, muestra errores del backend)
- [x] Conectar frontend con backend. (`api/client.js` y `hooks/useRecurso.js`; solo consume `/api/*`, sin datos simulados)

Componentes reutilizables: `Panel`, `KpiCard`, `Recurso` (carga, error y vacío), `EstadoCarga`, `EstadoError`, `TablaVentas`, `GraficoCategorias`, `FormularioVenta`, `PanelAgente`.

Verificación de la fase 3:
- `npm run build`: compila sin errores ni avisos. El gráfico queda en un fragmento aparte de 357 kB, y el principal ocupa 230 kB.
- Proxy de Vite: `/api/indicadores` devuelve los mismos valores que el backend directo (ingresos 6647.35, 50 ventas, 4 categorías).
- Render del lado del servidor con datos reales: estado de carga, estado de error con botón de reintentar, estado vacío, tabla con 10 filas y nombres del catálogo, formulario con 10 productos, KPI y panel del asistente deshabilitado. Las 8 comprobaciones pasan.
- Pendiente: comprobación visual en navegador. No hay herramienta de navegador disponible en esta sesión.

Decisiones de la fase 3:
- Moneda: la especificación no la define. Los importes se muestran con formato numérico `es-ES` y dos decimales, sin símbolo.
- Ventas recientes: las 10 últimas por fecha e id.
- Panel del asistente: solo un marcador deshabilitado. No contiene respuestas simuladas ni integración con Gemini.

## Fase 4 — Agente
- [x] Configurar Gemini. (`app/agente/gemini.py`: cliente desde `GEMINI_API_KEY`, timeout de 30 s; modelo configurable con `GEMINI_MODEL`, por defecto `gemini-2.5-flash`)
- [x] Implementar herramientas de consulta. (`app/agente/herramientas.py`: `consultar_resumen_ventas`, `consultar_ventas_por_producto`, `consultar_ventas_por_categoria`; solo lectura, sin parámetros)
- [x] Integrar function calling. (`app/agente/servicio.py`: bucle manual con `function_calls` y `FunctionResponse`, máximo 6 turnos)
- [x] Crear endpoint de chat. (`POST /api/agente/chat`, con `ChatRequest` y `ChatResponse` en Pydantic)
- [x] Construir interfaz conversacional. (`frontend/src/components/PanelAgente.jsx`, en el panel lateral)

## Fase 5 — Calidad
- [ ] Ejecutar pytest.
- [ ] Compilar frontend.
- [ ] Validar manejo de errores.
- [ ] Revisar seguridad de secretos.
- [ ] Documentar ejecución en README.

## Verificación de la fase 4
Decisiones de la fase 4:
- Herramientas sin parámetros: el modelo no puede pasar filtros ni SQL. Todas las consultas son SQLAlchemy fijas y las herramientas no escriben en la base de datos.
- Bucle de function calling manual, en lugar de la ejecución automática del SDK. Así controlo qué herramientas se ejecutan, cuento las usadas y limito los turnos a 6.
- Función no registrada pedida por el modelo: no se ejecuta nada y se devuelve un error al modelo.
- Fallo interno de una herramienta: se devuelve al modelo un mensaje genérico. El detalle solo se registra en el servidor.
- Errores de Gemini: 401 y 403 → 502 (revisar la configuración); 429 → 429; timeout o 504 → 504; respuesta vacía → 502; sin `GEMINI_API_KEY` → 503. Ningún mensaje de error incluye datos del proveedor.
- La clave viaja solo en la cabecera de la petición. No aparece en el cuerpo, en las respuestas ni en el esquema OpenAPI.
- Configuración: `backend/.env.example` documenta las variables. El `.env` real está ignorado en Git.

Verificación:
- `pytest`: 58 pruebas pasando.
  - Herramientas: solo se declaran las tres de lectura, sin parámetros; devuelven datos reales de SQLite; incluyen productos sin ventas; no modifican registros.
  - Servicio: encadena herramientas, responde sin herramientas cuando no las necesita, bloquea funciones no registradas, controla fallos internos, detecta respuestas vacías y limita los bucles.
  - Errores de Gemini simulados (401, 403, 429, 500, 504, timeout, error inesperado): cada uno produce el código HTTP previsto y ningún mensaje incluye la clave.
  - API: 200 con respuesta correcta, 503 sin clave, 422 con mensajes vacíos o de más de 1000 caracteres, y la clave ausente de respuestas y del esquema.
- Cliente real del SDK `google-genai` contra un servidor HTTP local que simula Gemini (sin coste ni red externa):
  - La primera petición declara las tres herramientas sin parámetros y envía la instrucción de sistema con temperatura 0.2.
  - La segunda petición devuelve a Gemini el resultado de `consultar_resumen_ventas` (`numero_ventas: 50`).
  - La clave viaja en la cabecera `x-goog-api-key` y no aparece en el cuerpo.
  - Errores reales del SDK: 401 → 502, 429 → 429, timeout de 1 s → 504.
- Servidor en ejecución en el puerto 8000: `POST /api/agente/chat` devuelve 503 sin `GEMINI_API_KEY`, y la ruta aparece en OpenAPI.
- `npm run build` sigue compilando. El panel del asistente renderiza su estado inicial.
- Pendiente: no he probado el modelo real de Gemini. Requiere una clave válida y una llamada con coste. Las pruebas usan respuestas simuladas.
- Aviso: el SDK `google-genai` emite un `DeprecationWarning` de Python 3.15 al importarse. No afecta al resultado.

## Regla de trabajo
Claude debe implementar una fase a la vez, ejecutar las verificaciones correspondientes y actualizar este plan. No avanzar automáticamente si existen errores sin resolver.
