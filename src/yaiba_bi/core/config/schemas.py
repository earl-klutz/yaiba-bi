"""データスキーマ定義モジュール

YAIBA から取り込んだ生データ・中間データの「データスキーマ」を定義する。

## 目的

処理工程ごとに DataFrame が持つべき列と型を一箇所で宣言し、
取り込み処理と後工程が同じ定義を参照できるようにする。

列名・構造キーの文字列リテラルは本モジュールには持たせず、columns.py の定数
(``COL_*`` / ``SCHEMA_KEY_*``) を参照する。
本モジュールが持つ情報は「どの列を」「どの型で」「どう束ねるか」の3点である。
各列の値の意味は、後工程の実装者向けに下表にまとめる。

## 構造

各スキーマは2階層の辞書である。

| キー | 値の型 | 値の意味 |
|---|---|---|
| ``SCHEMA_KEY_POSITION`` | dict | 座標データのスキーマ |
| ``SCHEMA_KEY_ATTENDANCE`` | dict | 参加・離脱データのスキーマ |
| ``SCHEMA_KEY_KEYS`` | list[str] | 列名のリスト。DataFrame の列順を兼ねる |
| ``SCHEMA_KEY_TYPES`` | list[type] | 型のリスト |

``SCHEMA_KEY_KEYS`` と ``SCHEMA_KEY_TYPES`` は同じ長さで、同じ位置の要素が対応する。

## LAYOUT_YAIBA の型

YAIBA が出力した生データの型。値はすべて JSON から読み込んだ素の値である。

### position (14列)

1行が「ある時刻における1プレイヤーの位置・姿勢」を表す。

| 列名 | 型 | 意味・値 |
|---|---|---|
| ``timestamp`` | ``float`` | ログに記録されたローカル時刻を UTC とみなして変換したエポック秒 |
| ``player_id`` | ``int`` | 各ユーザーに自動付与されるID (VRChat がインスタンス内で割り当てる) |
| ``pseudo_user_name`` | ``str`` | 匿名化したユーザー名 |
| ``location_x`` | ``float`` | ユーザーの位置 X 座標 [m] |
| ``location_y`` | ``float`` | ユーザーの位置 Y 座標 (高さ方向) [m] |
| ``location_z`` | ``float`` | ユーザーの位置 Z 座標 [m] |
| ``rotation_1`` | ``float`` | 視点の向き。X 軸まわり (ピッチ: 上下) [度]。0 以上 360 未満 |
| ``rotation_2`` | ``float`` | 視点の向き。Y 軸まわり (ヨー: 左右) [度]。0 以上 360 未満 |
| ``rotation_3`` | ``float`` | 視点の向き。Z 軸まわり (ロール: 傾き) [度]。0 以上 360 未満 |
| ``velocity_x`` | ``float`` | X 方向の位置変化 |
| ``velocity_y`` | ``float`` | Y 方向の位置変化 |
| ``velocity_z`` | ``float`` | Z 方向の位置変化 |
| ``is_vr`` | ``bool`` | True: VR モードで参加 / False: デスクトップで参加 |
| ``type_id`` | ``str`` | レコード種別。常に ``"yaiba/player_position"`` |

単位・値域は設計書「データ取り込み・前処理(I-O標準化)」の定義に従う。

### attendance (3列)

1行が「1プレイヤーの参加または離脱」の1イベントを表す。

| 列名 | 型 | 意味・値 |
|---|---|---|
| ``timestamp`` | ``float`` | イベント発生時刻 (ログに記録されたローカル時刻) を UTC とみなして変換したエポック秒 |
| ``pseudo_user_name`` | ``str`` | 匿名化した表示名。position と同じ方法で生成される |
| ``type_id`` | ``str`` | ``"vrc/player_join"`` (参加) / ``"vrc/player_left"`` (離脱) |

## LAYOUT_INTERMEDIATE の型

後工程へ渡す中間データの型。生データから変換・付与された列を含む。
``second`` は時刻を表す ``datetime``、``event_day`` は日付のみを表す ``date`` で、
粒度が異なる点に注意。

### position (15列)

| 列名 | 型 | 意味・値 |
|---|---|---|
| ``second`` | ``datetime`` | ログデータが取得された時刻。JST|
| ``user_id`` | ``int`` | ``player_id`` を改名したもの |
| ``user_name`` | ``str`` | ``pseudo_user_name`` を改名したもの |
| ``location_x`` 〜 ``velocity_z`` | ``float`` | 生データと同じ値 (9列) |
| ``is_vr`` | ``bool`` | 生データと同じ値 |
| ``event_day`` | ``date`` | イベント開催日 (ログ取得日)。JST |
| ``is_error`` | ``bool`` | True: レコードに不備が含まれる (値が LAYOUT_YAIBA の型と一致しない) |

### attendance (4列)

| 列名 | 型 | 意味・値 |
|---|---|---|
| ``second`` | ``datetime`` | 参加・離脱した時刻。JST |
| ``action`` | ``str`` | ``"join"`` (参加) / ``"left"`` (離脱)。``type_id`` を変換したもの |
| ``user_name`` | ``str`` | ``pseudo_user_name`` を改名したもの |
| ``is_error`` | ``bool`` | position と同じ |

``action`` には変換できない場合の ``"unknown"`` も定義されているが、
取り込み時点で参加・離脱以外のレコードは除外されるため、現状は現れない。

## スキーマ定義

Attributes:
    LAYOUT_YAIBA (dict): 生データのスキーマ。yaiba2df() が各レコードの値を
        型照合する際に ``SCHEMA_KEY_TYPES`` を使用する。
    LAYOUT_INTERMEDIATE (dict): 中間データのスキーマ。GenerateIntermediate() が
        列の並べ替えに ``SCHEMA_KEY_KEYS`` を使用する。
        ``SCHEMA_KEY_TYPES`` は現在どの処理からも参照されていない。

"""


from datetime import date, datetime

from .columns import (
    # 列名定数
    COL_SECOND,
    COL_USER_ID,
    COL_USER_NAME,
    COL_EVENT_DAY,
    COL_LOCATION_X,
    COL_LOCATION_Y,
    COL_LOCATION_Z,
    COL_ROTATION_1,
    COL_ROTATION_2,
    COL_ROTATION_3,
    COL_ACTION,
    COL_IS_ERROR,
    COL_IS_VR,
    COL_TYPE_ID,
    COL_TIMESTAMP,
    COL_PLAYER_ID,
    COL_PSEUDO_USER_NAME,
    COL_VELOCITY_X,
    COL_VELOCITY_Y,
    COL_VELOCITY_Z,
    # 構造キー定数
    SCHEMA_KEY_POSITION,
    SCHEMA_KEY_ATTENDANCE,
    SCHEMA_KEY_KEYS,
    SCHEMA_KEY_TYPES,
)


###################################
########## 生データスキーマ ##########
###################################


LAYOUT_YAIBA: dict = {
    SCHEMA_KEY_POSITION: {
        SCHEMA_KEY_KEYS: [
            COL_TIMESTAMP, COL_PLAYER_ID, COL_PSEUDO_USER_NAME,
            COL_LOCATION_X, COL_LOCATION_Y, COL_LOCATION_Z,
            COL_ROTATION_1, COL_ROTATION_2, COL_ROTATION_3,
            COL_VELOCITY_X, COL_VELOCITY_Y, COL_VELOCITY_Z,
            COL_IS_VR, COL_TYPE_ID,
        ],
        SCHEMA_KEY_TYPES: [
            float, int, str,
            float, float, float,
            float, float, float,
            float, float, float,
            bool, str,
        ],
    },
    SCHEMA_KEY_ATTENDANCE: {
        SCHEMA_KEY_KEYS: [
            COL_TIMESTAMP, COL_PSEUDO_USER_NAME, COL_TYPE_ID,
        ],
        SCHEMA_KEY_TYPES: [
            float, str, str,
        ],
    },
}

###################################
########## 中間データスキーマ ##########
###################################


LAYOUT_INTERMEDIATE: dict = {
    SCHEMA_KEY_POSITION: {
        SCHEMA_KEY_KEYS: [
            COL_SECOND, COL_USER_ID, COL_USER_NAME,
            COL_LOCATION_X, COL_LOCATION_Y, COL_LOCATION_Z,
            COL_ROTATION_1, COL_ROTATION_2, COL_ROTATION_3,
            COL_VELOCITY_X, COL_VELOCITY_Y, COL_VELOCITY_Z,
            COL_IS_VR, COL_EVENT_DAY, COL_IS_ERROR,
        ],
        SCHEMA_KEY_TYPES: [
            datetime, int, str,
            float, float, float,
            float, float, float,
            float, float, float,
            bool, date, bool,
        ],
    },
    SCHEMA_KEY_ATTENDANCE: {
        SCHEMA_KEY_KEYS: [
            COL_SECOND, COL_ACTION, COL_USER_NAME, COL_IS_ERROR,
        ],
        SCHEMA_KEY_TYPES: [
            datetime, str, str,
            bool,
        ],
    },
}