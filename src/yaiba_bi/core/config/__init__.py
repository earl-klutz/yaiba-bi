"""
YAIBA-BIで用いる定数や初期設定値等を扱うモジュール

- columns.py: DataFrameの列名
- errors.py: エラーコード
- paths.py: 出力ルート, サブディレクトリ, 拡張子
- defaults.py: 処理の標準値
- schemas.py: YAIBA入力Schema, 中間Schema, 必須列セット
- layouts.py: 出力画像等のレイアウト関係

"""


from .columns import *
from .errors import *
from .paths import *


#########################
########## 定数 ##########
#########################


from zoneinfo import ZoneInfo


VERSION = "0.1.0"  # 仮値
TIMEZONE = ZoneInfo("Asia/Tokyo")
FONT = "NotoSansCJK-Regular.ttc"  # 暫定
