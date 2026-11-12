import { useCallback, useEffect, useState } from "react";

export function useRecurso(fetcher) {
  const [version, setVersion] = useState(0);
  const [estado, setEstado] = useState({ cargando: true, datos: null, error: null });

  useEffect(() => {
    let activo = true;
    setEstado((previo) => ({ ...previo, cargando: true, error: null }));

    fetcher()
      .then((datos) => {
        if (activo) setEstado({ cargando: false, datos, error: null });
      })
      .catch((error) => {
        if (activo) setEstado({ cargando: false, datos: null, error: error.message });
      });

    return () => {
      activo = false;
    };
  }, [fetcher, version]);

  const recargar = useCallback(() => setVersion((v) => v + 1), []);

  return { ...estado, recargar };
}
