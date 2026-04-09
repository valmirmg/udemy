# Projeto ToDo com Tkinter

Aplicacao simples de lista de tarefas (ToDo) em Python, com interface grafica via `tkinter` e fallback para modo texto (CLI) quando `tkinter` nao estiver disponivel.

## Requisitos

- **Python 3.10+**
- `tkinter` (necessario para a interface grafica)

### Instalacao do tkinter por sistema

- **Windows**: normalmente ja vem com a instalacao padrao do Python.
- **Ubuntu/Debian**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y python3-tk
  ```
- **Fedora**:
  ```bash
  sudo dnf install -y python3-tkinter
  ```

### Validar se o tkinter foi instalado

Depois da instalacao, execute:

```bash
python3 -m tkinter
```

Se abrir a janela de teste do Tk, a dependencia foi instalada corretamente.

## Como executar

1. Abra um terminal na pasta do projeto:
   ```bash
   cd /caminho/para/CursorIA_ToDo
   ```
2. Execute:
   ```bash
   python3 main.py
   ```

## Modos de execucao

- **Com tkinter instalado**: abre a interface grafica.
- **Sem tkinter**: inicia automaticamente no modo CLI.

### Comandos do modo CLI

- `list` -> lista tarefas
- `add <texto>` -> adiciona tarefa
- `done <id>` -> marca/desmarca como concluida
- `del <id>` -> remove tarefa
- `exit` -> encerra o programa

## Funcionalidades

- Adicionar novas tarefas.
- Marcar/desmarcar tarefas como concluidas (duplo clique ou botao, no modo grafico).
- Excluir tarefa selecionada.
- Limpar tarefas da aba atual (pendentes ou concluidas, no modo grafico).

