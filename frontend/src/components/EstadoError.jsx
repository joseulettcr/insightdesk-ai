export default function EstadoError({ mensaje, onReintentar }) {
  return (
    <div className="estado estado--error" role="alert">
      <span>{mensaje}</span>
      {onReintentar && (
        <button type="button" className="boton boton--secundario" onClick={onReintentar}>
          Reintentar
        </button>
      )}
    </div>
  );
}
