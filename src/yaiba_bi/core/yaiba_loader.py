from dataclasses import dataclass
from typing import Optional, Tuple
import json
from datetime import datetime, date
import numpy as np
import pandas as pd
import yaiba


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
            attendance: 参加離脱情報。データが存在しない場合は None。
            area (Area): エリア境界情報。
            time_span (Optional[int]): 時間粒度（秒）。推定できない場合は None。
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

schema_yaiba = {
    "position": {
        "keys": [
            "timestamp", "player_id", "pseudo_user_name",
            "location_x", "location_y", "location_z",
            "rotation_1", "rotation_2", "rotation_3",
            "velocity_x", "velocity_y", "velocity_z",
            "is_vr", "type_id",
        ],
        "types": [
            float, int, str,
            float, float, float,
            float, float, float,
            float, float, float,
            bool, str
        ],
    },
    "attendance": {
        "keys": ["timestamp", "pseudo_user_name", "type_id"],
        "types": [float, str, str],
    },
}

schema_intermediate = {
    "position": {
        "keys": [
            "second", "user_id", "user_name",
            "location_x", "location_y", "location_z",
            "rotation_1", "rotation_2", "rotation_3",
            "velocity_x", "velocity_y", "velocity_z",
            "is_vr", "event_day", "is_error"
        ],
        "types": [
            datetime, int, str,
            float, float, float,
            float, float, float,
            float, float, float,
            bool, date, bool
        ]
    },
    "attendance": {
        "keys": [
            "second", "action", "user_name",
            "is_error"
        ],
        "types": [
            datetime, str, int,
            bool
        ]
    }
}


def load_session_log(log_file: str):
    """ログファイルを読み込み、session_log を生成する。

    Args:
        log_file (str): 読み込むログファイルのパス。

    Returns:
        YAIBA によりパースされた session_log オブジェクト。

    Raises:
        ValueError: ファイルが存在しない、アクセスできない、
            または YAIBA パースに失敗した場合。
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
    """位置データから秒粒度を推定する。

    player_id ごとに timestamp の差分の最頻値を算出する。

    Args:
        df_pos (pd.DataFrame): player_id と timestamp を含む位置データ。

    Returns:
        推定された秒粒度。差分が計算できない場合は None。
    """

    # すべての差を集めるリスト
    all_diffs = []

    # player_idごとに処理
    for pid, group in df_pos.groupby("player_id"):
        # timestampで並べ替え
        group = group.sort_values("timestamp")
        timestamps = group["timestamp"].tolist()
        samples = len(timestamps) // 10

        # 隣同士の差を計算
        for i in range(1, samples):
            diff = timestamps[i] - timestamps[i - 1]
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
    """attendance 用の action 値を正規化する。

    Args:
        v (str): 正規化対象のイベント種別文字列。

    Returns:
        `join`、`left`、`unknown` のいずれか。
    """
    if v == "vrc/player_join":
        return "join"
    elif v == "vrc/player_left":
        return "left"
    else:
        return "unknown"


def _isinstance_map(vals, types) -> bool:
    """値が指定型に一致するか判定する。

    Args:
        vals: 判定対象の値。
        types: 想定する型。

    Returns:
        値が指定型に一致する場合は True。
    """
    return isinstance(vals, types)


# ================================
# DataEng
# ================================

def yaiba2df(session_log, schema: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """session_log から position と attendance の 2 表を構築する。

    schema に基づく簡易型検証結果として、各レコードに is_error 列を付与する。

    Args:
        session_log: YAIBA によりパースされた session_log オブジェクト。
        schema (dict): 位置データと入退室イベントの列・型定義を含むスキーマ辞書。

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 位置データと入退室イベントの DataFrame。

    Raises:
        ValueError: YAIBA ログのパースに失敗した場合、
            または log_entries が存在しない場合。
    """
    try:
        encoder = yaiba.JsonEncoder(options=None)
        data = json.loads(encoder.encode(session_log))
    except Exception as e:
        # YAIBA パースに失敗したら即停止
        raise ValueError(f"YAIBA ログのパースに失敗しました: {e}")

    # log_entries がなければ即停止
    if "log_entries" not in data:
        raise ValueError("YAIBA ログに log_entries が含まれていません。")

    entry = data["log_entries"]

    pos_records = []
    attendance_records = []

    pos_keys = schema["position"]["keys"]
    pos_types = schema["position"]["types"]
    attendance_keys = schema["attendance"]["keys"]
    attendance_types = schema["attendance"]["types"]

    for record in entry:

        type_id = record["type_id"]
        if type_id == "yaiba/player_position":
            L = []
            for key in pos_keys:
                L.append(record[key])
            ret = map(_isinstance_map, L, pos_types)
            is_error = False in ret
            L.append(is_error)
            pos_records.append(L)

        elif type_id in ["vrc/player_join", "vrc/player_left"]:
            L = []
            for key in attendance_keys:
                L.append(record[key])
            ret = map(_isinstance_map, L, attendance_types)
            is_error = False in ret
            L.append(is_error)
            attendance_records.append(L)

    df_pos = pd.DataFrame(pos_records, columns=pos_keys + ["is_error"])
    df_event = pd.DataFrame(attendance_records, columns=attendance_keys + ["is_error"])

    return df_pos, df_event


def GenerateIntermediate(
    df_pos: pd.DataFrame,
    df_event: pd.DataFrame,
    schema: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """位置データとイベントデータを中間形式へ変換する。

    second 列・event_day 列の追加、action の正規化、列名変更、
    schema 順での列整列を行う。

    Args:
        df_pos (pd.DataFrame): 生の位置データ。
        df_event (pd.DataFrame): 生の入退室イベント。
        schema (dict): 中間形式の列順を定義したスキーマ辞書。

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: 中間形式に変換後の位置データと
        入退室イベント。
    """

    # --- position 側 ---

    rename_map = {
        "player_id": "user_id",
        "pseudo_user_name": "user_name",
    }

    if not df_pos.empty and "timestamp" in df_pos.columns:
        df_pos["second"] = pd.to_datetime(df_pos["timestamp"], unit="s")
        df_pos["second"] = df_pos["second"].dt.tz_localize("UTC")
        df_pos["event_day"] = df_pos["second"].dt.tz_convert("Asia/Tokyo").dt.date
        df_pos["second"] = df_pos["second"].dt.tz_localize(None)
        df_pos = df_pos.rename(columns=rename_map)

    # --- attendance 側 ---
    rename_map = {
        "pseudo_user_name": "user_name",
    }
    if not df_event.empty and "timestamp" in df_event.columns:
        df_event["second"] = pd.to_datetime(df_event["timestamp"], unit="s")
        df_event["second"] = df_event["second"].dt.tz_localize("UTC")
        df_event["second"] = df_event["second"].dt.tz_localize(None)
        df_event["action"] = df_event["type_id"].map(_normalize_action)
        df_event = df_event.drop(columns=["type_id"])
        df_event = df_event.rename(columns=rename_map)

    # --- schema 順でカラム整列（pandas 1行方式） ---
    if not df_pos.empty:
        desired = schema["position"]["keys"]
        cols = [c for c in desired if c in df_pos.columns]
        df_pos = df_pos[cols]

    if not df_event.empty:
        desired = schema["attendance"]["keys"]
        cols = [c for c in desired if c in df_event.columns]
        df_event = df_event[cols]

    return df_pos, df_event


def build_area(position: pd.DataFrame) -> Area:
    """位置データから空間範囲を表す Area を作成する。

    location_x、location_y、location_z の最小値と最大値を集計する。
    入力が None または空の場合は、すべて 0.0 の Area を返す。

    Args:
        position (pd.DataFrame): 位置データを格納した DataFrame。

    Returns:
        Area: 位置データから算出した空間範囲。
    """
    if position is None or position.empty:
        return Area(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    x_min, x_max = np.nanmin(position["location_x"]), np.nanmax(position["location_x"])
    y_min, y_max = np.nanmin(position["location_y"]), np.nanmax(position["location_y"])
    z_min, z_max = np.nanmin(position["location_z"]), np.nanmax(position["location_z"])
    return Area(
        float(x_min), float(x_max),
        float(y_min), float(y_max),
        float(z_min), float(z_max)
    )


# ================================
# A工程メイン関数
# ================================
def load(
    log_file: str,
    sec_interval: int = 1,
    anonymize: bool = True,
    base_time: Optional[datetime] = None
) -> LogData:
    """ログファイルを読み込み、解析用の LogData を生成する。

    ログの読み込み、DataFrame 生成、秒粒度推定、中間形式への変換、
    Area 算出を順に行い、LogData にまとめて返す。

    Args:
        log_file (str): 読み込むログファイルのパス。
        sec_interval (int): 秒単位の処理間隔（現状未使用）。
        anonymize (bool): 匿名化の有無（現状未使用）。
        base_time (Optional[datetime]): 基準時刻（現状未使用）。

    Returns:
        LogData: 位置データ、イベントデータ、空間範囲、時間粒度を
        まとめたログデータオブジェクト。

    Raises:
        ValueError: ログ読み込みまたは DataFrame 生成に失敗した場合。
    """

    # --- 専用関数で読み込み＋例外処理 ---
    session_log = load_session_log(log_file)

    # 2表を構築
    df_pos, df_event = yaiba2df(session_log, schema_yaiba)

    # 秒粒度の推定
    time_span = get_time_span(df_pos)
    df_pos, df_event = GenerateIntermediate(df_pos, df_event, schema_intermediate)

    # Areaを算出し、LogDataに格納
    area = build_area(df_pos if not df_pos.empty else None)
    logdata = LogData(
        position=df_pos,
        attendance=df_event,
        area=area,
        time_span=time_span
    )

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
    print("\ntime_span:", time_span)
