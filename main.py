from launcher import build_parser, choose_mode_interactively, launch


def main() -> None:
    args = build_parser().parse_args()
    mode = args.mode
    difficulty = args.difficulty
    if mode == "prompt":
        selection = choose_mode_interactively()
        if selection is None:
            print("已取消启动。")
            return
        mode, difficulty = selection

    launch(mode=mode, difficulty=difficulty, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
