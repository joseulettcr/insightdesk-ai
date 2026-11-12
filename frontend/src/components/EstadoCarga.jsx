export default function EstadoCarga({ texto = "Cargando datos…" }) {
  return (
    <div className="estado estado--carga" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{texto}</span>
    </div>
  );
}
