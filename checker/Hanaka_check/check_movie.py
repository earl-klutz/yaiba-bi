"""Run lightweight movie checks without encoding or invoking FFmpeg."""
import logging
import sys

from _support import Report, defaults_and_baseline, exception_result, load_target, references


def synthetic_input(pd, seconds=180):
    return pd.DataFrame({
        "second": pd.date_range("2026-01-02 00:00:00+09:00", periods=seconds, freq="s"),
        "user_id": ["synthetic-A"] * seconds,
        "user_name": ["HANAKA_FAKE_NAME_DO_NOT_EXPORT"] * seconds,
        "location_x": [float(i % 2) for i in range(seconds)],
        "location_y": [0.0] * seconds,
        "location_z": [float(i % 3) for i in range(seconds)],
        "event_day": ["2026-01-02"] * seconds,
    })


def main():
    report = Report("MOV")
    references("movie", report)
    m = load_target("movie", report)
    if m is None:
        return report.finish()
    defaults_and_baseline("movie", m, report)
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    for case, value, expected in (("INT", 1200, 1200), ("K", "1500k", 1500),
                                  ("M", "2M", 2000), ("INVALID", "bad", 2000)):
        report.run("BITRATE-" + case, expected, lambda v=value: m._resolve_bitrate_kbps(m.MovieParams(bitrate=v)))
    logger = logging.getLogger("hanaka.movie.check")
    gen = m.MovieGenerator(movie=m.MovieParams(duration_sec=1, fps=2))
    df = synthetic_input(pd)

    def smoke():
        try:
            prepared = gen.prepare(df, logger)
            anim, info = gen.render(prepared, logger)
            # Drawing the canvas invokes the initial animation frame, not a writer.
            anim._fig.canvas.draw()
            ax = anim._fig.axes[0]
            return (isinstance(prepared, pd.DataFrame), len(prepared), gen._event_day_str,
                    str(prepared["second"].dt.tz), isinstance(anim, FuncAnimation),
                    info["frames"], info["sec_per_frame"], len(ax.collections),
                    tuple(anim._fig.canvas.get_width_height()),
                    ax.collections[0].get_offsets().tolist(),
                    all("HANAKA_FAKE_NAME" not in t.get_text() for t in ax.texts))
        finally:
            plt.close("all")

    report.run("SMOKE", (True, 180, "2026-01-02", "Asia/Tokyo", True, 2, 179.0, 2,
                         (960, 720), [[0.0, 0.0]], True), smoke)
    report.run("SHORT-179", ("PipelineError", -2403),
               lambda: exception_result(lambda: gen.prepare(df.iloc[:179], logger)))
    report.run("MISSING", ("PipelineError", -2102),
               lambda: exception_result(lambda: gen.prepare(df.drop(columns="location_z"), logger)))
    report.run("EMPTY", ("PipelineError", -2204),
               lambda: exception_result(lambda: gen.prepare(df.iloc[:0], logger)))

    def trail():
        try:
            trial = m.MovieGenerator(movie=m.MovieParams(duration_sec=1, fps=2),
                                     trail=m.TrailParams(length_real_seconds=2))
            anim, info = trial.render(trial.prepare(df, logger), logger)
            anim._fig.canvas.draw()
            size = float(anim._fig.axes[0].collections[1].get_sizes()[0])
            return abs(size - 4.41) < 1e-10
        finally:
            plt.close("all")

    report.run("TRAIL", True, trail)
    report.emit("ENCODE", "SKIP", "MP4 integration", "not run",
                "optional: run/save_mp4 starts FFmpeg and run ignores io.out_dir", required=False)
    return report.finish()


if __name__ == "__main__":
    sys.exit(main())
