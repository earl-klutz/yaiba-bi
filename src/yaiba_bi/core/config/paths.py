""" Path定義モジュール

YAIBA-BIで用いるPathを定義する

## Google Colab Paths

Attributes:
    COLAB_BASE (Final[str]): Google Colab上でのファイル保存先のベースディレクトリパス
    COLAB_INPUT (Final[str]): Google Colab上での入力ファイル保存ディレクトリパス
    COLAB_INTERMEDIATE (Final[str]): Google Colab上での中間ファイル保存ディレクトリパス
    COLAB_OUTPUT (Final[str]): Google Colab上での出力ファイル保存ディレクトリパス

## File Extensions

Attributes:
    FILE_EXT_CSV (Final[str]): CSVファイルの拡張子
    FILE_EXT_PNG (Final[str]): PNGファイルの拡張子
    FILE_EXT_MP4 (Final[str]): MP4ファイルの拡張子

## Histogram Path Elements

Attributes:
    HIST_OUTPUT_DIR (Final[str]): ヒストグラムの出力ディレクトリ名
    HIST_FILENAME (Final[str]): ヒストグラムのファイル名

## Movie Path Elements

Attributes:
    MOVIE_OUTPUT_DIR (Final[str]): 動画の出力ディレクトリ名
    MOVIE_FILENAME (Final[str]): 動画のファイル名

"""


from typing import Final


#########################
########## 定数 ##########
#########################


# Google Colab Paths
COLAB_BASE:         Final[str] = "YAIBA_data"
COLAB_INPUT:        Final[str] = f"{COLAB_BASE}/input"
COLAB_INTERMEDIATE: Final[str] = f"{COLAB_BASE}/intermediate"
COLAB_OUTPUT:       Final[str] = f"{COLAB_BASE}/output"


# File Extensions
FILE_EXT_CSV: Final[str] = ".csv"
FILE_EXT_PNG: Final[str] = ".png"
FILE_EXT_MP4: Final[str] = ".mp4"

# Histogram Path Elements
HIST_OUTPUT_DIR: Final[str] = "histograms"
HIST_FILENAME:   Final[str] = "hist_dwell"


# Movie Path Elements
MOVIE_OUTPUT_DIR: Final[str] = "movies"
MOVIE_FILENAME:   Final[str] = "movie"
