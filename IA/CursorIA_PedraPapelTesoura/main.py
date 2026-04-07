import os
import sys
from pathlib import Path


def _python_do_venv() -> str | None:
    raiz = Path(__file__).resolve().parent
    for nome_venv in ("venv", ".venv"):
        python_venv = raiz / nome_venv / "bin" / "python"
        if python_venv.exists():
            return str(python_venv)
    return None


def _tentar_reexecutar_com_venv() -> bool:
    python_venv = _python_do_venv()
    if not python_venv:
        return False

    # Evita loop caso algo falhe na troca de interpretador.
    if os.environ.get("REEXEC_VENV") == "1":
        return False

    # Nao usar resolve(): em venv, o bin/python pode apontar para o mesmo alvo
    # do Python do sistema e isso impediria a troca de interpretador.
    if Path(sys.executable) == Path(python_venv):
        return False

    os.environ["REEXEC_VENV"] = "1"
    os.execv(python_venv, [python_venv, *sys.argv])
    return True


def _obter_game_controller():
    try:
        from controllers.game_controller import GameController
    except ModuleNotFoundError as erro:
        if erro.name == "pygame" and _tentar_reexecutar_com_venv():
            return None

        print("Dependencia ausente: pygame.")
        print("Instale no ambiente atual ou use o venv do projeto.")
        print("Sugestao:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        return None
    return GameController


def main() -> None:
    game_controller = _obter_game_controller()
    if game_controller is None:
        return

    controlador = game_controller()
    controlador.executar()


if __name__ == "__main__":
    main()