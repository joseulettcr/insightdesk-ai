import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatoEntero, formatoImporte } from "../utils/formato.js";

export default function GraficoCategorias({ datos }) {
  return (
    <div className="grafico">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={datos} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#94a3b8" strokeOpacity={0.3} />
          <XAxis dataKey="categoria" tickLine={false} axisLine={false} />
          <YAxis tickFormatter={formatoEntero} tickLine={false} axisLine={false} width={72} />
          <Tooltip formatter={(valor) => formatoImporte(valor)} cursor={{ fill: "#6366f1", fillOpacity: 0.08 }} />
          <Bar dataKey="ingresos" name="Ingresos" fill="#6366f1" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
