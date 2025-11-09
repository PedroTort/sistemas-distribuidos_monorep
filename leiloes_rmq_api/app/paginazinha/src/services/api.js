// URL base do seu backend
const API_URL = 'http://localhost:8000/';

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
        // Tenta fazer parse do JSON, mas retorna um objeto de sucesso se a resposta for vazia
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
    return postAPI('create-auction', auctionData);
};

/**
 * Busca todos os leilões ativos.
 */
export const get_auctions = async () => {
    try {
        console.log("Chamando GET em: get-auctions");
        const response = await fetch(`${API_URL}get-auctions`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        console.log("Resposta de get-auctions:", data);
        return data;
    } catch (error) {
        console.error('Falha ao chamar get_auctions:', error);
        throw error;
    }
};

/**
 * Efetua um lance em um leilão.
 */
export const make_bid = async (auctionName, bidValue, bidderName) => {
    return postAPI('make-bid', {
        auction_name: auctionName,
        bid_value: bidValue,
        bidder_name: bidderName
    });
};

/**
 * Registra interesse (inscrição) em um leilão.
 */
export const subscribe_to_auction = async (auctionName, subscriberName) => {
    return postAPI('subscribe', {
        auction_name: auctionName,
        subscriber_name: subscriberName
    });
};

/**
 * Cancela interesse (remove inscrição) em um leilão.
 */
export const unsubscribe_from_auction = async (auctionName, subscriberName) => {
    return postAPI('unsubscribe', {
        auction_name: auctionName,
        subscriber_name: subscriberName
    });
};

/**
 * (NOVA FUNÇÃO) Busca notificações para um usuário específico.
 * Assumindo que o backend tem um endpoint como /get-notifications/nomeDoUsuario
 */
export const get_notifications = async (userName) => {
    try {
        // Não usamos o console.log aqui para não poluir o console a cada 5s
        const response = await fetch(`${API_URL}get-notifications/${userName}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) {
            // Se o backend der 404 (sem notificações), não é um erro fatal
            if (response.status === 404) {
                return [];
            }
            throw new Error(`Erro ao buscar notificações: ${response.status} ${response.statusText}`);
        }
        // Assumimos que a API retorna um array de mensagens
        // Ex: [ { id: 1, text: "Novo lance de R$ 150 no Leilão X" }, ... ]
        const data = await response.json();
        return data || []; // Garante que é um array
    } catch (error) {
        console.error('Falha ao chamar get_notifications:', error);
        // Retorna array vazio em caso de falha para não quebrar a UI
        return [];
    }
};