import { useEffect, useRef, useState } from "react";

const COLUMNAS = ["principal", "lateral"];

// Lee la distribución guardada. Descarta ids desconocidos o repetidos y añade los que falten
// al final de su columna por defecto.
function leerDistribucion(clave, defecto) {
  try {
    const guardado = JSON.parse(localStorage.getItem(clave) ?? "null");
    if (!guardado || !COLUMNAS.every((c) => Array.isArray(guardado[c]))) return defecto;

    const conocidos = Object.values(defecto).flat();
    const vistos = new Set();
    const dist = {};
    for (const columna of COLUMNAS) {
      dist[columna] = [];
      for (const id of guardado[columna]) {
        if (conocidos.includes(id) && !vistos.has(id)) {
          vistos.add(id);
          dist[columna].push(id);
        }
      }
    }
    for (const columna of COLUMNAS) {
      for (const id of defecto[columna]) {
        if (!vistos.has(id)) {
          vistos.add(id);
          dist[columna].push(id);
        }
      }
    }
    return dist;
  } catch {
    // Dato corrupto o localStorage no disponible: se usa la distribución por defecto.
    return defecto;
  }
}

/**
 * Distribución de paneles entre columnas, con arrastre nativo (HTML5 Drag and Drop).
 * Un panel puede soltarse delante de otro panel (en cualquier columna) o al final de una columna.
 */
export function useDistribucion(clave, defecto) {
  const [dist, setDist] = useState(() => leerDistribucion(clave, defecto));
  const [arrastrando, setArrastrando] = useState(null);
  const origen = useRef(null);

  useEffect(() => {
    try {
      localStorage.setItem(clave, JSON.stringify(dist));
    } catch {
      // Sin persistencia: la distribución se mantiene durante la sesión.
    }
  }, [clave, dist]);

  function mover(id, columna, antesDe) {
    setDist((previa) => {
      const siguiente = {};
      for (const c of COLUMNAS) siguiente[c] = previa[c].filter((x) => x !== id);
      const lista = siguiente[columna];
      const posicion = antesDe ? lista.indexOf(antesDe) : -1;
      if (posicion >= 0) lista.splice(posicion, 0, id);
      else lista.push(id);
      return siguiente;
    });
  }

  function columnaDe(id) {
    return COLUMNAS.find((c) => dist[c].includes(id));
  }

  function terminar() {
    origen.current = null;
    setArrastrando(null);
  }

  // Props de arrastre para un panel concreto.
  function arrastre(id) {
    return {
      arrastrando: arrastrando === id,
      alEmpezar(evento) {
        evento.dataTransfer.effectAllowed = "move";
        evento.dataTransfer.setData("text/plain", id);
        origen.current = id;
        setArrastrando(id);
      },
      alTerminar: terminar,
      alPasarSobre(evento) {
        if (origen.current) evento.preventDefault();
      },
      alSoltarSobre(evento) {
        if (!origen.current) return;
        evento.preventDefault();
        evento.stopPropagation(); // Evita que la columna también procese el drop.
        if (origen.current !== id) mover(origen.current, columnaDe(id), id);
        terminar();
      },
    };
  }

  // Props de arrastre para una columna (zona de soltar al final).
  function zona(columna) {
    return {
      alPasarSobre(evento) {
        if (origen.current) evento.preventDefault();
      },
      alSoltar(evento) {
        if (!origen.current) return;
        evento.preventDefault();
        mover(origen.current, columna, null);
        terminar();
      },
    };
  }

  return { dist, arrastre, zona };
}
