import { lazy, Suspense, useMemo } from "react";
import { api } from "./api/client.js";
import FormularioVenta from "./components/FormularioVenta.jsx";
import EstadoCarga from "./components/EstadoCarga.jsx";
import KpiCard from "./components/KpiCard.jsx";
import PanelAgente from "./components/PanelAgente.jsx";
import Panel from "./components/Panel.jsx";
import Recurso from "./components/Recurso.jsx";
import TablaVentas from "./components/TablaVentas.jsx";
import { useRecurso } from "./hooks/useRecurso.js";
import { formatoEntero, formatoImporte } from "./utils/formato.js";

const GraficoCategorias = lazy(() => import("./components/GraficoCategorias.jsx"));

const VENTAS_RECIENTES = 10;

export default function App() {
  const productos = useRecurso(api.listarProductos);
  const ventas = useRecurso(api.listarVentas);
  const indicadores = useRecurso(api.obtenerIndicadores);

  const productosPorId = useMemo(
    () => Object.fromEntries((productos.datos ?? []).map((producto) => [producto.id, producto])),
    [productos.datos],
  );

  function actualizarTrasVenta() {
    ventas.recargar();
    indicadores.recargar();
  }

  return (
    <div className="app">
      <header className="cabecera">
        <div>
          <h1>InsightDesk AI</h1>
          <p>Indicadores comerciales en tiempo real</p>
        </div>
      </header>

      <div className="rejilla">
        <main className="principal">
          <section className="kpis" aria-label="Indicadores clave">
            <Recurso estado={indicadores}>
              {(datos) => (
                <>
                  <KpiCard
                    etiqueta="Ingresos totales"
                    valor={formatoImporte(datos.ingresos_totales)}
                    detalle={`${formatoEntero(datos.numero_ventas)} ventas registradas`}
                  />
                  <KpiCard
                    etiqueta="Unidades vendidas"
                    valor={formatoEntero(datos.cantidad_vendida)}
                    detalle="Suma de cantidades"
                  />
                  <KpiCard
                    etiqueta="Ticket promedio"
                    valor={formatoImporte(datos.ticket_promedio)}
                    detalle="Ingreso medio por venta"
                  />
                </>
              )}
            </Recurso>
          </section>

          <div className="fila-dos">
            <Panel titulo="Ventas por categoría">
              <Recurso
                estado={indicadores}
                esVacio={(datos) => datos.ventas_por_categoria.length === 0}
                mensajeVacio="Aún no hay ventas registradas."
              >
                {(datos) => (
                  <Suspense fallback={<EstadoCarga texto="Cargando gráfico…" />}>
                    <GraficoCategorias datos={datos.ventas_por_categoria} />
                  </Suspense>
                )}
              </Recurso>
            </Panel>

            <Panel titulo="Ventas recientes">
              <Recurso
                estado={ventas}
                esVacio={(datos) => datos.length === 0}
                mensajeVacio="Aún no hay ventas registradas."
              >
                {(datos) => (
                  <TablaVentas
                    ventas={[...datos].reverse().slice(0, VENTAS_RECIENTES)}
                    productosPorId={productosPorId}
                  />
                )}
              </Recurso>
            </Panel>
          </div>
        </main>

        <aside className="lateral">
          <Panel titulo="Registrar venta">
            <Recurso
              estado={productos}
              esVacio={(datos) => datos.length === 0}
              mensajeVacio="No hay productos disponibles."
            >
              {(datos) => <FormularioVenta productos={datos} onRegistrada={actualizarTrasVenta} />}
            </Recurso>
          </Panel>

          <Panel titulo="Asistente">
            <PanelAgente />
          </Panel>
        </aside>
      </div>
    </div>
  );
}
