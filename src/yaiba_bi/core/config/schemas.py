"""データスキーマ定義モジュール

YAIBA から取り込んだ生データ・中間データの「データスキーマ」を定義する。

## 目的

処理工程ごとに DataFrame が持つべき列と型を一箇所で宣言し、
取り込み処理と後工程が同じ定義を参照できるようにする。

列名・構造キーの文字列リテラルは本モジュールには持たせず、columns.py の定数
(``COL_*`` / ``SCHEMA_KEY_*``) を参照する。各列が何を表すかは columns.py を参照。
本モジュールが持つ情報は「どの列を」「どの型で」「どう束ねるか」の3点である。

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
``timestamp`` はエポック秒を表す ``float``。

### position (14列)

| 列名 | 型 |
|---|---|
| ``timestamp`` | ``float`` |
| ``player_id`` | ``int`` |
| ``pseudo_user_name`` | ``str`` |
| ``location_x`` | ``float`` |
| ``location_y`` | ``float`` |
| ``location_z`` | ``float`` |
| ``rotation_1`` | ``float`` |
| ``rotation_2`` | ``float`` |
| ``rotation_3`` | ``float`` |
| ``velocity_x`` | ``float`` |
| ``velocity_y`` | ``float`` |
| ``velocity_z`` | ``float`` |
| ``is_vr`` | ``bool`` |
| ``type_id`` | ``str`` |

### attendance (3列)

| 列名 | 型 |
|---|---|
| ``timestamp`` | ``float`` |
| ``pseudo_user_name`` | ``str`` |
| ``type_id`` | ``str`` |

## LAYOUT_INTERMEDIATE の型

後工程へ渡す中間データの型。生データから変換・付与された列を含む。
``second`` は時刻を表す ``datetime``、``event_day`` は日付のみを表す ``date`` で、
粒度が異なる点に注意。``is_error`` は型照合の結果として付与される。

### position (15列)

| 列名 | 型 |
|---|---|
| ``second`` | ``datetime`` |
| ``user_id`` | ``int`` |
| ``user_name`` | ``str`` |
| ``location_x`` | ``float`` |
| ``location_y`` | ``float`` |
| ``location_z`` | ``float`` |
| ``rotation_1`` | ``float`` |
| ``rotation_2`` | ``float`` |
| ``rotation_3`` | ``float`` |
| ``velocity_x`` | ``float`` |
| ``velocity_y`` | ``float`` |
| ``velocity_z`` | ``float`` |
| ``is_vr`` | ``bool`` |
| ``event_day`` | ``date`` |
| ``is_error`` | ``bool`` |

### attendance (4列)

| 列名 | 型 |
|---|---|
| ``second`` | ``datetime`` |
| ``action`` | ``str`` |
| ``user_name`` | ``str`` |
| ``is_error`` | ``bool`` |

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