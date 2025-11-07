import React, { useState } from 'react';
import { create_item, get_auctions } from './services/api'; // Importa a função da API

// 1. DEFINIÇÃO DOS ESTILOS (continua o mesmo)
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f3f4f6',
    padding: '1rem',
    fontFamily: 'Arial, sans-serif',
  },
  button: {
    padding: '1.5rem 3rem',
    backgroundColor: '#2563eb',
    color: 'white',
    fontSize: '1.5rem',
    fontWeight: 'bold',
    borderRadius: '0.5rem',
    border: 'none',
    cursor: 'pointer',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    transition: 'background-color 0.3s ease-in-out',
    minWidth: '400px', // Adicionei para os botões terem o mesmo tamanho
    textAlign: 'center',
  },
  buttonHover: {
    backgroundColor: '#1d4ed8',
  },
  buttonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
  },
  feedbackArea: {
    marginTop: '1rem', // Reduzi a margem para ficar mais perto do botão
    minHeight: '4rem', // Altura mínima
    width: '400px', // Mesmo tamanho dos botões
    textAlign: 'center',
  },
  errorText: {
    color: '#dc2626',
    fontWeight: '600',
  },
  successContainer: {
    color: '#166534',
  },
  preformatted: {
    marginTop: '0.5rem',
    backgroundColor: '#e5e7eb',
    padding: '1rem',
    borderRadius: '0.25rem',
    textAlign: 'left',
    fontSize: '0.875rem',
    color: '#1f2937',
    overflow: 'auto',
  },
};

// --- O COMPONENTE ---
function App() {
  // Estado geral
  const [isLoading, setIsLoading] = useState(false);

  // 2. ESTADOS SEPARADOS (MUITO IMPORTANTE)

  // Estados para o POST
  const [postResult, setPostResult] = useState(null);
  const [postError, setPostError] = useState(null);
  const [isPostButtonHovered, setIsPostButtonHovered] = useState(false); // Estado de hover do botão POST

  // Estados para o GET
  const [getAuctionsResult, setGetAuctionsResult] = useState(null);
  const [getAuctionsError, setGetAuctionsError] = useState(null);
  const [isGetButtonHovered, setIsGetButtonHovered] = useState(false); // Estado de hover do botão GET


  // Handler do Botão POST
  const handleButtonClick = async () => {
    setIsLoading(true);
    setPostResult(null);
    setPostError(null);

    try {
      // (Supomos que create_item() envia os dados que precisa)
      // Se precisar passar dados, seria:
      // const dados = { title: "Meu Leilão" };
      // const data = await create_item(dados);
      const data = await create_item();
      setPostResult(data);
    } catch (err) {
      setPostError(err.message || 'Ocorreu um erro desconhecido.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handler do Botão GET
  const handleButtonClickGet = async () => {
    setIsLoading(true);
    setGetAuctionsResult(null);
    setGetAuctionsError(null);

    try {
      const data = await get_auctions();
      setGetAuctionsResult(data);
    } catch (err) {
      setGetAuctionsError(err.message || 'Ocorreu um erro desconhecido.');
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Estilos dinâmicos separados
  const dynamicPostButtonStyle = {
    ...styles.button,
    ...(isPostButtonHovered && !isLoading && styles.buttonHover),
    ...(isLoading && styles.buttonDisabled),
  };

  const dynamicGetButtonStyle = {
    ...styles.button,
    marginTop: '2rem', // Espaço entre os botões
    ...(isGetButtonHovered && !isLoading && styles.buttonHover),
    ...(isLoading && styles.buttonDisabled),
  };


  return (
    // 4. Aplica os estilos usando a prop "style"
    <div style={styles.container}>

      {/* --- BOTÃO POST E SUA ÁREA DE FEEDBACK --- */}
      <button
        style={dynamicPostButtonStyle}
        onClick={handleButtonClick}
        disabled={isLoading}
        onMouseEnter={() => setIsPostButtonHovered(true)}
        onMouseLeave={() => setIsPostButtonHovered(false)}
      >
        {isLoading ? 'Carregando...' : 'Chamar API DO POST EIN'}
      </button>

      {/* Área de Feedback do POST */}
      <div style={styles.feedbackArea}>
        {postError && (
          <p style={styles.errorText}>
            Erro no POST: {postError}
          </p>
        )}
        {postResult && (
          <div style={styles.successContainer}>
            <p style={{ fontWeight: '600' }}>API (POST) respondeu:</p>
            <pre style={styles.preformatted}>
              {JSON.stringify(postResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* --- BOTÃO GET E SUA ÁREA DE FEEDBACK (O QUE VOCÊ PEDIU) --- */}
      <button
        style={dynamicGetButtonStyle}
        onClick={handleButtonClickGet} // <-- BUG CORRIGIDO AQUI
        disabled={isLoading}
        onMouseEnter={() => setIsGetButtonHovered(true)}
        onMouseLeave={() => setIsGetButtonHovered(false)}
      >
        {isLoading ? 'Carregando...' : 'Chamar API DO GET EIN'}
      </button>

      {/* Área de Feedback do GET (logo abaixo do botão GET) */}
      <div style={styles.feedbackArea}>
        {getAuctionsError && (
          <p style={styles.errorText}>
            Erro no GET: {getAuctionsError}
          </p>
        )}
        {getAuctionsResult && (
          <div style={styles.successContainer}>
            <p style={{ fontWeight: '600' }}>API (GET) respondeu:</p>
            <pre style={styles.preformatted}>
              {JSON.stringify(getAuctionsResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

    </div>
  );
}

export default App;