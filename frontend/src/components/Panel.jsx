import { useRef } from "react";

export default function Panel({ titulo, accion, className = "", arrastre, children }) {
  const seccion = useRef(null);
  const clases = ["panel", className, arrastre?.arrastrando ? "panel--arrastrando" : ""].filter(Boolean).join(" ");

  return (
    <section
      ref={seccion}
      className={clases}
      onDragOver={arrastre?.alPasarSobre}
      onDrop={arrastre?.alSoltarSobre}
    >
      <header
        className={`panel__cabecera ${arrastre ? "panel__asa" : ""}`}
        draggable={Boolean(arrastre)}
        title={arrastre ? "Arrastra para mover el panel" : undefined}
        onDragStart={(evento) => {
          if (!arrastre) return;
          evento.dataTransfer.setDragImage(seccion.current, 24, 24);
          arrastre.alEmpezar(evento);
        }}
        onDragEnd={arrastre?.alTerminar}
      >
        {arrastre && (
          <span className="panel__agarre" aria-hidden="true">
            ⠿
          </span>
        )}
        <h2>{titulo}</h2>
        {accion}
      </header>
      {children}
    </section>
  );
}
