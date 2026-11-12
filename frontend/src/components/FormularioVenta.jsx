import { useState } from "react";
import { api } from "../api/client.js";

const inicial = { productoId: "", cantidad: "1", precioUnitario: "", fecha: "" };

export default function FormularioVenta({ productos, onRegistrada }) {
  const [campos, setCampos] = useState(inicial);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(null);

  const actualizar = (campo) => (evento) => setCampos((previo) => ({ ...previo, [campo]: evento.target.value }));

  async function enviar(evento) {
    evento.preventDefault();
    setError(null);
    setExito(null);

    const venta = { producto_id: Number(campos.productoId), cantidad: Number(campos.cantidad) };
    if (campos.precioUnitario !== "") venta.precio_unitario = Number(campos.precioUnitario);
    if (campos.fecha !== "") venta.fecha = campos.fecha;

    setEnviando(true);
    try {
      await api.registrarVenta(venta);
      setCampos((previo) => ({ ...inicial, productoId: previo.productoId }));
      setExito("Venta registrada correctamente.");
      onRegistrada();
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <label className="campo">
        <span>Producto</span>
        <select value={campos.productoId} onChange={actualizar("productoId")} required>
          <option value="" disabled>
            Selecciona un producto
          </option>
          {productos.map((producto) => (
            <option key={producto.id} value={producto.id}>
              {producto.nombre}
            </option>
          ))}
        </select>
      </label>

      <div className="fila-campos">
        <label className="campo">
          <span>Cantidad</span>
          <input type="number" min="1" step="1" value={campos.cantidad} onChange={actualizar("cantidad")} required />
        </label>
        <label className="campo">
          <span>Precio unitario</span>
          <input
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Precio del catálogo"
            value={campos.precioUnitario}
            onChange={actualizar("precioUnitario")}
          />
        </label>
      </div>

      <label className="campo">
        <span>Fecha</span>
        <input type="date" value={campos.fecha} onChange={actualizar("fecha")} />
      </label>

      <button type="submit" className="boton" disabled={enviando || !campos.productoId}>
        {enviando ? "Registrando…" : "Registrar venta"}
      </button>

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}
      {exito && <p className="mensaje mensaje--exito" role="status">{exito}</p>}
    </form>
  );
}
