"""GoogleColabをUI化して利用する際に使用するモジュール

GoogleColab上で使用するディレクトリを定数で提供する

"""


import os
import shutil
from typing import Iterator

from yaiba_bi.core import config


# TODO: 参照切替で定数廃止(PR前にコメントごと削除)
# ディレクトリ定数
# BASE = "YAIBA_data"
# INPUT = f"{BASE}/input"
# INTERMEDIATE = f"{BASE}/intermediate"
# OUTPUT = f"{BASE}/output"


# 定数イテレータ
def __iters() -> Iterator[str]:
    """ディレクトリ定数を順番に取り出すイテレータを提供

    Google Colab をUIとして活用する際に使用する拡張機能 (private関数)

    Returns:
        INPUT -> INTERMEDIATE -> OUTPUT の順で値を返す
    """

    yield config.paths.COLAB_INPUT
    yield config.paths.COLAB_INTERMEDIATE
    yield config.paths.COLAB_OUTPUT


# ディレクトリ初期設定
def initialize() -> None:
    """GoogleColab上にファイルIOに必要なディレクトリを生成する

    作成するディレクトリは INPUT, INTERMEDIATE, OUTPUT

    """

    for path in __iters():
        os.makedirs(path, exist_ok=True)


# ディレクトリ後処理
def finalize() -> None:
    """GoogleColab上に作成したファイルとファイルIO用ディレクトリを削除する

    削除するディレクトリは INPUT, INTERMEDIATE, OUTPUT

    """

    shutil.rmtree(config.paths.COLAB_BASE)
