import { lazy, Suspense, useMemo } from "react";
import { api } from "./api/client.js";
import FormularioVenta from "./components/FormularioVenta.jsx";
import EstadoCarga from "./components/EstadoCarga.jsx";
import KpiCard from "./components/KpiCard.jsx";
import PanelAgente from "./components/PanelAgente.jsx";
import Panel from "./components/Panel.jsx";
import Recurso from "./components/Recurso.jsx";
import TablaVentas from "./components/TablaVentas.jsx";
import { useDistribucion } from "./hooks/useDistribucion.js";
import { useRecurso } from "./hooks/useRecurso.js";
import { useTema } from "./hooks/useTema.js";
import { formatoEntero, formatoImporte } from "./utils/formato.js";

const GraficoCategorias = lazy(() => import("./components/GraficoCategorias.jsx"));

const VENTAS_RECIENTES = 10;

const DISTRIBUCION_INICIAL = {
  principal: ["categorias", "recientes"],
  lateral: ["registro", "asistente"],
};

export default function App() {
  const productos = useRecurso(api.listarProductos);
  const ventas = useRecurso(api.listarVentas);
  const indicadores = useRecurso(api.obtenerIndicadores);
  const { tema, alternar } = useTema();
  const distribucion = useDistribucion("insightdesk.distribucion", DISTRIBUCION_INICIAL);

  const productosPorId = useMemo(
    () => Object.fromEntries((productos.datos ?? []).map((producto) => [producto.id, producto])),
    [productos.datos],
  );

  function actualizarTrasVenta() {
    ventas.recargar();
    indicadores.recargar();
  }

  const zonaPrincipal = distribucion.zona("principal");
  const zonaLateral = distribucion.zona("lateral");

  function renderPanel(id) {
    const arrastre = distribucion.arrastre(id);
    switch (id) {
      case "categorias":
        return (
          <Panel key={id} titulo="Ventas por categoría" arrastre={arrastre}>
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
        );
      case "recientes":
        return (
          <Panel key={id} titulo="Ventas recientes" arrastre={arrastre}>
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
        );
      case "registro":
        return (
          <Panel key={id} titulo="Registrar venta" arrastre={arrastre}>
            <Recurso
              estado={productos}
              esVacio={(datos) => datos.length === 0}
              mensajeVacio="No hay productos disponibles."
            >
              {(datos) => <FormularioVenta productos={datos} onRegistrada={actualizarTrasVenta} />}
            </Recurso>
          </Panel>
        );
      case "asistente":
        return (
          <Panel key={id} titulo="Asistente" arrastre={arrastre}>
            <PanelAgente />
          </Panel>
        );
      default:
        return null;
    }
  }

  return (
    <div className="app">
      <header className="cabecera">
        <div>
          <h1>InsightDesk AI</h1>
          <p>Indicadores comerciales en tiempo real</p>
        </div>
        <button type="button" className="boton-tema" onClick={alternar} aria-label="Cambiar modo claro u oscuro">
          {tema === "claro" ? "Modo oscuro" : "Modo claro"}
        </button>
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

          <div
            className="fila-dos"
            onDragOver={zonaPrincipal.alPasarSobre}
            onDrop={zonaPrincipal.alSoltar}
          >
            {distribucion.dist.principal.map((id) => renderPanel(id))}
          </div>
        </main>

        <aside
          className="lateral"
          onDragOver={zonaLateral.alPasarSobre}
          onDrop={zonaLateral.alSoltar}
        >
          {distribucion.dist.lateral.map((id) => renderPanel(id))}
        </aside>
      </div>
    </div>
  );
}
