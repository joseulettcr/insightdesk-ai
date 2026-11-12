const importe = new Intl.NumberFormat("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const entero = new Intl.NumberFormat("es-ES");

export const formatoImporte = (valor) => importe.format(valor);
export const formatoEntero = (valor) => entero.format(valor);

export function formatoFecha(isoDate) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
