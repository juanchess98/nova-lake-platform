"""Emit shared Spark configuration as CLI-friendly arguments."""

from core.config import spark_conf_cli_args


def main() -> None:
    for item in spark_conf_cli_args():
        print(item)


if __name__ == "__main__":
    main()
