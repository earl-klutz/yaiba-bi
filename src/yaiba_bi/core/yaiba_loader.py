from dataclasses import dataclass
from typing import Optional, Tuple
import json
from datetime import datetime
import numpy as np
import pandas as pd
import yaiba

from yaiba_bi.core import config


# ================================
# Classes
# ================================
@dataclass(frozen=True)
class Area:
    """エリアの3D境界値を保持するデータクラス。

    Args:
        x_min (float): X軸の最小値。
        x_max (float): X軸の最大値。
        y_min (float): Y軸の最小値。
        y_max (float): Y軸の最大値。
        z_min (float): Z軸の最小値。
        z_max (float): Z軸の最大値。
    """

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

class LogData:
    """ログデータを一元管理するコンテナクラス。

    位置情報・参加離脱情報・エリア境界・時間粒度を
    ゲッターメソッドで外部に公開する。
    """

    def __init__(self, position: pd.DataFrame,
                 attendance: Optional[pd.DataFrame],
                 area: Area,
                 time_span: Optional[int]) -> None:
        """各ログデータを受け取りインスタンスを初期化する。

        Args:
            position: 位置情報。
            attendance: 参加者情報。
            area (Area): エリア境界情報。
            time_span (Optional[int]): 時間粒度（秒）。
        """
        self._position = position
        self._attendance = attendance
        self._area = area
        self._time_span = time_span

    # ---- getters ----
    def get_position(self) -> pd.DataFrame:
        """位置情報を返す。

        Returns:
            位置情報。
        """
        return self._position

    def get_attendance(self) -> Optional[pd.DataFrame]:
        """参加離脱情報を返す。

        Returns:
            参加離脱情報。データが存在しない場合は None。
        """
        return self._attendance

    def get_area(self) -> Area:
        """エリア境界情報を返す。

        Returns:
            Area: X/Y/Z軸の最小・最大値を持つデータクラス。
        """
        return self._area

    def get_time_span(self) -> Optional[int]:
        """時間粒度（秒）を返す。

        Returns:
            Optional[int]: 推定された時間粒度（秒）。推定できない場合は None。
        """
        return self._time_span

# ================================
# Helpers
# ================================

# YAIBAログ由来の識別子。config/ 側に対応する定数がまだ無いため暫定でここに置く。
LOG_ENTRIES_KEY = "log_entries"
TYPE_ID_PLAYER_POSITION = "yaiba/player_position"
TYPE_ID_PLAYER_JOIN = "vrc/player_join"
TYPE_ID_PLAYER_LEFT = "vrc/player_left"
ACTION_JOIN = "join"
ACTION_LEFT = "left"
ACTION_UNKNOWN = "unknown"


def load_session_log(log_file: str) -> yaiba.SessionLog:
    """VRChatログファイルを読み込みセッションログを返す。

    Args:
        log_file (str): 読み込むログファイルのパス。

    Returns:
        yaiba.SessionLog: YAIBAがパースしたセッションログオブジェクト。

    Raises:
        ValueError: ファイルが存在しない・アクセス不可・読み込み失敗・
            パースに失敗した場合。
    """
    try:
        with open(log_file, encoding="utf-8") as fp:
            session_log = yaiba.parse_vrchat_log(fp)
    except FileNotFoundError:
        raise ValueError(f"指定されたログファイルが存在しません: {log_file}")
    except PermissionError:
        raise ValueError(f"指定されたログファイルにアクセスできません: {log_file}")
    except Exception as e:
        raise ValueError(f"ログファイルの読み込みに失敗しました: {log_file}, 詳細: {e}")

    if session_log is None:
        raise ValueError("YAIBA パースに失敗しました。session_log が None です。")

    return session_log


def get_time_span(df_pos: pd.DataFrame) -> int | None:
    """位置情報から秒粒度を推定する。

    先頭プレイヤーのタイムスタンプ差分の最頻値を
    時間粒度として返す。

    Args:
        df_pos: 位置情報。player_id および timestamp 列を含むこと。

    Returns:
        Optional[int]: 推定された秒粒度。推定できない場合は None。
    """

    # すべての差を集めるリスト
    all_diffs = []

    # player_idごとに処理
    for pid,group in df_pos.groupby(config.columns.COL_PLAYER_ID):
        # timestampで並べ替え
        group = group.sort_values(config.columns.COL_TIMESTAMP)
        timestamps = group[config.columns.COL_TIMESTAMP].tolist()
        samples = len(timestamps)//10

        # 隣同士の差を計算
        for i in range(1, samples):
            diff = timestamps[i] - timestamps[i-1]
            all_diffs.append(diff)

        break

    if len(all_diffs) == 0:
        print("差分を計算できませんでした。")
        return None
    else:
    # 最頻値を算出
        vals, counts = np.unique(all_diffs, return_counts=True)
        mode_sec = vals[np.argmax(counts)]
        return int(mode_sec)

def _normalize_action(v: str) -> str:
    """参加離脱ログのアクションを正規化する。

    Args:
        v (str): 元のアクション文字列（例: "vrc/player_join"）。

    Returns:
        str: 正規化後のアクション文字列。"join" / "left" / "unknown" のいずれか。
    """
    if v == TYPE_ID_PLAYER_JOIN:
        return ACTION_JOIN
    elif v == TYPE_ID_PLAYER_LEFT:
        return ACTION_LEFT
    else:
        return ACTION_UNKNOWN

def _isinstance_map(vals, types) -> bool:
    """値が指定した型のインスタンスかを判定する。

    Args:
        vals (Any): 型チェック対象の値。
        types (type): 比較する型。

    Returns:
        bool: vals が types のインスタンスであれば True。
    """
    return isinstance(vals,types)


# ================================
# DataEng
# ================================


def yaiba2df(session_log, schema: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """セッションログから位置情報・参加離脱情報の2表を構築する。

    YAIBAログをJSONエンコードし、スキーマに従って
    レコードを仕分けて変換する。

    Args:
        session_log (Any): YAIBAがパースしたセッションログ。
        schema (dict): 列名と型を定義したスキーマ辞書。

    Returns:
        位置情報データフレームと参加離脱情報データフレームのタプル。

    Raises:
        ValueError: YAIBAログのパース失敗または
            log_entries が存在しない場合。
    """
    try:
        encoder = yaiba.JsonEncoder(options=None)
        data = json.loads(encoder.encode(session_log))
    except Exception as e:
        # YAIBA パースに失敗したら即停止
        raise ValueError(f"YAIBA ログのパースに失敗しました: {e}")

    # log_entries がなければ即停止
    if LOG_ENTRIES_KEY not in data:
        raise ValueError("YAIBA ログに log_entries が含まれていません。")

    entry = data[LOG_ENTRIES_KEY]

    pos_records = []
    attendance_records = []


    pos_keys = schema[config.columns.SCHEMA_KEY_POSITION][config.columns.SCHEMA_KEY_KEYS]
    pos_types = schema[config.columns.SCHEMA_KEY_POSITION][config.columns.SCHEMA_KEY_TYPES]
    attendance_keys = schema[config.columns.SCHEMA_KEY_ATTENDANCE][config.columns.SCHEMA_KEY_KEYS]
    attendance_types = schema[config.columns.SCHEMA_KEY_ATTENDANCE][config.columns.SCHEMA_KEY_TYPES]

    for record in entry:

        type_id = record[config.columns.COL_TYPE_ID]
        if type_id == TYPE_ID_PLAYER_POSITION:
            L = []
            for key in pos_keys:
                L.append(record[key])
            ret = map(_isinstance_map,L,pos_types)
            is_error = False in ret
            L.append(is_error)
            pos_records.append(L)


        elif type_id in [TYPE_ID_PLAYER_JOIN, TYPE_ID_PLAYER_LEFT]:
            L = []
            for key in attendance_keys:
                L.append(record[key])
            ret = map(_isinstance_map,L,attendance_types)
            is_error = False in ret
            L.append(is_error)
            attendance_records.append(L)

    df_pos = pd.DataFrame(pos_records,columns = pos_keys+[config.columns.COL_IS_ERROR])
    df_event = pd.DataFrame(attendance_records,columns = attendance_keys+[config.columns.COL_IS_ERROR])

    return df_pos, df_event


def GenerateIntermediate(df_pos: pd.DataFrame, df_event: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """位置情報・参加離脱情報に中間列を追加して整形する。

    位置情報に second（UTC）と event_day（JST）を追加し、
    参加離脱情報に second（UTC）を付与してaction列を正規化する。

    Args:
        df_pos: 位置情報。timestamp 列を含むこと。
        df_event: 参加離脱情報。timestamp および type_id 列を含むこと。
        schema (dict): 出力列順を定義したスキーマ辞書。

    Returns:
        整形後の位置情報と参加離脱情報のタプル。
    """

    # --- position 側 ---

    if not df_pos.empty and config.columns.COL_TIMESTAMP in df_pos.columns:
        df_pos[config.columns.COL_SECOND] = pd.to_datetime(df_pos[config.columns.COL_TIMESTAMP], unit="s")
        df_pos[config.columns.COL_SECOND] = df_pos[config.columns.COL_SECOND].dt.tz_localize(config.TIMEZONE_UTC)
        df_pos[config.columns.COL_EVENT_DAY] = df_pos[config.columns.COL_SECOND].dt.tz_convert(config.TIMEZONE_JST).dt.date
        df_pos[config.columns.COL_SECOND] = df_pos[config.columns.COL_SECOND].dt.tz_localize(None)
        df_pos = df_pos.rename(columns=config.columns.RENAME_POSITION)

    # --- attendance 側 ---
    if not df_event.empty and config.columns.COL_TIMESTAMP in df_event.columns:
        df_event[config.columns.COL_SECOND] = pd.to_datetime(df_event[config.columns.COL_TIMESTAMP], unit="s")
        df_event[config.columns.COL_SECOND] = df_event[config.columns.COL_SECOND].dt.tz_localize(config.TIMEZONE_UTC)
        df_event[config.columns.COL_SECOND] = df_event[config.columns.COL_SECOND].dt.tz_localize(None)
        df_event[config.columns.COL_ACTION] = df_event[config.columns.COL_TYPE_ID].map(_normalize_action)
        df_event = df_event.drop(columns=[config.columns.COL_TYPE_ID])
        df_event = df_event.rename(columns=config.columns.RENAME_ATTENDANCE)



    # --- schema 順でカラム整列（pandas 1行方式） ---
    if not df_pos.empty:
        desired = schema[config.columns.SCHEMA_KEY_POSITION][config.columns.SCHEMA_KEY_KEYS]
        cols = [c for c in desired if c in df_pos.columns]
        df_pos = df_pos[cols]

    if not df_event.empty:
        desired = schema[config.columns.SCHEMA_KEY_ATTENDANCE][config.columns.SCHEMA_KEY_KEYS]
        cols = [c for c in desired if c in df_event.columns]
        df_event = df_event[cols]

    return df_pos, df_event

def build_area(position: pd.DataFrame) -> Area:
    """位置情報からAreaを算出する。

    location_x/y/z 各列の最小・最大値を求めて Area を生成する。
    データが空またはNoneの場合は全て0の Area を返す。

    Args:
        position: 位置情報。location_x / location_y / location_z 列を含むこと。

    Returns:
        Area: X/Y/Z軸の最小・最大値を持つAreaデータ。

    """
    if position is None or position.empty:
        return Area(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    x_min, x_max = np.nanmin(position[config.columns.COL_LOCATION_X]), np.nanmax(position[config.columns.COL_LOCATION_X])
    y_min, y_max = np.nanmin(position[config.columns.COL_LOCATION_Y]), np.nanmax(position[config.columns.COL_LOCATION_Y])
    z_min, z_max = np.nanmin(position[config.columns.COL_LOCATION_Z]), np.nanmax(position[config.columns.COL_LOCATION_Z])
    return Area(float(x_min), float(x_max),
                float(y_min), float(y_max),
                float(z_min), float(z_max))



# ================================
# データ取り込み・前処理(IO標準化)工程メイン関数
# ================================
def load(log_file: str,
        sec_interval: int = config.defaults.DEFAULT_LOAD_SEC_INTERVAL,
        anonymize: bool = config.defaults.DEFAULT_LOAD_ANONYMIZE,
        base_time: Optional[datetime] = None) -> LogData:
    """ログファイルを読み込みLogDataとして返すメイン関数。

    ログファイルの読み込み・パース・中間変換・
    エリア算出を一括して実行する。

    Args:
        log_file (str): 読み込むログファイルのパス。
        sec_interval (int): 時間粒度（秒）。デフォルト 1。
        anonymize (bool): 匿名化フラグ。デフォルト True。
        base_time (Optional[datetime]): 基準時刻。None の場合はログから自動取得。

    Returns:
        LogData: 位置情報・参加離脱情報・エリア・時間粒度を格納した LogData オブジェクト。
    """

    # --- 専用関数で読み込み＋例外処理 ---
    session_log = load_session_log(log_file)

    # 2表を構築
    df_pos, df_event = yaiba2df(session_log,config.schemas.LAYOUT_YAIBA)

    # 秒粒度の推定
    time_span = get_time_span(df_pos)
    df_pos, df_event = GenerateIntermediate(df_pos, df_event,config.schemas.LAYOUT_INTERMEDIATE)

    # Areaを算出し、LogDataに格納
    area = build_area(df_pos if not df_pos.empty else None)
    logdata = LogData(position=df_pos, attendance=df_event, area=area, time_span = time_span)

    return logdata


if __name__ == "__main__":
    log_file = r"C:\Users\tinyt\Downloads\output.txt"

    logdata = load(log_file, sec_interval=1, anonymize=True, base_time=None)
    position = logdata.get_position()
    attendance = logdata.get_attendance()
    area = logdata.get_area()
    time_span = logdata.get_time_span()


    # 動作確認（必要に応じて保存に置き換え可）
    print("Position (head):")
    print(position.head())
    print("\nAttendance (head):")
    print(attendance.head())
    print("\nArea:", area)
    print("\ntime_span:",time_span)

