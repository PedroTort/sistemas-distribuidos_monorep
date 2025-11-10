import React, { useState, useEffect, useRef } from 'react';
import {
  API_URL, // MODIFICADO: Importa a URL base
  create_auction,
  get_auctions,
  make_bid,
  subscribe_to_auction,
  unsubscribe_from_auction,
  // get_notifications foi removido
} from './services/api';

// --- ESTILOS ---
const styles = {
  appContainer: {
    display: 'flex',
    flexDirection: 'row',
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
    fontFamily: 'Arial, sans-serif',
  },
  userColumn: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '2rem',
    borderRight: '2px solid #d1d5db',
  },
  userColumnTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '1rem',
  },
  loginContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginTop: '2rem',
  },
  textInput: {
    fontSize: '1rem',
    padding: '0.75rem 1rem',
    borderRadius: '0.5rem',
    border: '1px solid #9ca3af',
    minWidth: '300px',
    marginBottom: '1rem',
    boxSizing: 'border-box',
    width: '100%'
  },
  buttonGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: '1rem',
    width: '400px',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '0.5rem',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
    minWidth: '400px',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  modalTitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    margin: 0,
    marginBottom: '1rem',
  },
  modalLabel: {
    fontWeight: '600',
    fontSize: '0.875rem',
    marginBottom: '0.25rem',
    display: 'block'
  },
  feedbackArea: {
    marginTop: '1.5rem',
    width: '400px',
    textAlign: 'center',
    minHeight: '4rem', // Garante espaço mesmo vazio
  },
  errorText: {
    color: '#dc2626',
    fontWeight: '600',
    wordBreak: 'break-word',
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
    maxHeight: '300px',
  },
  buttonBase: {
    padding: '1rem 2rem',
    backgroundColor: '#2563eb',
    color: 'white',
    fontSize: '1rem',
    fontWeight: 'bold',
    borderRadius: '0.5rem',
    border: 'none',
    cursor: 'pointer',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.2s ease-in-out',
    width: '100%',
  },
  buttonHover: {
    backgroundColor: '#1d4ed8',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
  buttonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  buttonSecondary: {
    backgroundColor: '#6b7280',
  },
  buttonSecondaryHover: {
    backgroundColor: '#4b5563',
  },
  messageBox: {
    width: '400px',
    marginTop: '1.5rem',
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb',
    display: 'flex',
    flexDirection: 'column',
  },
  messageBoxTitle: {
    fontWeight: 'bold',
    color: '#374151',
    borderBottom: '1px solid #e5e7eb',
    padding: '0.75rem 1rem',
    margin: 0,
    fontSize: '1rem',
  },
  messageList: {
    height: '200px',
    overflowY: 'auto', // Adiciona scroll
    padding: '0.5rem',
    display: 'flex',
    flexDirection: 'column-reverse', // Mostra mensagens novas em baixo
  },
  messageItem: {
    padding: '0.5rem 0.75rem',
    borderBottom: '1px solid #f3f4f6',
    fontSize: '0.875rem',
    color: '#4b5563',
  },
  messageTimestamp: {
    fontSize: '0.75rem',
    color: '#9ca3af',
    display: 'block',
    marginTop: '0.25rem',
  },
  noMessages: {
    color: '#6b7280',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: '2rem',
  }
};


// --- COMPONENTE 1: StyledButton ---
function StyledButton({ onClick, disabled, children, style = {}, type = 'primary' }) {
  const [isHovered, setIsHovered] = useState(false);

  let baseStyle = type === 'primary' ? styles.buttonBase : { ...styles.buttonBase, ...styles.buttonSecondary };
  let hoverStyle = type === 'primary' ? styles.buttonHover : styles.buttonSecondaryHover;

  const dynamicStyle = {
    ...baseStyle,
    ...(isHovered && !disabled && hoverStyle),
    ...(disabled && styles.buttonDisabled),
    ...style,
  };

  return (
    <button
      style={dynamicStyle}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
    </button>
  );
}

// --- COMPONENTE 2: Modal (Popup) ---
function Modal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}


/**
 * NOVO: Helper para formatar eventos SSE em mensagens legíveis
 */
const formatMessage = (eventData) => {
  const timestamp = new Date().toISOString();
  const id = new Date().getTime(); // ID simples para a key do React
  let text = `Evento desconhecido: ${eventData.event_type}`;

  switch (eventData.event_type) {
    case 'lance_validado':
      text = `[${eventData.auction_name}] Novo lance de R$ ${eventData.bid_value.toFixed(2)} por ${eventData.user_id}.`;
      break;
    case 'lance_invalidado':
      text = `[${eventData.auction_name}] Seu lance foi considerado inválido. Motivo: ${eventData.motivo || 'N/A'}`;
      break;
    case 'leilao_vencedor':
      text = `[${eventData.auction_name}] Leilão encerrado! Vencedor: ${eventData.user_id} com R$ ${eventData.bid_value.toFixed(2)}.`;
      break;
    case 'link_pagamento':
      text = `[${eventData.auction_name}] Parabéns, você venceu! Link para pagamento: ${eventData.payment_link}`;
      break;
    case 'status_pagamento':
      text = `[${eventData.auction_name}] Atualização do pagamento: ${eventData.status}`;
      break;
    case 'sistema': // Adicionado para mensagens de conexão/erro
      text = `[Sistema] ${eventData.message}`;
      break;
    default:
      text = `[${eventData.auction_name || 'Sistema'}] ${eventData.message || JSON.stringify(eventData)}`;
      break;
  }
  return { id, timestamp, text };
};


// --- COMPONENTE 3: UserColumn ---
function UserColumn({ userTitle }) {
  const [userName, setUserName] = useState(null);
  const [tempName, setTempName] = useState("");

  const [modalType, setModalType] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Campos do formulário
  const [auctionName, setAuctionName] = useState("");
  const [auctionDesc, setAuctionDesc] = useState("");
  const [auctionValue, setAuctionValue] = useState("");
  const [auctionStart, setAuctionStart] = useState("");
  const [auctionEnd, setAuctionEnd] = useState("");
  const [bidValue, setBidValue] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [apiResult, setApiResult] = useState(null);
  const [apiError, setApiError] = useState(null);

  // NOVO ESTADO PARA AS MENSAGENS
  const [messages, setMessages] = useState([]);
  const messageListRef = useRef(null); // Ref para auto-scroll

  // --- Funções de Login ---
  const handleLogin = () => {
    if (tempName.trim()) {
      setUserName(tempName.trim());
      setApiError(null);
      setApiResult(null);
      setMessages([]); // Limpa mensagens ao logar
    }
  };

  // --- Funções do Modal ---
  const openModal = (type) => {
    setAuctionName("");
    setAuctionDesc("");
    setAuctionValue("0.00");
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const localISOTime = now.toISOString().slice(0, 16);
    setAuctionStart(localISOTime);
    setAuctionEnd(localISOTime);
    setBidValue("0.00");
    setApiError(null);
    setApiResult(null);
    setModalType(type);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setModalType(null);
  };

  const handleGetAuctions = async () => {
    setIsLoading(true);
    setApiResult(null);
    setApiError(null);
    try {
      const data = await get_auctions();
      setApiResult(data);
    } catch (err) {
      setApiError(err.message || 'Erro desconhecido ao buscar leilões.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitModal = async () => {
    if (modalType !== 'CREATE' && !auctionName.trim()) {
      setApiError("O nome do leilão é obrigatório.");
      return;
    }
    if (!userName) {
      setApiError("Usuário não está logado.");
      return;
    }
    setIsLoading(true);
    setApiResult(null);
    setApiError(null);
    try {
      let data;
      switch (modalType) {
        case 'CREATE':
          if (!auctionName || parseFloat(auctionValue) <= 0 || !auctionStart || !auctionEnd) {
            throw new Error("Preencha todos os campos do leilão (Nome, Valor > 0, Datas).");
          }
          const auctionData = {
            auction_name: auctionName,
            description: auctionDesc,
            current_value: parseFloat(auctionValue),
            start_date: new Date(auctionStart).toISOString(), // Converte para UTC
            end_date: new Date(auctionEnd).toISOString(),
          };
          data = await create_auction(auctionData);
          setApiResult(data);
          break;
        case 'BID':
          if (parseFloat(bidValue) <= 0) {
            throw new Error("O valor do lance deve ser maior que zero.");
          }
          const bidData = {
            auction_name: auctionName,
            bid_value: parseFloat(bidValue),
            bidder_name: userName
          };
          data = await make_bid(bidData);
          setApiResult(data);
          break;
        case 'SUBSCRIBE':
          data = await subscribe_to_auction(auctionName, userName);
          setApiResult(data);
          break;
        case 'UNSUBSCRIBE':
          data = await unsubscribe_from_auction(auctionName, userName);
          setApiResult(data);
          break;
        default:
          throw new Error("Ação desconhecida.");
      }

      // Limpa os campos do modal e fecha
      setTimeout(() => {
        closeModal();
      }, 1500); // Fecha após 1.5s para ver a mensagem de sucesso

    } catch (err) {
      setApiError(err.message || `Erro ao executar ${modalType}.`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Renderização do Modal ---
  const renderModalContent = () => {
    const auctionNameInput = (
      <div>
        <label style={styles.modalLabel}>Nome do Leilão:</label>
        <input type="text" style={styles.textInput} value={auctionName} onChange={(e) => setAuctionName(e.target.value)} placeholder="Ex: Leilão do Apartamento" disabled={isLoading} />
      </div>
    );
    let title = "";
    let content = null;
    switch (modalType) {
      case 'CREATE':
        title = "Criar Novo Leilão";
        content = (
          <>
            {auctionNameInput}
            <div><label style={styles.modalLabel}>Descrição:</label><input type="text" style={styles.textInput} value={auctionDesc} onChange={(e) => setAuctionDesc(e.target.value)} placeholder="Descrição (opcional)" disabled={isLoading} /></div>
            <div><label style={styles.modalLabel}>Valor Inicial (R$):</label><input type="number" style={styles.textInput} value={auctionValue} min="0.01" step="0.01" onChange={(e) => setAuctionValue(e.target.value)} disabled={isLoading} /></div>
            <div><label style={styles.modalLabel}>Data de Início:</label><input type="datetime-local" style={styles.textInput} value={auctionStart} onChange={(e) => setAuctionStart(e.target.value)} disabled={isLoading} /></div>
            <div><label style={styles.modalLabel}>Data de Fim:</label><input type="datetime-local" style={styles.textInput} value={auctionEnd} onChange={(e) => setAuctionEnd(e.target.value)} disabled={isLoading} /></div>
          </>
        );
        break;
      case 'BID':
        title = "Efetuar Lance";
        content = (
          <>
            {auctionNameInput}
            <div><label style={styles.modalLabel}>Valor do Lance (R$):</label><input type="number" style={styles.textInput} value={bidValue} min="0.01" step="0.01" onChange={(e) => setBidValue(e.target.value)} placeholder="Ex: 150.50" disabled={isLoading} /></div>
          </>
        );
        break;
      case 'SUBSCRIBE':
        title = "Registar Interesse";
        content = auctionNameInput;
        break;
      case 'UNSUBSCRIBE':
        title = "Cancelar Interesse";
        content = auctionNameInput;
        break;
      default:
        return null;
    }
    return (
      <>
        <h2 style={styles.modalTitle}>{title}</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {content}
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <StyledButton onClick={handleSubmitModal} disabled={isLoading} style={{ flex: 2 }}>
              {isLoading ? "Processando..." : "Confirmar"}
            </StyledButton>
            <StyledButton onClick={closeModal} disabled={isLoading} type="secondary" style={{ flex: 1 }}>
              Cancelar
            </StyledButton>
          </div>
          <div style={styles.feedbackArea}>
            {apiError && <p style={styles.errorText}>{apiError}</p>}
            {apiResult && (
              <div style={styles.successContainer}>
                <p style={{ fontWeight: '600' }}>Sucesso!</p>
                <pre style={styles.preformatted}>{JSON.stringify(apiResult, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      </>
    );
  };

  // --- MODIFICADO: Lógica de Notificações (SSE) ---
  useEffect(() => {
    if (!userName) {
      setMessages([]);
      return;
    }

    console.log(`Conectando ao SSE como: ${userName}`);
    // Conecta ao endpoint de eventos do backend
    const eventSource = new EventSource(`${API_URL}eventos/${userName}`);

    // Ocorre quando a conexão é aberta
    eventSource.onopen = () => {
      console.log("Conexão SSE aberta com o servidor.");
      setMessages(prev => [
        formatMessage({ event_type: 'sistema', message: 'Conectado ao servidor de eventos.' }),
        ...prev
      ]);
    };

    // Ocorre quando uma nova mensagem (evento) é recebida
    eventSource.onmessage = (event) => {
      try {
        const eventData = JSON.parse(event.data);
        console.log("Evento SSE recebido:", eventData);

        // Formata a mensagem e adiciona no início da lista
        const novaMensagem = formatMessage(eventData);
        setMessages(prev => [novaMensagem, ...prev]);

      } catch (error) {
        console.error("Erro ao processar mensagem SSE:", error, event.data);
      }
    };

    // Ocorre se houver um erro na conexão
    eventSource.onerror = (error) => {
      console.error("Erro na conexão SSE:", error);
      setMessages(prev => [
        formatMessage({ event_type: 'sistema', message: 'Erro na conexão de eventos. Tentando reconectar...' }),
        ...prev
      ]);
      // O EventSource tentará reconectar automaticamente
    };

    // Função de limpeza: Fecha a conexão quando o componente desmonta ou o userName muda
    return () => {
      console.log("Fechando conexão SSE.");
      eventSource.close();
    };

  }, [userName]); // Depende do userName

  // NOVO: useEffect para auto-scroll da caixa de mensagens
  useEffect(() => {
    if (messageListRef.current) {
      // Com 'flex-direction: column-reverse', rolar para o topo (0)
      // mostra o conteúdo mais recente (que está no fundo do flex).
      messageListRef.current.scrollTop = 0;
    }
  }, [messages]); // Roda sempre que as mensagens mudarem


  // --- Renderização da Coluna ---
  return (
    <div style={styles.userColumn}>
      <h1 style={styles.userColumnTitle}>
        {userTitle} {userName ? `(Logado como: ${userName})` : "(Offline)"}
      </h1>

      {!userName ? (
        <div style={styles.loginContainer}>
          <input
            type="text"
            placeholder="Digite seu nome de usuário"
            style={styles.textInput}
            value={tempName}
            onChange={(e) => setTempName(e.target.value)}
          />
          <StyledButton
            onClick={handleLogin}
            disabled={!tempName.trim()}
            style={{ width: '300px' }}
          >
            Entrar
          </StyledButton>
        </div>
      ) : (
        <div style={styles.buttonGrid}>
          <StyledButton onClick={() => openModal('CREATE')} disabled={isLoading}>
            Criar Leilão
          </StyledButton>
          <StyledButton onClick={handleGetAuctions} disabled={isLoading}>
            {isLoading && !isModalOpen ? "Consultando..." : "Consultar Leilões Ativos"}
          </StyledButton>
          <StyledButton onClick={() => openModal('BID')} disabled={isLoading}>
            Efetuar Lance
          </StyledButton>
          <StyledButton onClick={() => openModal('SUBSCRIBE')} disabled={isLoading}>
            Registar Interesse
          </StyledButton>
          <StyledButton onClick={() => openModal('UNSUBSCRIBE')} disabled={isLoading}>
            Cancelar Interesse
          </StyledButton>
        </div>
      )}

      {/* Área de Feedback (para 'Consultar Leilões') */}
      <div style={styles.feedbackArea}>
        {!isModalOpen && apiError && <p style={styles.errorText}>{apiError}</p>}
        {!isModalOpen && apiResult && (
          <div style={styles.successContainer}>
            <p style={{ fontWeight: '600' }}>Resultado:</p>
            <pre style={styles.preformatted}>{JSON.stringify(apiResult, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* NOVA CAIXA DE NOTIFICAÇÕES (renderiza se estiver logado) */}
      {userName && (
        <div style={styles.messageBox}>
          <h3 style={styles.messageBoxTitle}>Caixa de Notificações (SSE)</h3>
          <div style={styles.messageList} ref={messageListRef}>
            {/* Usamos 'flex-direction: column-reverse' no estilo, 
                          então o .map() normal vai renderizar de baixo para cima. 
                          As mensagens já são adicionadas no início do array (ex: [msg3, msg2, msg1])
                        */}
            {messages.length === 0 ? (
              <p style={styles.noMessages}>Nenhuma notificação por enquanto.</p>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} style={styles.messageItem}>
                  {msg.text}
                  {msg.timestamp && (
                    <span style={styles.messageTimestamp}>
                      {new Date(msg.timestamp).toLocaleString('pt-BR')}
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Modal (Popup) */}
      <Modal isOpen={isModalOpen} onClose={isLoading ? () => { } : closeModal}>
        {renderModalContent()}
      </Modal>
    </div>
  );
}

// --- COMPONENTE FINAL: App ---
function App() {
  return (
    <div style={styles.appContainer}>
      <UserColumn userTitle="Usuário A" />
      <UserColumn userTitle="Usuário B" />
    </div>
  );
}

export default App;