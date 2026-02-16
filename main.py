from riskline.engine.decision import decide_action


def main() -> None:
    # Placeholder entrypoint for v1 scaffold.
    action = decide_action(score=50)
    print(f"Riskline scaffold ready. Current sample action: {action}")


if __name__ == "__main__":
    main()
