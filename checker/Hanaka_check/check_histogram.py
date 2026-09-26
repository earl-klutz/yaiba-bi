"""Run deterministic histogram checks with temporary output only."""
import io
import logging
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from _support import Report, defaults_and_baseline, exception_result, load_target, references


def synthetic_input(pd):
    # A has 60 unique seconds, B 120. The repeated A row adds no dwell time.
    times = pd.date_range("2026-01-02 00:00:00", periods=120, freq="s")
    return pd.DataFrame({"second": list(times[:60]) + list(times) + [times[0]],
                         "user_id": ["A"] * 60 + ["B"] * 120 + ["A"],
                         "user_name": ["HANAKA_FAKE_NAME_DO_NOT_EXPORT"] * 181})


def main():
    report = Report("HIST")
    references("histogram", report)
    m = load_target("histogram", report)
    if m is None:
        return report.finish()
    defaults_and_baseline("histogram", m, report)
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    with TemporaryDirectory(prefix="hanaka-hist-") as temp:
        gen = m.HistogramGenerator(m.IOParams(out_dir=temp), m.HistParams(), "check")
        df = synthetic_input(pd)

        def smoke():
            try:
                summary = gen.compute_dwell_summary(df)
                fig, ax, stats = gen.draw_histogram(summary["dwell_minutes"].to_numpy())
                return (isinstance(summary, pd.DataFrame), summary.columns.tolist(),
                        summary["dwell_seconds"].tolist(), summary["dwell_minutes"].tolist(),
                        summary["event_day"].tolist(), isinstance(fig, Figure),
                        stats, len(ax.lines), float(fig.dpi))
            finally:
                plt.close("all")

        report.run("SMOKE", (True, ["user_id", "dwell_seconds", "dwell_minutes", "event_day"],
                             [60, 120], [1.0, 2.0], ["2026-01-02", "2026-01-02"], True,
                             {"mean": 1.5, "median": 1.5, "p95": 1.95}, 3, 144.0), smoke)

        def timezone():
            aware = pd.DataFrame({"second": pd.to_datetime(["2026-01-01T15:00:00.900Z"]), "user_id": ["A"]})
            result = m.to_jst_floor_seconds(aware, gen.logger)
            return str(result["sec_floor"].iloc[0]), result["event_day"].iloc[0]

        report.run("TIMEZONE", ("2026-01-02 00:00:00+09:00", "2026-01-02"), timezone)
        for case, data in (("NONE", None), ("EMPTY", df.iloc[:0])):
            report.run(case, ("ValueError", None),
                       lambda data=data: exception_result(lambda: gen.run(data, "invalid")))
        report.run("MISSING", ("ValueError", None),
                   lambda: exception_result(lambda: gen.compute_dwell_summary(df.drop(columns="second"))))
        report.run("FILE-MISSING", ("FileNotFoundError", None),
                   lambda: exception_result(lambda: m.run_histogram_mvp(csv_path=Path(temp) / "absent.csv", io=gen.io)))

        def output():
            stream = io.StringIO()
            handler = logging.StreamHandler(stream)
            level = gen.logger.level
            gen.logger.addHandler(handler)
            gen.logger.setLevel(logging.INFO)
            try:
                result = gen.run(df, "synthetic")
                csv = Path(result["csv"])
                png = Path(result["png"])
                exported = pd.read_csv(csv)
                return (csv.parent == Path(temp) and png.parent == Path(temp),
                        png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n",
                        exported.columns.tolist(), exported["dwell_seconds"].tolist(),
                        result["users"], result["mean"], result["median"], result["p95"],
                        "HANAKA_FAKE_NAME" not in csv.read_text(encoding="utf-8") + stream.getvalue(),
                        png.stem.startswith("synthetic-") and png.stem.endswith("_check"),
                        not plt.get_fignums())
            finally:
                gen.logger.removeHandler(handler)
                gen.logger.setLevel(level)
                handler.close()
                plt.close("all")

        report.run("IO-PRIVACY", (True, True, ["user_id", "dwell_seconds", "dwell_minutes", "event_day"],
                                  [60, 120], 2, 1.5, 1.5, 1.95, True, True, True), output)

        def empty_plot():
            try:
                fig, ax, stats = gen.draw_histogram(np.array([], dtype=float))
                return all(np.isnan(v) for v in stats.values()) and len(ax.lines) == 0
            finally:
                plt.close("all")

        report.run("EMPTY-PLOT", True, empty_plot)
    return report.finish()


if __name__ == "__main__":
    sys.exit(main())
