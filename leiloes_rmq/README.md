# Trab-1 - Distribuídos

## Descrição
Este projeto é parte da disciplina de Sistemas Distribuídos e utiliza Python para implementar funcionalidades com mensageria, transferência de arquivos e outras tarefas relacionadas ao trabalho acadêmico.

## Docker

Siga a seguinte ordem dos comandos para a execução correta do fluxo

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
```

Para iniciar as filas:

```bash
python .ms_leilao/init_auctions.py
```

Para iniciar o bid manager

```bash
python .ms_lance/bid_manager.py
```

Para iniciar o notification manager

```bash
python .ms_notificacao/notification_manager.py
```

Para cada usuário que dará lances:

```bash
python .client/client_manager.py
```
Para iniciar os leiloes

```bash
python .ms_leilao/auction_manager.py
```


---
