import sqlite3
from pathlib import Path
from typing import Any

try:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import ttk
except ModuleNotFoundError:
    tk = None
    messagebox = None
    ttk = None


class TodoApp:
    def __init__(self, root: Any) -> None:
        self.root = root
        self.root.title("Lista de Tarefas")
        self.root.geometry("560x480")
        self.root.resizable(False, False)

        # listas de mapeamento entre índice visual e índice real
        self.index_map_pending: list[int] = []
        self.index_map_done: list[int] = []

        self.tasks: list[dict[str, object]] = []
        self.db_path = Path(__file__).with_name("tasks.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self._init_db()
        self._build_ui()
        self._load_tasks()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _init_db(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.conn.commit()

    def _build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#f4f5fb")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#f4f5fb")
        style.configure("TLabel", background="#f4f5fb")
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        container = ttk.Frame(self.root, padding=12, style="TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            container,
            text="Projeto ToDo",
            style="Title.TLabel",
        )
        title_label.pack(pady=(0, 10), anchor="w")

        subtitle = ttk.Label(
            container,
            text="Organize suas tarefas pendentes e concluídas.",
        )
        subtitle.pack(pady=(0, 12), anchor="w")

        input_frame = ttk.Frame(container)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.task_var = tk.StringVar()
        task_entry = ttk.Entry(
            input_frame,
            textvariable=self.task_var,
        )
        task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        task_entry.bind("<Return>", lambda event: self.add_task())

        add_button = ttk.Button(
            input_frame,
            text="Adicionar",
            width=14,
            command=self.add_task,
            style="Accent.TButton",
        )
        add_button.pack(side=tk.LEFT)

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.notebook = notebook

        pending_tab = ttk.Frame(notebook, padding=6)
        done_tab = ttk.Frame(notebook, padding=6)
        notebook.add(pending_tab, text="Pendentes")
        notebook.add(done_tab, text="Concluídas")

        # Lista de pendentes
        pending_frame = ttk.Frame(pending_tab)
        pending_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox_pending = tk.Listbox(
            pending_frame,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 11),
            activestyle="none",
        )
        self.listbox_pending.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_pending = ttk.Scrollbar(pending_frame, orient=tk.VERTICAL)
        scrollbar_pending.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_pending.config(yscrollcommand=scrollbar_pending.set)
        scrollbar_pending.config(command=self.listbox_pending.yview)

        self.listbox_pending.bind("<Double-Button-1>", lambda event: self.toggle_done())

        # Lista de concluídas
        done_frame = ttk.Frame(done_tab)
        done_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox_done = tk.Listbox(
            done_frame,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 11),
            activestyle="none",
        )
        self.listbox_done.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_done = ttk.Scrollbar(done_frame, orient=tk.VERTICAL)
        scrollbar_done.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_done.config(yscrollcommand=scrollbar_done.set)
        scrollbar_done.config(command=self.listbox_done.yview)

        self.listbox_done.bind("<Double-Button-1>", lambda event: self.toggle_done())

        # barra de ações inferior
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(fill=tk.X, pady=(0, 0))

        done_button = ttk.Button(
            buttons_frame,
            text="Marcar concluída",
            command=self.toggle_done,
        )
        done_button.pack(side=tk.LEFT)

        delete_button = ttk.Button(
            buttons_frame,
            text="Excluir tarefa",
            command=self.delete_task,
        )
        delete_button.pack(side=tk.LEFT, padx=(8, 0))

        clear_button = ttk.Button(
            buttons_frame,
            text="Limpar aba",
            command=self.clear_all,
        )
        clear_button.pack(side=tk.RIGHT)

    def add_task(self) -> None:
        text = self.task_var.get().strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite uma tarefa antes de adicionar.")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (text, done) VALUES (?, ?)",
            (text, 0),
        )
        task_id = cursor.lastrowid
        self.conn.commit()

        self.tasks.append({"id": task_id, "text": text, "done": False})
        self._refresh_listbox()
        self.task_var.set("")

    def _get_selected_index(self) -> int | None:
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            selection = self.listbox_pending.curselection()
            if not selection:
                messagebox.showinfo("Informação", "Selecione uma tarefa pendente na lista.")
                return None
            visual_index = selection[0]
            if visual_index >= len(self.index_map_pending):
                return None
            return self.index_map_pending[visual_index]
        selection = self.listbox_done.curselection()
        if not selection:
            messagebox.showinfo("Informação", "Selecione uma tarefa concluída na lista.")
            return None
        visual_index = selection[0]
        if visual_index >= len(self.index_map_done):
            return None
        return self.index_map_done[visual_index]

    def toggle_done(self) -> None:
        index = self._get_selected_index()
        if index is None:
            return

        task = self.tasks[index]
        new_done = not bool(task.get("done", False))
        task_id = int(task.get("id")) if task.get("id") is not None else None

        if task_id is not None:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE tasks SET done = ? WHERE id = ?",
                (1 if new_done else 0, task_id),
            )
            self.conn.commit()

        task["done"] = new_done
        self._refresh_listbox()

    def delete_task(self) -> None:
        index = self._get_selected_index()
        if index is None:
            return

        task = self.tasks[index]
        task_id = int(task.get("id")) if task.get("id") is not None else None

        if task_id is not None:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()

        del self.tasks[index]
        self._refresh_listbox()

    def clear_all(self) -> None:
        if not self.tasks:
            return

        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            if not any(not t.get("done", False) for t in self.tasks):
                return
            if messagebox.askyesno(
                "Confirmar",
                "Tem certeza que deseja remover todas as tarefas pendentes?",
            ):
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE done = 0")
                self.conn.commit()
                self.tasks = [t for t in self.tasks if t.get("done", False)]
        else:
            if not any(t.get("done", False) for t in self.tasks):
                return
            if messagebox.askyesno(
                "Confirmar",
                "Tem certeza que deseja remover todas as tarefas concluídas?",
            ):
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE done = 1")
                self.conn.commit()
                self.tasks = [t for t in self.tasks if not t.get("done", False)]

        self._refresh_listbox()

    def _refresh_listbox(self) -> None:
        self.listbox_pending.delete(0, tk.END)
        self.listbox_done.delete(0, tk.END)
        self.index_map_pending.clear()
        self.index_map_done.clear()

        for idx, task in enumerate(self.tasks):
            prefix = "✔" if task.get("done", False) else "•"
            text = str(task.get("text", ""))
            display = f"{prefix} {text}"
            if task.get("done", False):
                self.index_map_done.append(idx)
                self.listbox_done.insert(tk.END, display)
            else:
                self.index_map_pending.append(idx)
                self.listbox_pending.insert(tk.END, display)

    def _load_tasks(self) -> None:
        cursor = self.conn.cursor()
        try:
            rows = cursor.execute(
                "SELECT id, text, done FROM tasks ORDER BY id"
            ).fetchall()
            self.tasks = [
                {
                    "id": int(row["id"]),
                    "text": str(row["text"]),
                    "done": bool(row["done"]),
                }
                for row in rows
            ]
            self._refresh_listbox()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Erro ao carregar",
                f"Não foi possível carregar as tarefas salvas.\n\nDetalhes: {exc}",
            )

    def on_close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
        self.root.destroy()


def main() -> None:
    if tk is None:
        print("Tkinter não está disponível neste ambiente.")
        print("Iniciando em modo texto (CLI)...")
        run_cli()
        return

    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


def run_cli() -> None:
    db_path = Path(__file__).with_name("tasks.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()

    print("\nComandos: list | add <texto> | done <id> | del <id> | exit")
    while True:
        raw = input("todo> ").strip()
        if not raw:
            continue

        if raw == "exit":
            break

        if raw == "list":
            rows = conn.execute(
                "SELECT id, text, done FROM tasks ORDER BY id"
            ).fetchall()
            if not rows:
                print("Sem tarefas.")
                continue
            for row in rows:
                marker = "x" if row["done"] else " "
                print(f"[{marker}] {row['id']}: {row['text']}")
            continue

        if raw.startswith("add "):
            text = raw[4:].strip()
            if not text:
                print("Informe o texto da tarefa.")
                continue
            conn.execute("INSERT INTO tasks (text, done) VALUES (?, 0)", (text,))
            conn.commit()
            print("Tarefa adicionada.")
            continue

        if raw.startswith("done "):
            task_id = raw[5:].strip()
            if not task_id.isdigit():
                print("Informe um id numérico.")
                continue
            conn.execute(
                "UPDATE tasks SET done = CASE WHEN done = 1 THEN 0 ELSE 1 END WHERE id = ?",
                (int(task_id),),
            )
            conn.commit()
            print("Tarefa atualizada.")
            continue

        if raw.startswith("del "):
            task_id = raw[4:].strip()
            if not task_id.isdigit():
                print("Informe um id numérico.")
                continue
            conn.execute("DELETE FROM tasks WHERE id = ?", (int(task_id),))
            conn.commit()
            print("Tarefa removida.")
            continue

        print("Comando inválido.")

    conn.close()


if __name__ == "__main__":
    main()

