"""　カラム名定義モジュール

YAIBAの出力をPandasで解釈する際に利用するDataFrame等の列名を定義する

## 列名定数

Attributes:
    COL_SECOND (Final[str]): タイムスタンプ(秒)
    COL_USER_ID (Final[str]): ユーザー識別ID
    COL_USER_NAME (Final[str]): ユーザー名
    COL_EVENT_DAY (Final[str]): イベント日付
    COL_LOCATION_X (Final[str]): プレイヤーのX座標
    COL_LOCATION_Y (Final[str]): プレイヤーのY座標
    COL_LOCATION_Z (Final[str]): プレイヤーのZ座標
    COL_ROTATION_1 (Final[str]): プレイヤーの視点角度θ
    COL_ROTATION_2 (Final[str]): プレイヤーの視点角度φ
    COL_ROTATION_3 (Final[str]): プレイヤーの視点角度ρ
    COL_ACTION (Final[str]): レコード種別
    COL_IS_ERROR (Final[str]): レコードエラーフラグ
    COL_IS_VR (Final[str]): VRフラグ
    COL_TYPE_ID (Final[str]): レコード種別識別ID
    COL_TIMESTAMP (Final[str]): タイムスタンプ
    COL_PLAYER_ID (Final[str]): プレイヤーID
    COL_PSEUDO_USER_NAME (Final[str]): 匿名化後ユーザー名
    COL_VELOCITY_X (Final[str]): プレイヤーのX方向速度
    COL_VELOCITY_Y (Final[str]): プレイヤーのY方向速度
    COL_VELOCITY_Z (Final[str]): プレイヤーのZ方向速度

## スキーマ辞書キー

Attributes:
    SCHEMA_KEY_POSITION (Final[str]): 座標値辞書キー
    SCHEMA_KEY_ATTENDANCE (Final[str]): 入退室値辞書キー
    SCHEMA_KEY_KEYS (Final[str]): DataFrameキー一覧辞書キー
    SCHEMA_KEY_TYPES (Final[str]): DataFrame値型一覧辞書キー

## 変換マップ

Attributes:
    RENAME_POSITION (Final[Dict[str, str]]): 座標カラム名変換マップ
    RENAME_ATTENDANCE (Final[Dict[str, str]]): 入退室カラム名変換マップ

## 必須カラムリスト

Attributes:
    ATTENDANCE_REQUIRED_COLUMNS (Final[List[str]]): 入退室データフレーム必須カラムリスト

"""


from typing import (
    Final,
    Dict,
    List
)


#########################
########## 定数 ##########
#########################


# Column Name
COL_SECOND:           Final[str] = "second"
COL_USER_ID:          Final[str] = "user_id"
COL_USER_NAME:        Final[str] = "user_name"
COL_EVENT_DAY:        Final[str] = "event_day"
COL_LOCATION_X:       Final[str] = "location_x"
COL_LOCATION_Y:       Final[str] = "location_y"
COL_LOCATION_Z:       Final[str] = "location_z"
COL_ROTATION_1:       Final[str] = "rotation_1"
COL_ROTATION_2:       Final[str] = "rotation_2"
COL_ROTATION_3:       Final[str] = "rotation_3"
COL_ACTION:           Final[str] = "action"
COL_IS_ERROR:         Final[str] = "is_error"
COL_IS_VR:            Final[str] = "is_vr"
COL_TYPE_ID:          Final[str] = "type_id"
COL_TIMESTAMP:        Final[str] = "timestamp"
COL_PLAYER_ID:        Final[str] = "player_id"
COL_PSEUDO_USER_NAME: Final[str] = "pseudo_user_name"
COL_VELOCITY_X:       Final[str] = "velocity_x"
COL_VELOCITY_Y:       Final[str] = "velocity_y"
COL_VELOCITY_Z:       Final[str] = "velocity_z"

# Schema Key
SCHEMA_KEY_POSITION:   Final[str] = "position"
SCHEMA_KEY_ATTENDANCE: Final[str] = "attendance"
SCHEMA_KEY_KEYS:       Final[str] = "keys"
SCHEMA_KEY_TYPES:      Final[str] = "types"


##############################
########## 変換マップ ##########
##############################


RENAME_POSITION: Final[Dict[str, str]] = {
    COL_PLAYER_ID: COL_USER_ID,
    COL_PSEUDO_USER_NAME: COL_USER_NAME
}

RENAME_ATTENDANCE: Final[Dict[str, str]] = {
    COL_PSEUDO_USER_NAME: COL_USER_NAME
}


###################################
########## 必須カラムリスト ##########
###################################


ATTENDANCE_REQUIRED_COLUMNS: Final[List[str]] = [
    COL_SECOND,
    COL_ACTION,
    COL_USER_NAME,
    COL_IS_ERROR
]
