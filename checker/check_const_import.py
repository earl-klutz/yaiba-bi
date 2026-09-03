"""
yaiba_bi.core.config下の定数にアクセスできるかをチェックする専用の実行ファイル

=>チェック範囲は全ての定数へのアクセス可否のみとする

CLIからPJルートで下記コマンドで実行
uv run python3 checker/check_const_import.py
"""


from yaiba_bi.core import config


def list_up_const(mod) -> None:
    """ 2026/08/10チェック結果

    columns.py  定数27個 => OK ... len()で判断
    defaults.py 定数28個 => OK ... len()で判断
    errors.py   定数9個  => OK ... len()で判断
    layouts.py  定数38個 => OK ... len()で判断
    paths.py    定数11個 => OK ... len()で判断
    schemas.py  定数2個  => OK ... list_up_constの処理だとimport文が全部引っかかるので、目視確認してOK

    """

    const = [{k: v} for k, v in vars(mod).items() if k.isupper()]
    print(len(const))
    for v in const:
        print(f"{v}")


if __name__ == "__main__":
    list_up_const(config.columns)
    list_up_const(config.defaults)
    list_up_const(config.errors)
    list_up_const(config.layouts)
    list_up_const(config.paths)
    list_up_const(config.schemas)
