const API_URL = 'http://localhost:8000/';

export const create_item = async () => {
    try {
        console.log("Chamando create_item da API");

        const response = await fetch(`${API_URL}create-auction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": "teste 4",
                "description": "description",
                "current_value": 1.5,
                "start_date": "2025-11-06T21:39:00+00:00",
                "end_date": "2025-12-06T21:39:00+00:00"
            })
        });

        console.log("Response do create_item:", response);

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        // Converte a resposta para JSON
        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Falha ao chamar a API:', error);
        throw error;
    }
};

export const get_auctions = async () => {
    try {
        const response = await fetch(`${API_URL}get-auctions`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        // Se a resposta da API não for bem-sucedida (ex: erro 404, 500)
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        // Converte a resposta para JSON
        const data = await response.json();
        return data;

    } catch (error) {
        // Captura erros (ex: rede caiu, API fora do ar)
        console.error('Falha ao chamar a API:', error);
        // Re-lança o erro para o componente React poder tratá-lo
        throw error;
    }
};