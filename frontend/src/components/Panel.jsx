export default function Panel({ titulo, accion, className = "", children }) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel__cabecera">
        <h2>{titulo}</h2>
        {accion}
      </header>
      {children}
    </section>
  );
}
