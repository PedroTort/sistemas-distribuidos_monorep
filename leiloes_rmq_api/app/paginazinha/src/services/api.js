// MODIFICADO: URL base do seu backend
export const API_URL = 'http://localhost:5000/'; // Porta 5000

/**
 * Função genérica para tratar requisições POST
 */
const postAPI = async (endpoint, bodyData) => {
    try {
        console.log(`Chamando POST em: ${endpoint}`, bodyData);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bodyData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Erro da API (${response.status}) em ${endpoint}:`, errorText);
            throw new Error(`Erro na API (${response.status}): ${errorText || response.statusText}`);
        }

        const text = await response.text();
        const data = text ? JSON.parse(text) : { success: true, message: `${endpoint} executado.` };
        console.log(`Resposta da API para ${endpoint}:`, data);
        return data;

    } catch (error) {
        console.error(`Falha ao chamar ${endpoint}:`, error);
        throw error;
    }
};

/**
 * NOVO: Função genérica para tratar requisições DELETE (com corpo)
 */
const deleteAPI = async (endpoint, bodyData) => {
    try {
        console.log(`Chamando DELETE em: ${endpoint}`, bodyData);
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bodyData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Erro da API (${response.status}) em ${endpoint}:`, errorText);
            throw new Error(`Erro na API (${response.status}): ${errorText || response.statusText}`);
        }

        const text = await response.text();
        const data = text ? JSON.parse(text) : { success: true, message: `${endpoint} executado.` };
        console.log(`Resposta da API para ${endpoint}:`, data);
        return data;

    } catch (error) {
        console.error(`Falha ao chamar ${endpoint}:`, error);
        throw error;
    }
};


/**
 * Cria um novo leilão.
 */
export const create_auction = async (auctionData) => {
    // MODIFICADO: Endpoint
    return postAPI('leiloes', auctionData);
};

/**
 * Busca todos os leilões ativos.
 */
export const get_auctions = async () => {
    try {
        // MODIFICADO: Endpoint
        console.log("Chamando GET em: leiloes/ativos");
        const response = await fetch(`${API_URL}leiloes/ativos`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        console.log("Resposta de leiloes/ativos:", data);
        return data;
    } catch (error) {
        console.error('Falha ao chamar get_auctions:', error);
        throw error;
    }
};

/**
 * Efetua um lance em um leilão.
 */
export const make_bid = async (auctionData) => {
    // MODIFICADO: Endpoint e corpo
    // O backend espera o corpo que o MS Lance espera, vamos apenas passar o objeto
    return postAPI('lance', auctionData);
};

/**
 * MODIFICADO: Registra interesse (inscrição) em um leilão.
 */
export const subscribe_to_auction = async (leilao_id, client_id) => {
    // O backend espera o ID na URL e o client_id no corpo
    const endpoint = `leiloes/${leilao_id}/registrar-interesse`;
    const body = { client_id: client_id };
    return postAPI(endpoint, body);
};

/**
 * MODIFICADO: Cancela interesse (remove inscrição) em um leilão.
 */
export const unsubscribe_from_auction = async (leilao_id, client_id) => {
    // O backend espera o ID na URL e o client_id no corpo
    const endpoint = `leiloes/${leilao_id}/cancelar-interesse`;
    const body = { client_id: client_id };
    // Usa o novo helper DELETE
    return deleteAPI(endpoint, body);
};

// REMOVIDO: A função get_notifications foi removida.
// Usaremos EventSource (SSE) diretamente no componente React.