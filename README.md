# Trab-1 - Distribuídos

## Descrição
Este projeto é parte da disciplina de Sistemas Distribuídos e utiliza Python para implementar funcionalidades com mensageria, transferência de arquivos e outras tarefas relacionadas ao trabalho acadêmico.

## Docker

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
```

```bash
python ./leiloes_rmq/fila_builder.py
```

```bash
python ./leiloes_rmq/ms_leilao/leilao_manager.py
```

```bash
python ./leiloes_rmq/ms_lance/lance_manager.py
```

```bash
python ./leiloes_rmq/ms_notificacao/notification_manager.py
```

Para cada usuário que dará lances:

```bash
python ./leiloes_rmq/cliente/client_manager.py
```

Para iniciar os leiloes

```bash
python ./leiloes_rmq/ms_leilao/leilao.py
```

---
