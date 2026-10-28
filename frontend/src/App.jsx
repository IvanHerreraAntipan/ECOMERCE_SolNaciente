import { useState } from 'react';

function App() {
  const [tema, setTema] = useState('dark-glass');

  const cambiarTema = (nuevoTema) => {
    setTema(nuevoTema);
    document.documentElement.setAttribute('data-theme', nuevoTema);
  };

  const categorias = ['Maderos', 'Gomas', 'Pelotas', 'Zapatillas', 'Mesas'];

  return (
    <div style={{ minHeight: '100vh', padding: '2rem' }}>
      {/* Barra de navegación superior estilo Glass */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '1rem 2rem',
        borderRadius: '50px',
        backgroundColor: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        backdropFilter: 'blur(12px)',
        marginBottom: '2.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🏓</span>
          <h2 style={{ margin: 0, fontWeight: '800', letterSpacing: '1px' }}>SolNaciente</h2>
        </div>

        {/* Categorías aprobadas */}
        <nav style={{ display: 'flex', gap: '1.5rem', fontWeight: '500' }}>
          {categorias.map((cat) => (
            <span key={cat} style={{ cursor: 'pointer', color: 'var(--color-text-muted)' }}>
              {cat}
            </span>
          ))}
        </nav>

        {/* Selector de los 4 temas */}
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button onClick={() => cambiarTema('dark-glass')} style={btnPill(tema === 'dark-glass')}>
            1. Dark Glass
          </button>
          <button onClick={() => cambiarTema('sol-naciente')} style={btnPill(tema === 'sol-naciente')}>
            2. Sol Naciente
          </button>
          <button onClick={() => cambiarTema('madera-carbono')} style={btnPill(tema === 'madera-carbono')}>
            3. Madera
          </button>
          <button onClick={() => cambiarTema('pelota-blanca')} style={btnPill(tema === 'pelota-blanca')}>
            4. Minimal
          </button>
        </div>
      </header>

      {/* Hero Banner estilo de la imagen */}
      <main style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{
          position: 'relative',
          padding: '3rem',
          borderRadius: '24px',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          backdropFilter: 'blur(16px)'
        }}>
          <span style={{ 
            color: 'var(--color-secondary)', 
            fontWeight: 'bold', 
            textTransform: 'uppercase', 
            fontSize: '0.85rem',
            letterSpacing: '1.5px' 
          }}>
            Equipamiento Profesional de Tenis de Mesa
          </span>
          <h1 style={{ fontSize: '2.5rem', margin: '1rem 0', maxWidth: '600px', lineHeight: 1.2 }}>
            Diseñado para campeones. Domina cada punto.
          </h1>
          <p style={{ color: 'var(--color-text-muted)', maxWidth: '500px', marginBottom: '2rem' }}>
            Maderos de carbono, gomas de alta fricción, pelotas 3 estrellas 40+, zapatillas de alta adherencia y mesas reglamentarias.
          </p>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button style={{
              backgroundColor: 'var(--color-primary)',
              color: tema === 'dark-glass' ? '#000' : '#fff',
              border: 'none',
              padding: '0.8rem 1.8rem',
              borderRadius: '30px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}>
              Ver Catálogo
            </button>
            <button style={{
              backgroundColor: 'transparent',
              color: 'var(--color-text-main)',
              border: '1px solid var(--color-border)',
              padding: '0.8rem 1.8rem',
              borderRadius: '30px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}>
              Quiénes Somos
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

const btnPill = (activo) => ({
  backgroundColor: activo ? 'var(--color-primary)' : 'transparent',
  color: activo ? (document.documentElement.getAttribute('data-theme') === 'dark-glass' || !document.documentElement.getAttribute('data-theme') ? '#000' : '#fff') : 'var(--color-text-muted)',
  border: '1px solid var(--color-border)',
  padding: '0.35rem 0.75rem',
  borderRadius: '20px',
  cursor: 'pointer',
  fontSize: '0.8rem',
  fontWeight: activo ? 'bold' : 'normal'
});

export default App;