# Trab-2 - Distribuídos

## Descrição
Este projeto é parte da disciplina de Sistemas Distribuídos e utiliza Pyro para simular uma arquitetura de processos pares 

Para instalar as dependencias necessarias:

```bash
poetry install && poetry shell
```

Siga a seguinte ordem dos comandos, em terminais diferentes, para a execução correta do fluxo

```bash
pyro5-ns
```

```bash
python pyro.py PeerA
```

```bash
python pyro.py PeerB
```

```bash
python pyro.py PeerC
```

```bash
python pyro.py PeerD
```

