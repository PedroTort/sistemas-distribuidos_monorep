export const API_URL = 'http://localhost:5000/';

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


export const create_auction = async (auctionData) => {
    return postAPI('leiloes', auctionData);
};

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

export const make_bid = async (auctionData) => {
    return postAPI('lance', auctionData);
};


export const subscribe_to_auction = async (leilao_id, client_id) => {
    const endpoint = `leiloes/${leilao_id}/registrar-interesse`;
    const body = { client_id: client_id };
    return postAPI(endpoint, body);
};


export const unsubscribe_from_auction = async (leilao_id, client_id) => {
    const endpoint = `leiloes/${leilao_id}/cancelar-interesse`;
    const body = { client_id: client_id };
    return deleteAPI(endpoint, body);
};
