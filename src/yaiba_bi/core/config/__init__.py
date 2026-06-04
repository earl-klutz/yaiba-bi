"""
YAIBA-BIで用いる定数や初期設定値等を扱うモジュール

- columns.py: DataFrameの列名
- errors.py: エラーコード
- paths.py: 出力ルート, サブディレクトリ, 拡張子
- defaults.py: 処理の標準値
- schemas.py: YAIBA入力Schema, 中間Schema, 必須列セット
- layouts.py: 出力画像等のレイアウト関係

Attributes:
    VERSION (Final[str]):  バージョン情報
    TIMEZONE_UTC (Final[ZoneInfo]): 標準タイムゾーン(UTC)
    TIMEZONE_JST (Final[ZoneInfo]): ローカルタイムゾーン(JST)
    FONT (Final[str]): 標準フォントファイルパス
"""


from .columns import *
# from .errors import *
# from .paths import *

# from .defaults import *
# from .schemas import *
# from .layouts import *


# init定数用import
from typing import Final
from zoneinfo import ZoneInfo


#########################
########## 定数 ##########
#########################


VERSION:      Final[str]      = "0.1.0"  # 仮値
TIMEZONE_UTC: Final[ZoneInfo] = ZoneInfo("UTC")
TIMEZONE_JST: Final[ZoneInfo] = ZoneInfo("Asia/Tokyo")
FONT:         Final[str]      = "NotoSansCJK-Regular.ttc"  # 暫定
