"""Tests for the Monte Carlo experiment benchmark harness."""

import csv
from pathlib import Path
from pulselex.experiment import run_experiment, main


def test_run_experiment_structure_and_metrics():
    trials = 50
    rows = run_experiment(trials=trials, seed=42)
    assert len(rows) == 6

    expected_keys = {
        "bit_error_probability",
        "trials",
        "uncoded_symbol_error_rate",
        "hamming_9_5_symbol_error_rate",
        "blocks_with_correction",
        "uncoded_bits_per_symbol",
        "coded_bits_per_symbol",
    }

    for row in rows:
        assert set(row.keys()) == expected_keys
        assert row["trials"] == trials
        assert 0.0 <= row["uncoded_symbol_error_rate"] <= 1.0
        assert 0.0 <= row["hamming_9_5_symbol_error_rate"] <= 1.0
        assert row["uncoded_bits_per_symbol"] == 5
        assert row["coded_bits_per_symbol"] == 9


def test_experiment_main_csv_output(tmp_path: Path, monkeypatch):
    out_csv = tmp_path / "bench_test.csv"
    test_args = ["experiment.py", "--trials", "20", "--seed", "3", "--output", str(out_csv)]
    monkeypatch.setattr("sys.argv", test_args)

    main()

    assert out_csv.exists()
    with out_csv.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 6
        assert reader[0]["trials"] == "20"
