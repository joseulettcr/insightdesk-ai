const BASE_URL = "/api";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function describirError(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((error) => {
        const campo = error.loc?.slice(1).join(".");
        return campo ? `${campo}: ${error.msg}` : error.msg;
      })
      .join(" · ");
  }
  return `Error del servidor (${status}).`;
}

async function peticion(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(`${BASE_URL}${ruta}`, {
      ...opciones,
      headers: { Accept: "application/json", "Content-Type": "application/json" },
    });
  } catch {
    throw new ApiError("No se pudo conectar con el servidor. Comprueba que el backend esté en ejecución.", 0);
  }

  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new ApiError(describirError(cuerpo?.detail, respuesta.status), respuesta.status);
  }
  return cuerpo;
}

export const api = {
  listarProductos: () => peticion("/productos"),
  listarVentas: () => peticion("/ventas"),
  registrarVenta: (venta) => peticion("/ventas", { method: "POST", body: JSON.stringify(venta) }),
  obtenerIndicadores: () => peticion("/indicadores"),
  consultarAgente: (mensaje) => peticion("/agente/chat", { method: "POST", body: JSON.stringify({ mensaje }) }),
};
