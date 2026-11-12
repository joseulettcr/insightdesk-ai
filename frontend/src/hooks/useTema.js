import { useEffect, useState } from "react";

const CLAVE = "insightdesk.tema";
const TEMAS = ["claro", "oscuro"];

function leerPreferencia() {
  try {
    const guardado = localStorage.getItem(CLAVE);
    if (TEMAS.includes(guardado)) return guardado;
  } catch {
    // localStorage puede no estar disponible (modo privado, datos bloqueados).
  }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "oscuro" : "claro";
}

export function useTema() {
  const [tema, setTema] = useState(leerPreferencia);

  useEffect(() => {
    // El CSS (index.css) usa "light" / "dark" en data-theme.
    document.documentElement.dataset.theme = tema === "claro" ? "light" : "dark";
    try {
      localStorage.setItem(CLAVE, tema);
    } catch {
      // Sin persistencia: el tema sigue funcionando durante la sesión.
    }
  }, [tema]);

  const alternar = () => setTema((actual) => (actual === "claro" ? "oscuro" : "claro"));

  return { tema, alternar };
}
