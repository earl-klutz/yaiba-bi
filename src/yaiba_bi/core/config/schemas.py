"""データスキーマ定義モジュール

YAIBA から取り込んだ生データ・中間データの「データスキーマ」を定義する。

各スキーマは columns.py で定義された列名定数 (``COL_*``) と構造キー定数
(``SCHEMA_KEY_*``) を参照し、列をどの型で・どう束ねるかを辞書として宣言する。
列名・キーの文字列リテラルは本モジュールには持たせず、columns.py を参照する。

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
            datetime, str, int,
            bool,
        ],
    },
}