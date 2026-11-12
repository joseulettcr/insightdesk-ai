import { formatoFecha, formatoImporte } from "../utils/formato.js";

export default function TablaVentas({ ventas, productosPorId }) {
  return (
    <div className="tabla-contenedor">
      <table className="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Producto</th>
            <th className="numero">Cant.</th>
            <th className="numero">Precio</th>
            <th className="numero">Total</th>
          </tr>
        </thead>
        <tbody>
          {ventas.map((venta) => (
            <tr key={venta.id}>
              <td>{formatoFecha(venta.fecha)}</td>
              <td>{productosPorId[venta.producto_id]?.nombre ?? `Producto #${venta.producto_id}`}</td>
              <td className="numero">{venta.cantidad}</td>
              <td className="numero">{formatoImporte(venta.precio_unitario)}</td>
              <td className="numero">{formatoImporte(venta.cantidad * venta.precio_unitario)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
