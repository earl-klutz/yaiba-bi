# Hanaka 軽量チェック

`movie.py` と `histogram.py` の設定参照化を検証する。pytestから独立した直接実行スクリプトであり、正式testsの代替・全体仕様の網羅テストではない。

## 基準と作業範囲

- 基準: 取得済み `origin/develop` = `4961ace689f01207810f747b59066b774ee7e884`。
- 作業場所: `C:/Users/admin/Documents/ChatGPT/yaiba_bi`、detached HEAD。
- 開始時: `master` はコミットなし、remoteなし、作業ファイル・ステージ済み差分・未追跡ファイルなし。対象originを登録してfetch後、空の作業ツリーへdevelopを展開。`HEAD...origin/develop` は `0 0`。既存のdivergedブランチを変更・統合していない。
- 変更範囲は上記2ファイルと `checker/Hanaka_check/` のみ。config、正式tests、依存定義、lock、その他実装を変更しない。
- 既存コメント・docstringの変更なし。分岐・計算・公開シグネチャ・例外条件・ログ・出力命名は維持。
- ZIPには実行指示書のみ。別添 `YAIBA-BIテスト設計書.md` はZIP・添付保存先・リポジトリ内で見つからず、原文未確認。実行指示書第8節と現行ソースを根拠とした。

## 環境・実行

リポジトリルートで既存手順の `uv sync --frozen` を実行する（lockを更新しない）。Python >=3.10、今回はPython 3.12.14。numpy、pandas、matplotlib、tqdm、tzdataに加え、coreの初期化がyaiba等をimportするため既存プロジェクト依存一式が必要。

```powershell
uv run --frozen python checker/Hanaka_check/check_movie.py
uv run --frozen python checker/Hanaka_check/check_histogram.py
uv run --frozen python -m compileall -q src/yaiba_bi/core/movie.py src/yaiba_bi/core/histogram.py checker/Hanaka_check
git diff --check
```

今回の実行は同じuv環境の `.venv/Scripts/python.exe` を直接使用。uvがPATHになかったため一時領域にuvを導入し、`uv sync --frozen` で作成した。依存バージョンは既存lockのnumpy 2.4.3、pandas 3.0.1、matplotlib 3.10.8、pytest 9.0.2。共有ランタイムに依存を追加していない。

チェックは `src/` をimport検索先頭に設定し、対象モジュールとconfigの `__file__` が作業ツリー内にあることも確認する。configをmockしない。headless backendはimport前に設定する。

## 判定・固定データ

各項目は安定したID、PASS/FAIL/SKIP、期待値、実際値を表示。失敗時には例外名も表示する。終了コードはFAILあり=1、FAILなしで必須項目の実行不能あり=2、必須項目すべてPASS=0。任意のMOV-ENCODEはSKIPでも終了0。依存の事前存在確認による不足だけを実行不能とし、import中の未知の例外や定数名の誤りはFAILとする。

`baseline.json` は基準developの既定値・型を固定したリテラルと採用参照の関数／クラス別出現数を持つ。実行時のconfigから期待値を生成しない。READMEの対応表と差分レビューで意味を照合し、REFではASTのAttributeをスコープ別に確認する。DEFAULTは全パラメータの値と型（tuple要素も含む）、BASELINEはconfig値と型・所在を確認する。この組合せで「同値のリテラルへ逆戻り」「configと本体が一緒に変化」を検出する。ソース全文一致をチェックの合格条件にはしない。

## ケース一覧

前提は上記環境、参照仕様は基準SHAの各対象関数。模擬データ生成、実行、CLI判定を分離する。乱数・実データ・ネットワークは使用しない。

| ID | 対象関数 | 前提／入力 | 期待値・判定根拠 | 後処理 |
| --- | --- | --- | --- | --- |
| MOV/HIST-IMPORT | モジュールimport | ローカルsrc | 実体パス一致、import成功 | なし |
| MOV/HIST-REF-* | 採用参照箇所 | 対象AST | baseline.jsonの関数／クラス別参照数、config import、TZ alias | なし |
| MOV/HIST-DEFAULT-* | 各パラメータクラス | 引数なし | 固定した全既定値・型 | なし |
| MOV/HIST-BASELINE-* | 採用config、TZ | 基準値 | 同値・同型、ローカルconfig。histの見送りエラー値も維持 | なし |
| MOV-BITRATE-* | _resolve_bitrate_kbps | 1200 / 1500k / 2M / bad | 1200 / 1500 / 2000 / 2000 kbps | なし |
| MOV-SMOKE | prepare, render | 固定180秒・1ユーザー・2fps・1秒動画 | 180行、JST、2フレーム、179秒間隔、960×720、scatter 2つ、初期座標(0,0)、架空氏名が注釈にない | finallyで全Figure close |
| MOV-SHORT-179 | prepare | 179秒 | PipelineError -2403 | なし |
| MOV-MISSING | prepare | location_z欠落 | PipelineError -2102 | なし |
| MOV-EMPTY | prepare | 必須列あり0行 | PipelineError -2204 | なし |
| MOV-TRAIL | prepare, render | trail=2秒 | trail点面積4.41、許容差1e-10 | finallyで全Figure close |
| MOV-ENCODE | run/save_mp4 | 任意統合項目 | SKIP。FFmpeg非起動 | なし |
| HIST-SMOKE | compute_dwell_summary, draw_histogram | A=60秒、B=120秒、Aの重複1行 | 60/120秒=1/2分、mean=median=1.5、p95=1.95、4列、Figure、基準線3本、144dpi | finallyで全Figure close |
| HIST-TIMEZONE | to_jst_floor_seconds | UTC 15:00:00.900 | JST翌日00:00:00へ秒床、event_day生成 | なし |
| HIST-NONE/EMPTY | run | None/0行 | ValueError、出力なし | runのfinally |
| HIST-MISSING | compute_dwell_summary | second欠落 | ValueError | なし |
| HIST-FILE-MISSING | run_histogram_mvp | 一時領域の不存在CSV | FileNotFoundError | TemporaryDirectory |
| HIST-IO-PRIVACY | run | 上記合成値＋架空user_name | PNG署名・パス・命名・CSV列/値・結果統計。CSVと捕捉ログに架空氏名なし | handler復元、Figure close、一時領域削除 |
| HIST-EMPTY-PLOT | draw_histogram | 空float配列 | mean/median/p95がNaN、基準線0本 | finallyで全Figure close |

MP4保存・FFmpeg・本番出力ディレクトリは軽量チェックで使わない。histは既存IOParams.out_dirからTemporaryDirectoryを指定。movieはrunがout_dirを利用せず、naming.result_pathも固定相対パスを使用するため、prepare/renderまでを実行する。Figure内部への参照はチェック側だけで使用し、全動画の保存はしない。

## 全体方針との対応

| 全体方針／具体例 | 分類 | 理由・ケース |
| --- | --- | --- |
| 正常な小規模入力、空、必須列欠落 | 今回実装 | 両SMOKE、EMPTY、MISSING |
| None | 今回実装 | HIST-NONE。movieのNoneは将来の正式tests候補 |
| 180秒境界／179秒 | 今回実装 | MOV-SMOKE、MOV-SHORT-179 |
| その他不正型、NaT、欠損user_id、境界座標、複数イベント日 | 将来の正式tests候補 | 外部参照化の軽量検証に限定。現行例外・除去条件の追加調査が必要 |
| 時刻変換、重複秒、集計、bitrate | 今回実装 | TIMEZONE、SMOKE、BITRATE |
| Figure・CSV・返却型値・命名・架空氏名非露出 | 今回実装 | SMOKE、IO-PRIVACY。ただしPNG画素・MP4内情報の網羅検査ではない |
| 現行エラー、Figure後処理 | 今回実装 | EMPTY、MISSING、SHORT、各finally |
| 不存在入力、一時領域I/O | 今回実装 | FILE-MISSING、IO-PRIVACY |
| 既存出力衝突とoverwrite、権限不足、容量不足、途中失敗時の本体資源解放 | 将来の正式tests候補 | hist overwrite未使用、movie保存系には実I/Oが伴う |
| MP4エンコード、movie.run全体 | 安全に実行できずSKIP | 任意MOV-ENCODE。既存APIでout_dir隔離できないため軽量checkから除外 |
| 他モジュールの修正、正式tests更新、大規模性能測定 | 対象外 | 担当範囲・設定参照化を超える |

## 不整合・見送り事項

| 対象 | 現行値・型 | 候補値・型 | 採否・理由 |
| --- | --- | --- | --- |
| HistParams.figsize | (10,6): tuple[int,int] | layouts.HISTOGRAM_FIGSIZE_INCHES=(10.0,6.0): tuple[float,float] | 見送り、要素型相違 |
| histogram.EC_STATS_EMPTY | -2302: int | errors.EC_STATS_EMPTY=-2303: int | 見送り、値相違 |
| histogram.EC_STATS_UNKNOWN | -2399: int | errors.EC_STATS_UNKNOWN=-2400: int、EC_INPUT_UNKNOWN=-2399: int | 見送り、前者は値相違、後者は入力カテゴリ名でrun全体の未知エラーとの意味一致を断定しない |
| movieのtz_localize/tz_convert引数 | Asia/Tokyo、UTC: str | TIMEZONE_JST/UTC: ZoneInfo | 見送り、引数型とpandasのtz実装選択を維持。モジュールのZoneInfo定数のみ参照化 |
| MovieParams.format | mp4: str | paths.FILE_EXT_MP4=.mp4: str | 見送り、値相違。文字列加工を追加しない |
| result_pathのkind | movie: str | paths.MOVIE_OUTPUT_DIR=movies: str | 見送り、APIキーとディレクトリ名は別用途 |
| p95分位点 | 0.95: float | defaults.DEFAULT_PERCENTILE_P95=95.0: float | 見送り、単位相違。計算係数変更なし |
| バージョン | c2.0/v1: str | config.VERSION=0.1.0: str | 見送り、値と用途相違 |
| movieのタイトル・軸名、FFmpegオプションキー、auto bins、out_dir未指定、sec_floor等一時列 | 既存値 | 同じ意味・型の定義なし | 維持。Noneや0/1を他用途の定数へ寄せない |
| RESULT_ROOT、build_basename、meta_paths | 既存naming参照 | 既存参照 | 維持、命名ロジック変更なし |

既存の `fontconfig.setup_fonts()` は即returnするため日本語グリフ警告が出る。画像構造・生成チェックは通るが、日本語描画の見た目は未保証。movie.renderには同名_frameの重複定義とnaive時刻のtz_convert先行呼び出しがあり、今回修正しない。設計書と現行コードでエラーコード・入出力仕様が異なる箇所もあり、現行developを維持した。

## 実行結果

2026-09-26、Windows / Python 3.12.14。独自check実行時に日本語フォントのグリフ警告あり。

| コマンド | 終了コード | 結果 |
| --- | --- | --- |
| `.venv/Scripts/python.exe checker/Hanaka_check/check_movie.py` | 0 | PASS 109 / FAIL 0 / SKIP 1（任意ENCODE） |
| `.venv/Scripts/python.exe checker/Hanaka_check/check_histogram.py` | 0 | PASS 72 / FAIL 0 / SKIP 0 |
| `.venv/Scripts/python.exe -m compileall -q src/yaiba_bi/core/movie.py src/yaiba_bi/core/histogram.py checker/Hanaka_check` | 0 | 構文チェック成功 |
| `.venv/Scripts/python.exe checker/check_const_import.py` | 0 | 全config参照を表示して正常終了 |
| `git diff --check` | 0 | 追跡済み差分の空白エラーなし |
| `.venv/Scripts/python.exe -m pytest <repo>/tests/test_histogram.py <repo>/tests/test_movie_generator.py -q --tb=short -p no:cacheprovider` | 1 | 作業版・未変更基準版とも 6 failed / 2 passed / 1 skipped |

pytestは各々TemporaryDirectory内をカレントディレクトリにし、対象のsrcをPYTHONPATHに設定して子プロセスで実行した。基準版は上記SHAをgit archiveで一時領域へ展開し、作業版を上書きせず検証。両版で同じ結果だった。

- histogramの5失敗: runのoutput_basename省略、コンストラクタのver省略、存在しないrange_min引数。正式testsと現行APIの不一致。
- movieの1失敗: trail無効の既定値では点面積1.0だが、テストは有効時の4.41を期待する。
- 1 SKIP: 既存pytestのFFmpeg実行ファイル検出がfalse。MP4保存は未検証。
- 2 PASS: movieの短いデータ・必須列欠落の例外チェック。

これらは今回導入した差分ではない。範囲外の正式tests・本体ロジックは修正しない。

差分自己レビューでは参照を基準のリテラルへ解決したASTが基準版と一致し、コメントのtoken列も一致した。これは作業時のロジック差分確認であり、軽量check自体の全文固定テストではない。新規5ファイルは直接読み、Python構文、JSON構文、末尾空白を別途確認。ステージ済み差分はない。

最終git status:

```text
## HEAD (no branch)
 M src/yaiba_bi/core/histogram.py
 M src/yaiba_bi/core/movie.py
?? checker/Hanaka_check/
```

commit・push・PR作成/更新・GitHub書き込みは実施しない。成果は人間のレビュー用に未コミットで残す。

## 採用した外部参照

以下の各行は「基準developの現行値・型 = config候補値・型」を確認して採用。秒・kbps・px・dpi・alpha等は各定数名に対応する同一単位。参照場所の詳細はbaseline.jsonのreferencesとソース差分を参照。TIMEZONE_JSTは両モジュールの既存ZoneInfo("Asia/Tokyo")と同値・同型。

| 対象 | 参照先（config配下） | 現行値＝候補値 | 型 | 採否 |
| --- | --- | --- | --- | --- |
| movie | `columns.COL_EVENT_DAY` | `'event_day'` | str | 採用：同義・同値・同型 |
| movie | `columns.COL_LOCATION_X` | `'location_x'` | str | 採用：同義・同値・同型 |
| movie | `columns.COL_LOCATION_Z` | `'location_z'` | str | 採用：同義・同値・同型 |
| movie | `columns.COL_SECOND` | `'second'` | str | 採用：同義・同値・同型 |
| movie | `columns.COL_USER_ID` | `'user_id'` | str | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_AUTO_MAX_SECONDS` | `120` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_AUTO_MIN_SECONDS` | `10` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_BITRATE_KBPS` | `2000` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_CODEC` | `'libx264'` | str | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_DURATION_REAL_SECONDS` | `10800` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_DURATION_SECONDS` | `None` | NoneType | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_FPS` | `30` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_MIN_UNIQUE_SECONDS` | `180` | int | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_MOVFLAGS` | `'+faststart'` | str | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_MOVIE_PIXEL_FORMAT` | `'yuv420p'` | str | 採用：同義・同値・同型 |
| movie | `defaults.DEFAULT_OVERWRITE` | `False` | bool | 採用：同義・同値・同型 |
| movie | `errors.EC_CU_DATA_EMPTY` | `-2204` | int | 採用：同義・同値・同型 |
| movie | `errors.EC_STATS_UNKNOWN` | `-2400` | int | 採用：同義・同値・同型 |
| movie | `errors.EC_STORAGE_DST_INVALID` | `-2701` | int | 採用：同義・同値・同型 |
| movie | `errors.EC_STORAGE_IO` | `-2704` | int | 採用：同義・同値・同型 |
| movie | `errors.EC_STORAGE_PERM` | `-2702` | int | 採用：同義・同値・同型 |
| movie | `layouts.DEFAULT_FONT_FAMILY` | `'Meiryo'` | str | 採用：同義・同値・同型 |
| movie | `layouts.DEFAULT_FONT_SIZE` | `16` | int | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_AXES_BACKGROUND_COLOR` | `'white'` | str | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_BACKGROUND_COLOR` | `'#eeeeee'` | str | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_DPI` | `120` | int | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_HEIGHT_PX` | `720` | int | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_PALETTE` | `'tab10'` | str | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_POINT_ALPHA` | `1.0` | float | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_POINT_RADIUS_PX` | `6` | int | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_TRAIL_ALPHA_END` | `0.1` | float | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_TRAIL_ALPHA_START` | `1.0` | float | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_TRAIL_LENGTH_REAL_SECONDS` | `0` | int | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_TRAIL_POINT_SCALE` | `0.35` | float | 採用：同義・同値・同型 |
| movie | `layouts.MOVIE_WIDTH_PX` | `960` | int | 採用：同義・同値・同型 |
| movie | `paths.MOVIE_FILENAME` | `'movie'` | str | 採用：同義・同値・同型 |
| histogram | `columns.COL_EVENT_DAY` | `'event_day'` | str | 採用：同義・同値・同型 |
| histogram | `columns.COL_SECOND` | `'second'` | str | 採用：同義・同値・同型 |
| histogram | `columns.COL_USER_ID` | `'user_id'` | str | 採用：同義・同値・同型 |
| histogram | `defaults.DEFAULT_CSV_ENCODING` | `'utf-8'` | str | 採用：同義・同値・同型 |
| histogram | `defaults.DEFAULT_HISTOGRAM_BINS` | `None` | NoneType | 採用：同義・同値・同型 |
| histogram | `defaults.DEFAULT_OVERWRITE` | `False` | bool | 採用：同義・同値・同型 |
| histogram | `errors.EC_STATS_INPUT` | `-2301` | int | 採用：同義・同値・同型 |
| histogram | `errors.EC_STORAGE_IO` | `-2704` | int | 採用：同義・同値・同型 |
| histogram | `errors.EC_STORAGE_PERM` | `-2702` | int | 採用：同義・同値・同型 |
| histogram | `layouts.DEFAULT_IMAGE_DPI` | `144` | int | 採用：同義・同値・同型 |
| histogram | `layouts.HISTOGRAM_EDGE_COLOR` | `'black'` | str | 採用：同義・同値・同型 |
| histogram | `layouts.HISTOGRAM_REFERENCE_LINE_STYLE` | `'--'` | str | 採用：同義・同値・同型 |
| histogram | `layouts.HISTOGRAM_TITLE` | `'YAIBA: 滞在時間の分布（JST, 1秒分解能）'` | str | 採用：同義・同値・同型 |
| histogram | `layouts.HISTOGRAM_X_LABEL` | `'在室時間 [minutes]'` | str | 採用：同義・同値・同型 |
| histogram | `layouts.HISTOGRAM_Y_LABEL` | `'人数 [counts]'` | str | 採用：同義・同値・同型 |
| histogram | `paths.FILE_EXT_CSV` | `'.csv'` | str | 採用：同義・同値・同型 |
| histogram | `paths.FILE_EXT_PNG` | `'.png'` | str | 採用：同義・同値・同型 |
| histogram | `paths.HIST_FILENAME` | `'hist_dwell'` | str | 採用：同義・同値・同型 |
| histogram | `paths.HIST_OUTPUT_DIR` | `'histograms'` | str | 採用：同義・同値・同型 |
