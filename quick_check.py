#!/usr/bin/env python3
"""rds-postgres-quick-check

Simple tool to show top 5 slowest queries from pg_stat_statements.
"""

import argparse
import os
import sys
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

# Default connection values. Replace these for your environment or set environment variables.
DB_HOST = os.getenv("DB_HOST", "your-rds-endpoint.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "your_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "your_password")
DB_PORT = os.getenv("DB_PORT", "5432")

TOP_N = 10

QUERY_TEMPLATE = """
SELECT
    query,
    calls,
    {col} AS total_time,
    ({col} / GREATEST(calls, 1)) AS avg_time,
    rows
FROM pg_stat_statements
WHERE query != ''
  AND query NOT ILIKE '%%pg_stat_statements%%'
ORDER BY {col} DESC
LIMIT %s
"""

COLUMN_DETECTION_QUERY = """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'pg_stat_statements'
  AND column_name IN ('total_exec_time', 'total_time')
ORDER BY column_name = 'total_exec_time' DESC
LIMIT 1
"""


def format_ms(value: Any) -> str:
    try:
        return f"{float(value):.3f}"  # already in ms
    except (TypeError, ValueError):
        return "n/a"


def show_top_queries(conn_params: dict, top_n: int = TOP_N) -> None:
    print("Connecting to Postgres with:")
    print(
        f"  host={conn_params['host']} dbname={conn_params['dbname']} user={conn_params['user']} port={conn_params['port']}"
    )

    try:
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(COLUMN_DETECTION_QUERY)
                col_row = cur.fetchone()
                if not col_row:
                    print(
                        "ERROR: pg_stat_statements view not found or has unexpected columns."
                    )
                    sys.exit(1)
                time_col = col_row["column_name"]
                query = QUERY_TEMPLATE.format(col=time_col)
                cur.execute(query, (top_n,))
                rows = cur.fetchall()

                if not rows:
                    print(
                        "No rows returned. Confirm pg_stat_statements is enabled and populated."
                    )
                    return

                print("\nTop %d slowest queries (by total_time ms):\n" % top_n)
                print(
                    f"{'rank':>4} {'calls':>10} {'total_ms':>12} {'avg_ms':>10} {'rows':>8} query"
                )
                print("-" * 110)

                for i, row in enumerate(rows, start=1):
                    print(
                        f"{i:>4} {int(row['calls']):>10} {format_ms(row['total_time']):>12} {format_ms(row['avg_time']):>10} {int(row['rows']):>8} {row['query']}"
                    )

    except psycopg2.Error as exc:
        print("ERROR: could not query pg_stat_statements:")
        print(str(exc))
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quick check AWS RDS/Aurora Postgres bottlenecks via pg_stat_statements"
    )
    parser.add_argument("--host", default=DB_HOST, help="Postgres hostname or endpoint")
    parser.add_argument("--port", default=DB_PORT, help="Postgres port (default 5432)")
    parser.add_argument("--dbname", default=DB_NAME, help="Database name")
    parser.add_argument("--user", default=DB_USER, help="Username")
    parser.add_argument("--password", default=DB_PASS, help="Password")
    parser.add_argument(
        "--top", type=int, default=TOP_N, help="Top N slowest queries (default 5)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    conn_params = {
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
    }

    show_top_queries(conn_params, top_n=args.top)


if __name__ == "__main__":
    main()
