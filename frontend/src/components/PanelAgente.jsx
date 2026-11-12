import { useState } from "react";
import { api } from "../api/client.js";

const ETIQUETAS_HERRAMIENTAS = {
  consultar_resumen_ventas: "resumen de ventas",
  consultar_ventas_por_producto: "ventas por producto",
  consultar_ventas_por_categoria: "ventas por categoría",
};

export default function PanelAgente() {
  const [mensajes, setMensajes] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);

  async function enviar(evento) {
    evento.preventDefault();
    const mensaje = pregunta.trim();
    if (!mensaje || enviando) return;

    setError(null);
    setPregunta("");
    setMensajes((previos) => [...previos, { rol: "usuario", texto: mensaje }]);
    setEnviando(true);
    try {
      const respuesta = await api.consultarAgente(mensaje);
      setMensajes((previos) => [
        ...previos,
        { rol: "asistente", texto: respuesta.respuesta, herramientas: respuesta.herramientas_usadas },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="agente">
      <div className="agente__mensajes" aria-live="polite">
        {mensajes.length === 0 && (
          <p className="agente__texto">
            Pregunta por ventas, productos o categorías. Las cifras se calculan con los datos registrados.
          </p>
        )}
        {mensajes.map((mensaje, indice) => (
          <div key={indice} className={`burbuja burbuja--${mensaje.rol}`}>
            <p className="burbuja__texto">{mensaje.texto}</p>
            {mensaje.herramientas?.length > 0 && (
              <p className="burbuja__fuentes">
                Datos consultados: {mensaje.herramientas.map((h) => ETIQUETAS_HERRAMIENTAS[h] ?? h).join(", ")}
              </p>
            )}
          </div>
        ))}
        {enviando && <p className="agente__texto">Consultando el asistente…</p>}
      </div>

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

      <form className="agente__formulario" onSubmit={enviar}>
        <textarea
          className="agente__entrada"
          rows={2}
          maxLength={1000}
          placeholder="Ej.: ¿Qué producto genera más ingresos?"
          value={pregunta}
          onChange={(evento) => setPregunta(evento.target.value)}
          disabled={enviando}
        />
        <button type="submit" className="boton" disabled={enviando || !pregunta.trim()}>
          Enviar
        </button>
      </form>
    </div>
  );
}
