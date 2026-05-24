# Issue #37 対応：event_log_visualizer.py 共通化調査

対象ファイル: `src/yaiba_bi/core/event_log_visualizer.py`

## 方針

- 既存ロジック・関数名・戻り値は変更しない
- 定数・初期値・列名・エラーコードの `src/yaiba_bi/core/config/` への移動のみ
- 機能固有のグラフタイトル・細かい見た目設定は対象外

---

## config/paths.py — 出力先

`_Naming` クラスが持つ出力ルートとファイル名パターンを移動する。
クラスごと `paths.py` へ移動するのが自然。

| 現在の箇所 | 値 |
|---|---|
| `_Naming.RESULT_ROOT` (L126) | `Path("./YAIBA_data/output")` |
| `cc_png_path` のファイル名パターン (L145) | `"cc_line_{event_day}_{filename}.png"` |
| `trajectory_png_path` のファイル名パターン (L159) | `"traj_{event_day}_{filename}.png"` |
| `stats_txt_path` のファイル名パターン (L173) | `"stats_{event_day}_{filename}.txt"` |

---

## config/columns.py — 列名

| 定数名(案) | 値 | 使用箇所 |
|---|---|---|
| `COL_SECOND` | `"second"` | L241, 245, 246, 254, 256, 298, 387, 437, 443, 472 |
| `COL_ACTION` | `"action"` | L241, 248 |
| `COL_DELTA` | `"delta"` | L248, 249, 250 |
| `COL_CC` | `"cc"` | L256, 272, 321 |
| `COL_TIME_ALT` | `"t"` | L298, 387（`second` の代替時間列として cc・軌跡の両処理で使用） |
| `COL_USER_ID` | `"user_id"` | L437, 467, 470 |
| `COL_LOCATION_X` | `"location_x"` | L437, 476, 479, 480 |
| `COL_LOCATION_Z` | `"location_z"` | L437, 476, 479, 480 |

`_build_concurrency` 内の `action_map = {"join": 1, "left": -1}` (L247) もアクション値定数として切り出せる。

---

## config/errors.py — エラーコード

| 定数名(案) | 値 | 意味 | 使用箇所 |
|---|---|---|---|
| `ERR_INVALID_DATA` | `-2101` | データ不正・必須列不足・空データ | L243, 252, 300, 389, 440, 446 |
| `ERR_INVALID_BOUNDS` | `-2301` | 描画領域不正（幅・高さが0以下） | L458 |

---

## config/defaults.py — 初期値

### RenderConfig のデフォルト値

| 定数名(案) | 値 | 対応フィールド (L) |
|---|---|---|
| `DEFAULT_DPI` | `144` | `RenderConfig.dpi` (L82) |
| `DEFAULT_WIDTH_PX` | `1280` | `RenderConfig.width_px` (L83) |
| `DEFAULT_HEIGHT_PX` | `720` | `RenderConfig.height_px` (L84) |

### TrajectoryConfig のデフォルト値

| 定数名(案) | 値 | 対応フィールド (L) |
|---|---|---|
| `DEFAULT_COLOR_SCHEME` | `"by_user"` | `TrajectoryConfig.color_scheme` (L112) |
| `DEFAULT_BREAK_GAP_FACTOR` | `3.0` | `TrajectoryConfig.break_gap_factor` (L113) |
| `DEFAULT_START_MARKER_PX` | `6` | `TrajectoryConfig.start_marker_size_px` (L114) |
| `DEFAULT_END_MARKER_PX` | `10` | `TrajectoryConfig.end_marker_size_px` (L115) |
| `DEFAULT_FIT_MODE` | `"fit"` | `TrajectoryConfig.fit_mode` (L118) |
| `DEFAULT_MARGIN_PX` | `0` | `TrajectoryConfig.margin_px` (L119) |
| `DEFAULT_CLIP_OOB` | `True` | `TrajectoryConfig.clip_oob` (L120) |

### タイムゾーン文字列

| 定数名(案) | 値 | 使用箇所 |
|---|---|---|
| `TZ_JST` | `"Asia/Tokyo"` | L303, L443 |
| `TZ_UTC` | `"UTC"` | L245, 254, 396, 443 |

---

## 対象外

issue の方針（「機能固有の見た目設定は非対象」）に基づき、以下は共通化しない。

- グラフタイトル: `"同時接続数の推移"` (L324)、`"参加者の軌跡"` (L488)
- 軸ラベル: `"時間 (JST)"` (L322)、`"同時接続数"` (L323)、`"x [m]"` (L485)、`"z [m]"` (L486)
- 描画スタイル: `linewidth=1.5` (L321)、グリッド `alpha=0.3` (L325, 489)
- `auto_linewidth` 計算内の係数 `3.0`、`0.3` (L468)

---

## 移動量まとめ

| 移動先 | 対象の数 |
|---|---|
| `config/paths.py` | 出力ルート + ファイル名パターン 3種（`_Naming` クラスごと） |
| `config/columns.py` | 列名定数 8種 + アクション値マップ 1種 |
| `config/errors.py` | エラーコード 2種 |
| `config/defaults.py` | デフォルト値 10種 + タイムゾーン文字列 2種 |
