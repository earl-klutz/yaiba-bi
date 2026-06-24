"""YAIBA-BIの画像・動画・グラフ表示に関する標準レイアウト値。"""

from typing import Final


# 可視化共通
DEFAULT_IMAGE_WIDTH_PX: Final[int] = 1280
DEFAULT_IMAGE_HEIGHT_PX: Final[int] = 720
DEFAULT_IMAGE_DPI: Final[int] = 144

DEFAULT_FONT_FAMILY: Final[str] = "Meiryo"
DEFAULT_FONT_SIZE: Final[int] = 16
DEFAULT_FONT_FALLBACKS: Final[tuple[str, ...]] = (
    "Noto Sans CJK JP",
    "IPAGothic",
    "DejaVu Sans",
)


# 動画
MOVIE_WIDTH_PX: Final[int] = 960
MOVIE_HEIGHT_PX: Final[int] = 720
MOVIE_DPI: Final[int] = 120

MOVIE_PALETTE: Final[str] = "tab10"
MOVIE_BACKGROUND_COLOR: Final[str] = "#eeeeee"
MOVIE_AXES_BACKGROUND_COLOR: Final[str] = "white"

MOVIE_POINT_RADIUS_PX: Final[int] = 6
MOVIE_POINT_ALPHA: Final[float] = 1.0

MOVIE_TRAIL_LENGTH_REAL_SECONDS: Final[int] = 0
MOVIE_TRAIL_ALPHA_START: Final[float] = 1.0
MOVIE_TRAIL_ALPHA_END: Final[float] = 0.1
MOVIE_TRAIL_POINT_SCALE: Final[float] = 0.35


# ヒストグラム
HISTOGRAM_FIGSIZE_INCHES: Final[tuple[float, float]] = (10.0, 6.0)
HISTOGRAM_EDGE_COLOR: Final[str] = "black"
HISTOGRAM_REFERENCE_LINE_STYLE: Final[str] = "--"

HISTOGRAM_TITLE: Final[str] = "YAIBA: 滞在時間の分布（JST, 1秒分解能）"
HISTOGRAM_X_LABEL: Final[str] = "在室時間 [minutes]"
HISTOGRAM_Y_LABEL: Final[str] = "人数 [counts]"


# ヒートマップ
HEATMAP_CMAP: Final[str] = "viridis"
HEATMAP_INTERPOLATION: Final[str] = "nearest"
HEATMAP_ASPECT: Final[str] = "equal"

HEATMAP_TITLE: Final[str] = "イベントの混雑エリア"
HEATMAP_X_LABEL: Final[str] = "X座標"
HEATMAP_Z_LABEL: Final[str] = "Z座標"


# 軌跡・同時接続数グラフ
TRAJECTORY_COLOR_SCHEME: Final[str] = "by_user"
TRAJECTORY_START_MARKER_SIZE_PX: Final[int] = 6
TRAJECTORY_END_MARKER_SIZE_PX: Final[int] = 10
TRAJECTORY_MARGIN_PX: Final[int] = 0

CHART_GRID_LINE_STYLE: Final[str] = "--"
CHART_GRID_ALPHA: Final[float] = 0.3
CONCURRENCY_LINE_WIDTH: Final[float] = 1.5
CONCURRENCY_LINE_COLOR: Final[str] = "#1f77b4"