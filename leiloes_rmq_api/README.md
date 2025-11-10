# Trab-1 - Distribuídos

## Descrição
Este projeto é parte da disciplina de Sistemas Distribuídos e utiliza Python para implementar funcionalidades com mensageria, transferência de arquivos e outras tarefas relacionadas ao trabalho acadêmico.

## Docker

Siga a seguinte ordem dos comandos para a execução correta do fluxo

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
```

```bash
sudo systemctl start rabbitmq-server
```

```bash
uvicorn api.gateway:app --host 0.0.0.0 --port 5000 --reload
```

```bash
uvicorn ms_leilao.auction:app --host 0.0.0.0 --port 5001 --reload
```

```bash
uvicorn ms_lance.bid:app --host 0.0.0.0 --port 5002 --reload
```

```bash
uvicorn ms_pagamento.payment:app --host 0.0.0.0 --port 5003 --reload
```
