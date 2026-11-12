import EstadoCarga from "./EstadoCarga.jsx";
import EstadoError from "./EstadoError.jsx";

export default function Recurso({ estado, esVacio, mensajeVacio, children }) {
  const { cargando, error, datos, recargar } = estado;

  if (error) return <EstadoError mensaje={error} onReintentar={recargar} />;
  if (datos === null) return cargando ? <EstadoCarga /> : null;
  if (esVacio?.(datos)) return <p className="estado estado--vacio">{mensajeVacio}</p>;
  return children(datos);
}
