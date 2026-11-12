import inflation_by_category as ic


def r(month, cat, yoy, mom=0.1):
    return {"month": month, "category": cat, "category_name": cat.title(), "category_group": "G",
            "yoy_pct": yoy, "mom_pct": mom, "index_nsa": 1, "index_sa": 1}


class FakeClient:
    def __init__(self):
        self.calls = []

    def inflation_categories(self, **params):
        self.calls.append(params)
        if params.get("latest"):  # newest month: most 12-month changes missing
            return {"rows": [r("2026-10-01", "gasoline", 37.4), r("2026-10-01", "rent", None), r("2026-10-01", "food", None)]}
        if params.get("month_from") == "2026-09" and params.get("month_to") == "2026-09":
            return {"rows": [r("2026-09-01", "rent", 3.5), r("2026-09-01", "food", -0.4), r("2026-09-01", "gasoline", 30.0)]}
        return {"total": 2, "rows": [r("2024-01-01", "rent", 6.0), r("2024-02-01", "rent", 5.8)]}


def test_previous_month():
    assert ic.previous_month("2026-01-01") == "2025-12"
    assert ic.previous_month("2026-10-01") == "2026-09"


def test_falls_back_to_month_with_changes():
    ranking = ic.latest_ranking(FakeClient())
    assert [x["category"] for x in ranking] == ["gasoline", "rent", "food"]
    assert ranking[0]["month"] == "2026-09-01"


def test_main(tmp_path, monkeypatch):
    monkeypatch.setattr(ic, "DataPorium", FakeClient)
    assert ic.main(["--out", str(tmp_path), "--history", "rent"]) == 0
    assert (tmp_path / "latest.csv").read_text().splitlines()[1].startswith("2026-09-01,gasoline")
    assert len((tmp_path / "history.csv").read_text().splitlines()) == 3
    assert (tmp_path / "latest.png").stat().st_size > 1000
