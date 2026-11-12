"""Which prices are rising fastest? US inflation by category (gasoline, rent, groceries, car insurance and more),
ranked by the 12-month change, with a bar chart and optional history.

    python inflation_by_category.py
    python inflation_by_category.py --history shelter,rent,food_at_home --since 2020-01

Needs a DataPorium API key in the DATAPORIUM_API_KEY environment variable.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from dataporium import DataPorium

COLUMNS = ["month", "category", "category_name", "category_group", "yoy_pct", "mom_pct", "index_nsa", "index_sa"]


def previous_month(month: str) -> str:
    year, mon = int(month[:4]), int(month[5:7])
    year, mon = (year - 1, 12) if mon == 1 else (year, mon - 1)
    return f"{year:04d}-{mon:02d}"


def latest_ranking(dp: DataPorium) -> list[dict]:
    """All categories in the newest month that has 12-month changes, fastest rising first.

    When most categories of the newest month have no 12-month change (a month a year earlier was not
    collected, as happened with October 2025), the month before is used instead.
    """
    rows = dp.inflation_categories(latest=True, limit=100).get("rows") or []
    for _ in range(3):
        if rows and sum(r.get("yoy_pct") is not None for r in rows) * 2 >= len(rows):
            break
        if not rows:
            return []
        month = previous_month(rows[0]["month"])
        rows = dp.inflation_categories(month_from=month, month_to=month, limit=100).get("rows") or []
    with_change = [r for r in rows if r.get("yoy_pct") is not None]
    return sorted(with_change, key=lambda r: r["yoy_pct"], reverse=True)


def history(dp: DataPorium, categories: str, since: str) -> list[dict]:
    rows: list[dict] = []
    while True:
        answer = dp.inflation_categories(category=categories, month_from=since, sort="month", order="asc",
                                         limit=5000, offset=len(rows))
        page = answer.get("rows") or []
        rows.extend(page)
        if len(page) < 5000 or len(rows) >= int(answer.get("total") or 0):
            return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def plot(rows: list[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = list(reversed(rows))  # largest at the top
    names = [r["category_name"] for r in rows]
    values = [r["yoy_pct"] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(rows) + 1.2))
    ax.barh(names, values, color=["#b5462f" if v > 0 else "#2f6db5" for v in values])
    for y, v in enumerate(values):
        ax.text(v, y, f" {v:+.1f}%", va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.axvline(0, color="#555", linewidth=0.8)
    ax.set_xlabel("Change in prices over 12 months (%)")
    ax.set_title(f"US inflation by category, {rows[0]['month'][:7]}")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rank US inflation by category.")
    parser.add_argument("--history", help="Also save the monthly history of these categories, e.g. shelter,rent")
    parser.add_argument("--since", default="2020-01", help="First month of the history (YYYY-MM, default 2020-01)")
    parser.add_argument("--out", default="output", help="Folder for the files (default output)")
    parser.add_argument("--no-chart", action="store_true", help="Skip the PNG chart (no matplotlib needed)")
    args = parser.parse_args(argv)

    dp = DataPorium()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ranking = latest_ranking(dp)
    if not ranking:
        print("No data returned", file=sys.stderr)
        return 1
    write_csv(out / "latest.csv", ranking)
    print(f"US inflation by category, {ranking[0]['month'][:7]} (12-month change):")
    for r in ranking:
        mom = f"{r['mom_pct']:+.1f}%" if r.get("mom_pct") is not None else "  n/a"
        print(f"  {r['category_name'][:44]:44} {r['yoy_pct']:+6.1f}%   1 month {mom}")
    if not args.no_chart:
        plot(ranking, out / "latest.png")
        print(f"Chart: {out / 'latest.png'}")

    if args.history:
        rows = history(dp, args.history, args.since)
        write_csv(out / "history.csv", rows)
        print(f"History: {len(rows)} rows in {out / 'history.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
