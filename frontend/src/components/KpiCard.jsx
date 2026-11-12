export default function KpiCard({ etiqueta, valor, detalle }) {
  return (
    <article className="kpi">
      <p className="kpi__etiqueta">{etiqueta}</p>
      <p className="kpi__valor">{valor}</p>
      {detalle && <p className="kpi__detalle">{detalle}</p>}
    </article>
  );
}
