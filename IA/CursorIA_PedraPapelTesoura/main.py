from controllers.game_controller import GameController


def main() -> None:
    controlador = GameController()
    controlador.executar()


if __name__ == "__main__":
    main()