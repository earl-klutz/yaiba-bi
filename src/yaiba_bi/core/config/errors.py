""" エラーコード定義モジュール

YAIBA-BIのエラーコードを定義する

## 2200番台

Attributes:
    EC_CU_DATA_EMPTY (Final[int]): 前処理後にデータが空になった

## 2300番台

Attributes:
    EC_INPUT_UNKNOWN (Final[int]): 想定外のエラー
    EC_STATS_INPUT (Final[int]): 入力値が不正
    EC_STATS_EMPTY (Final[int]): 集計対象データなし

## 2400番台

Attributes:
    EC_STATS_UNKNOWN (Final[int]): 想定外のエラー
    EC_SAMPLE_SHORT (Final[int]): サンプル数が不足

## 2700番台

Attributes:
    EC_STORAGE_DST_INVALID (Final[int]): ファイルが既に存在
    EC_STORAGE_PERM (Final[int]): 書き込み権限が不足
    EC_STORAGE_IO (Final[int]): I/O例外

"""


from typing import Final


#########################
########## 定数 ##########
#########################


# 2200番台
EC_CU_DATA_EMPTY:      Final[int] = -2204  # 前処理後にデータが空になった

# 2300番台
EC_STATS_INPUT:         Final[int] = -2301  # 入力値が不正
EC_STATS_EMPTY:         Final[int] = -2303  # 集計対象データなし
EC_INPUT_UNKNOWN:       Final[int] = -2399  # 想定外のエラー

# 2400番台
EC_STATS_UNKNOWN:       Final[int] = -2400  # 想定外のエラー
EC_SAMPLE_SHORT:        Final[int] = -2403  # サンプル数が不足

# 2700番台
EC_STORAGE_DST_INVALID: Final[int] = -2701  # ファイルが既に存在
EC_STORAGE_PERM:        Final[int] = -2702  # 書き込み権限が不足
EC_STORAGE_IO:          Final[int] = -2704  # I/O例外
