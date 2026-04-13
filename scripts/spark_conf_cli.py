"""Emit shared Spark configuration in CLI-friendly formats."""

import argparse
import shlex
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import spark_conf_cli_args


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=("runtime", "spark-sql"),
        default="runtime",
        help="Emit the shared runtime config or the spark-sql-specific wrapper config.",
    )
    parser.add_argument(
        "--format",
        choices=("argv", "submit-args"),
        default="argv",
        help="Emit newline-delimited argv items or a shell-ready submit-args string.",
    )
    parser.add_argument(
        "--master",
        help="Optional Spark master URL to prepend when using --format submit-args.",
    )
    parser.add_argument(
        "--conf",
        dest="extra_conf",
        action="append",
        default=[],
        help="Additional Spark --conf entries to append.",
    )
    parser.add_argument(
        "--include-pyspark-shell",
        action="store_true",
        help="Append pyspark-shell when using --format submit-args.",
    )
    args = parser.parse_args()

    cli_args = spark_conf_cli_args(
        include_spark_sql_cli_overrides=args.target == "spark-sql"
    )

    for config in args.extra_conf:
        cli_args.extend(["--conf", config])

    if args.format == "submit-args":
        submit_args = []
        if args.master:
            submit_args.extend(["--master", args.master])
        submit_args.extend(cli_args)
        if args.include_pyspark_shell:
            submit_args.append("pyspark-shell")
        print(shlex.join(submit_args))
        return

    for item in cli_args:
        print(item)


if __name__ == "__main__":
    main()
