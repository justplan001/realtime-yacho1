import pandas as pd
import ezdxf
import os
import tkinter as tk
from tkinter import filedialog
import sys
import math

# =============================================================================
# 定数・ラベル・レイヤー設定の一元管理（編集しやすいように先頭にまとめています）
# =============================================================================
layer_names = {
    "colored_lines": "COLORED_LINES",      # 測量のラインや数値
    "main_line_1": "1MAIN_LINES",           # H列、F列、J列で描く縦線
    "main_line_2": "2MAIN_LINES",           # G列とI列で描く縦線
    "romen":       "4Romen",                # 円（直径指定）・四角形（中央配置）→内部に十字線の有無で判定
    "sen":         "3Sen",                  # 左右桝、メジ、境界線（図形部分）
    "sen_mozi":    "3SenMozi",              # 3Senに付属する文字
    "other":       "5Other"                 # 未定義の名称
}

label_settings = {
    # 円（直径指定）　※ラベル設定がある場合はExcelの値は無視して、こちらのdiameterを使う
    "下": {"type": "circle", "diameter": 0.75},
    "下水": {"type": "circle", "diameter": 0.75},
    "D": {"type": "circle", "diameter": 0.75},
    "S": {"type": "circle", "diameter": 0.4},
    "SV": {"type": "circle", "diameter": 0.3},
    "sv": {"type": "circle", "diameter": 0.3},
    "w": {"type": "circle", "diameter": 0.3},
    "W": {"type": "circle", "diameter": 0.3},

    # 四角形（中央配置）→内部に十字線は描画しない
    "桝": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "マス": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "ms": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "MS": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "F": {"type": "rectangle", "size": (0.4, 0.6), "draw_cross": False},
    "消": {"type": "rectangle", "size": (0.4, 0.6), "draw_cross": False},

    # 十字の四角形（中央配置）→内部に十字線を描画する
    "市": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "民": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "し": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "み": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "みん": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "si": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "min": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "SI": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "MIN": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "杭": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},
    "都市再生": {"type": "rectangle", "size": (0.4, 0.4), "draw_cross": True},

    # 左側桝（枡）
    "msl": {"type": "rectangle", "size": (0.5, 0.6), "group": "left_masu"},
    "lms": {"type": "rectangle", "size": (0.5, 0.6), "group": "left_masu"},
    "MSL": {"type": "rectangle", "size": (0.5, 0.6), "group": "left_masu"},
    "LMS": {"type": "rectangle", "size": (0.5, 0.6), "group": "left_masu"},
    "左枡": {"type": "rectangle", "size": (0.5, 0.6), "group": "left_masu"},

    # 右側桝（枡）
    "msr": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "rms": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "MSR": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "RMS": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "右桝": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},

    # メジ（破線C列(OFF)は読まない）
    "メジ": {"type": "line", "linetype": "DASHED"},

    # 境界線（左側）
    "左境": {"type": "line", "linetype": "DASHDOT", "group": "left_boundary"},
    "LS":   {"type": "line", "linetype": "DASHDOT", "group": "left_boundary"},
    "ls":   {"type": "line", "linetype": "DASHDOT", "group": "left_boundary"},
    "sl":   {"type": "line", "linetype": "DASHDOT", "group": "left_boundary"},
    "SL":   {"type": "line", "linetype": "DASHDOT", "group": "left_boundary"},

    # 境界線（右側）
    "右境": {"type": "line", "linetype": "DASHDOT", "group": "right_boundary"},
    "RS":   {"type": "line", "linetype": "DASHDOT", "group": "right_boundary"},
    "rs":   {"type": "line", "linetype": "DASHDOT", "group": "right_boundary"},
    "sr":   {"type": "line", "linetype": "DASHDOT", "group": "right_boundary"},
    "SR":   {"type": "line", "linetype": "DASHDOT", "group": "right_boundary"},

    # 特殊記号（電柱・信号など）→poleタイプ
    "電": {"type": "pole", "radius": 0.15},
    "EP": {"type": "pole", "radius": 0.15},
    "電柱": {"type": "pole", "radius": 0.15},
    "信号": {"type": "pole", "radius": 0.15},
    "信": {"type": "pole", "radius": 0.15}
}

# カラーパレット（DXFの色番号）
colors = [1, 2, 3, 4, 6]  # 赤, 黄, 緑, シアン, マゼンタ

# =============================================================================
# ユーティリティ関数
# =============================================================================
def safe_float(value, default=0.0):
    try:
        float_value = float(value)
        return float_value if not math.isnan(float_value) and float_value != 0 else default
    except (ValueError, TypeError):
        return default

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls *.xlsm *.xlsb")]
    )
    return file_path

# =============================================================================
# 描画用関数（レイヤー指定を追加）
# =============================================================================
def add_rectangle(msp, x, y, width, height, align='center', layer="WHITE_LINES"):
    if align == 'left':
        left = x
        center_x = x + width / 2
    elif align == 'right':
        left = x - width
        center_x = x - width / 2
    else:
        left = x - width / 2
        center_x = x
    top = y + height / 2
    bottom = y - height / 2
    points = [(left, bottom), (left + width, bottom), (left + width, top), (left, top), (left, bottom)]
    msp.add_lwpolyline(points, dxfattribs={'layer': layer})
    return center_x, y

def add_cross_in_rectangle(x, y, width, height, layer="WHITE_LINES"):
    half_width, half_height = width / 2, height / 2
    msp.add_line((x - half_width, y), (x + half_width, y), dxfattribs={'layer': layer})
    msp.add_line((x, y - half_height), (x, y + half_height), dxfattribs={'layer': layer})

def add_pole_symbol(msp, x, y, radius, align='left', layer="WHITE_LINES"):
    if align == 'left':
        center_x = x - radius
    elif align == 'right':
        center_x = x + radius
    else:
        center_x = x
    msp.add_circle((center_x, y), radius=radius, dxfattribs={'layer': layer})
    msp.add_line((center_x, y + radius), (center_x, y + radius + 0.3), dxfattribs={'layer': layer})
    msp.add_line((center_x, y - radius), (center_x, y - radius - 0.3), dxfattribs={'layer': layer})
    return center_x

# =============================================================================
# レイヤーグループ分け用のセット
# =============================================================================
four_romen_labels = {"下", "下水", "D", "S", "SV", "sv", "w", "W",
                      "桝", "マス", "ms", "MS", "F", "消",
                      "市", "民", "し", "み", "みん", "si", "min", "SI", "MIN", "杭", "都市再生"}
three_sen_labels = {"msl", "lms", "MSL", "LMS", "左枡",
                      "msr", "rms", "MSR", "RMS", "右桝",
                      "メジ", "左境", "LS", "ls", "sl", "SL", "右境", "RS", "rs", "sr", "SR"}

def get_layers(label):
    """
    ラベルに応じて図形描画レイヤー（shape_layer）とテキスト描画レイヤー（text_layer）を返す。
    3Senグループの場合、文字は sen_mozi レイヤーに割り当てる。
    """
    if label in four_romen_labels:
        return layer_names["romen"], layer_names["romen"]
    elif label in three_sen_labels:
        return layer_names["sen"], layer_names["sen_mozi"]
    else:
        return layer_names["other"], layer_names["other"]

# =============================================================================
# DXFファイル生成
# =============================================================================
# グローバル起点
start_x, start_y = 0, 0

try:
    file_path = select_file()
    if not file_path:
        print("No file selected. Exiting...")
        sys.exit()

    print("Excelファイル読み込み開始")
    df = pd.read_excel(file_path, nrows=10000)
    print(f"読み込んだ行数: {len(df)}")

    print("DXF生成開始")
    doc = ezdxf.new(dxfversion='R2000')
    msp = doc.modelspace()

    # 日本語フォントスタイルの作成
    doc.styles.new('JAPANESE', dxfattribs={'font': 'MS Gothic'})
    print("日本語フォントスタイルを作成しました")

    # 新しいレイヤーの作成（layer_namesの設定に基づく）
    doc.layers.new(name=layer_names["colored_lines"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["main_line_1"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["main_line_2"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["romen"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["sen"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["sen_mozi"], dxfattribs={'color': 7})
    doc.layers.new(name=layer_names["other"], dxfattribs={'color': 7})

    # ラインタイプの作成
    doc.linetypes.new('DASHED', dxfattribs={'description': 'Dashed line', 'pattern': [0.5, -0.25]})
    doc.linetypes.new('DASHDOT', dxfattribs={'description': 'Dash-dot line', 'pattern': [0.5, -0.25, 0.0, -0.25]})

    # -----------------------------------------------------------------------------
    # 縦線描画用関数（レイヤー指定を利用）
    # -----------------------------------------------------------------------------
    def draw_lines(start_x, h_value, g_value, i_value, f_value=None, j_value=None):
        second_line_x = start_x + h_value
        third_line_x  = start_x + g_value
        fourth_line_x = second_line_x - i_value

        line_end_y = start_y + 100
        # H列由来の線（1MAIN_LINES）
        msp.add_line((start_x, start_y), (start_x, line_end_y),
                     dxfattribs={'layer': layer_names["main_line_1"]})
        msp.add_line((second_line_x, start_y), (second_line_x, line_end_y),
                     dxfattribs={'layer': layer_names["main_line_1"]})
        # G列・I列由来の線（2MAIN_LINES）
        msp.add_line((third_line_x, start_y), (third_line_x, line_end_y),
                     dxfattribs={'layer': layer_names["main_line_2"]})
        msp.add_line((fourth_line_x, start_y), (fourth_line_x, line_end_y),
                     dxfattribs={'layer': layer_names["main_line_2"]})

        # F列・J列のオフセット線（1MAIN_LINES）
        parallel_f_x = None
        parallel_j_x = None
        if f_value is not None:
            parallel_f_x = start_x - f_value
            msp.add_line((parallel_f_x, start_y), (parallel_f_x, line_end_y),
                         dxfattribs={'layer': layer_names["main_line_1"]})
            print(f"F列の平行オフセットを描画: ({parallel_f_x}, {start_y}) -> ({parallel_f_x}, {line_end_y})")
        if j_value is not None:
            parallel_j_x = second_line_x + j_value
            msp.add_line((parallel_j_x, start_y), (parallel_j_x, line_end_y),
                         dxfattribs={'layer': layer_names["main_line_1"]})
            print(f"J列の平行オフセットを描画: ({parallel_j_x}, {start_y}) -> ({parallel_j_x}, {line_end_y})")
        return second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x

    # 初期設定値（Excelの2行目のF～J列）を取得
    try:
        excel_data = pd.read_excel(file_path, usecols='F:J', nrows=10000)
        # ※ここでは複数行のデータが使えるように nrows を 10000 に変更しています
        f_value = safe_float(excel_data.iloc[1, 0]) if pd.notna(excel_data.iloc[1, 0]) else None
        g_value = safe_float(excel_data.iloc[1, 1], default=0.0)
        h_value = safe_float(excel_data.iloc[1, 2], default=10.0)
        i_value = safe_float(excel_data.iloc[1, 3], default=0.0)
        j_value = safe_float(excel_data.iloc[1, 4]) if pd.notna(excel_data.iloc[1, 4]) else None
    except ValueError:
        print("警告: F, G, H, I, J列が見つかりません。デフォルト値を使用します。")
        f_value, g_value, h_value, i_value, j_value = None, 0.0, 10.0, 0.0, None

    second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x = draw_lines(start_x, h_value, g_value, i_value, f_value, j_value)

    # -----------------------------
    # COLORED_LINES レイヤーの起点表示
    # -----------------------------
    init_value = safe_float(df.iloc[0, 1])
    init_y = start_y + init_value
    color = colors[0]
    msp.add_line((start_x, init_y), (start_x, start_y), dxfattribs={
        'color': color, 
        'layer': layer_names["colored_lines"]
    })
    msp.add_text(f"{init_value:.2f}", dxfattribs={
        'height': 0.3,
        'color': color,
        'layer': layer_names["colored_lines"],
        'insert': (start_x - 1, init_y),
        'style': 'JAPANESE'
    })
    print("起点の値をCOLORED_LINESレイヤーに表示しました")

    # 起点情報として、描画に使用した値をそのまま表示
    # F列の値を歩道(L)、J列の値を歩道(R)として表示する
    msp.add_text(
        f"歩道(L)={f_value if f_value is not None else 0:.2f} 側溝(L)={i_value:.2f} 幅員={h_value:.2f} 側溝(R)={g_value:.2f} 歩道(R)={j_value if j_value is not None else 0:.2f}",
        dxfattribs={
            'height': 0.3,
            'insert': (start_x - 1, start_y - 0.5),
            'layer': layer_names["colored_lines"],
            'style': 'JAPANESE'
        }
    )
    print("起点情報（描画に使用した値）をCOLORED_LINESレイヤーに表示しました")

    filename = os.path.basename(file_path)
    msp.add_text(filename, dxfattribs={
        'height': 0.3,
        'insert': (start_x - 1, start_y - 1),
        'layer': layer_names["colored_lines"],
        'style': 'JAPANESE'
    })
    print(f"ファイル名を表示: {filename}")

    # =============================================================================
    # メイン描画処理（Excelの各行を順次処理）
    # =============================================================================
    # row_counterは、***を検出するたびに次の行を使うためにインクリメントする
    row_counter = 2  # Excel上の2行目から開始

    for index, row in df.iterrows():
        try:
            label = str(row.iloc[0]).strip()
            if pd.isna(label) or label == "":
                print(f"A列が空白のため、行 {index + 2} で処理を終了します。")
                break

            # ***の場合は、新しい起点を設定し、F～J列の次の行の値を使用する
            if label == "***":
                start_x += 30
                start_y = 0
                row_counter += 1  # ここで単純にインクリメント
                # Excelの行数が足りなければ、エラーまたは既存の値を使うかは検討の余地あり
                f_value = safe_float(excel_data.iloc[row_counter - 1, 0]) if pd.notna(excel_data.iloc[row_counter - 1, 0]) else None
                g_value = safe_float(excel_data.iloc[row_counter - 1, 1], default=g_value)
                h_value = safe_float(excel_data.iloc[row_counter - 1, 2], default=h_value)
                i_value = safe_float(excel_data.iloc[row_counter - 1, 3], default=i_value)
                j_value = safe_float(excel_data.iloc[row_counter - 1, 4]) if pd.notna(excel_data.iloc[row_counter - 1, 4]) else None
                second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x = draw_lines(start_x, h_value, g_value, i_value, f_value, j_value)
                msp.add_text(
                    f"歩道(L)={f_value if f_value is not None else 0:.2f} 側溝(L)={i_value:.2f} 幅員={h_value:.2f} 側溝(R)={g_value:.2f} 歩道(R)={j_value if j_value is not None else 0:.2f}",
                    dxfattribs={
                        'height': 0.3, 
                        'insert': (start_x - 1, start_y - 0.5),
                        'layer': layer_names["colored_lines"],
                        'style': 'JAPANESE'
                    }
                )
                print(f"新しい起点を作成しました: {index + 2}行目 (Excel行: {row_counter + 1})")
                continue

            # COLORED_LINES 用の値は元々B列（インデックス1）の値を使用
            b_value = safe_float(row.iloc[1])
            # 垂直方向の位置：起点から b_value 分だけ下がる
            y = start_y + b_value
            color = colors[index % len(colors)]
            # 最初の行は既に起点表示済みなので、重複しないようにスキップ
            if index != 0:
                msp.add_line((start_x, start_y), (start_x, y), dxfattribs={
                    'color': color, 
                    'layer': layer_names["colored_lines"]
                })
                msp.add_text(f"{(y - start_y):.2f}", dxfattribs={
                    'height': 0.3,
                    'color': color,
                    'layer': layer_names["colored_lines"],
                    'insert': (start_x - 3, y),
                    'style': 'JAPANESE'
                })

            # オブジェクト描画時の x 座標は元々C列（インデックス2）から取得
            x_value = row.iloc[2]
            if pd.isna(x_value) or x_value == "":
                x = start_x + h_value
                align = 'right'
            else:
                x_value = safe_float(x_value)
                if x_value < 0:
                    x = start_x + h_value + x_value
                    align = 'right'
                else:
                    x = start_x + x_value
                    align = 'left'
            
            # 水平線（起点から x まで）
            msp.add_line((start_x, y), (x, y), dxfattribs={
                'color': color, 
                'layer': layer_names["colored_lines"]
            })
            msp.add_text(f"{(x - start_x):.2f}", dxfattribs={
                'height': 0.3,
                'color': color,
                'layer': layer_names["colored_lines"],
                'insert': (x, y + 0.5),
                'style': 'JAPANESE'
            })

            # 各オブジェクトの描画
            shape_layer, text_layer = get_layers(label)

            if label in label_settings:
                setting = label_settings[label]
                if setting["type"] == "rectangle":
                    if setting.get("group") == "right_masu":
                        x = start_x + h_value
                        align = 'right'
                    elif setting.get("group") == "left_masu":
                        x = start_x
                        align = 'left'
                    else:
                        x_value = row.iloc[2]
                        if pd.isna(x_value) or x_value == "":
                            x = start_x + h_value
                            align = 'right'
                        else:
                            x_value = safe_float(x_value)
                            if x_value < 0:
                                x = start_x + h_value + x_value
                                align = 'right'
                            else:
                                x = start_x + x_value
                                align = 'left'
                    width, height = setting["size"]
                    if setting.get("group") in {"right_masu", "left_masu"}:
                        center_x, center_y = add_rectangle(msp, x, y, width, height, align=align, layer=shape_layer)
                    else:
                        center_x, center_y = add_rectangle(msp, x, y, width, height, align='center', layer=shape_layer)
                        if setting.get("draw_cross", False):
                            add_cross_in_rectangle(center_x, center_y, width, height, layer=shape_layer)
                    text_x = center_x
                    print(f"四角形（{label}）を追加: ({x}, {y}), サイズ: ({width}, {height}), 配置: {align}")
                elif setting["type"] == "circle":
                    # ここでは、Excelの値ではなく、ラベル設定のdiameterを優先して使用
                    diameter = setting.get("diameter", safe_float(row.iloc[3], default=0.1))
                    x_value = row.iloc[2]
                    if pd.isna(x_value) or x_value == "":
                        x = start_x + h_value
                        align = 'right'
                    else:
                        x_value = safe_float(x_value)
                        if x_value < 0:
                            x = start_x + h_value + x_value
                            align = 'right'
                        else:
                            x = start_x + x_value
                            align = 'left'
                    msp.add_circle((x, y), radius=diameter / 2, dxfattribs={'layer': shape_layer})
                    text_x = x
                    print(f"円（{label}）を追加: ({x}, {y}), 半径: {diameter/2}")
                elif setting["type"] == "line":
                    linetype = setting["linetype"]
                    if setting.get("group") == "left_boundary":
                        boundary_x = parallel_f_x if parallel_f_x is not None else start_x
                        msp.add_line((boundary_x, y), (boundary_x - 3, y),
                                     dxfattribs={'layer': shape_layer, 'linetype': linetype})
                        text_x = boundary_x
                    elif setting.get("group") == "right_boundary":
                        boundary_x = parallel_j_x if parallel_j_x is not None else second_line_x
                        msp.add_line((boundary_x, y), (boundary_x + 3, y),
                                     dxfattribs={'layer': shape_layer, 'linetype': linetype})
                        text_x = boundary_x - 1.5
                    else:
                        msp.add_line((start_x, y), (second_line_x, y),
                                     dxfattribs={'layer': shape_layer, 'linetype': linetype})
                        text_x = start_x + 0.2
                    print(f"線（{label}）を追加: y={y}, linetype={linetype}")
                elif setting["type"] == "pole":
                    radius = setting["radius"]
                    x_value = row.iloc[2]
                    if pd.isna(x_value) or x_value == "":
                        x = start_x + h_value
                        align = 'right'
                    else:
                        x_value = safe_float(x_value)
                        if x_value < 0:
                            x = start_x + h_value + x_value
                            align = 'right'
                        else:
                            x = start_x + x_value
                            align = 'left'
                    center_x = add_pole_symbol(msp, x, y, radius, align, layer=shape_layer)
                    text_x = center_x
                    print(f"電柱記号（{label}）を追加: ({x}, {y}), 半径: {radius}, 配置: {align}")
                else:
                    x_value = row.iloc[2]
                    if pd.isna(x_value) or x_value == "":
                        x = start_x + h_value
                        align = 'right'
                    else:
                        x_value = safe_float(x_value)
                        if x_value < 0:
                            x = start_x + h_value + x_value
                            align = 'right'
                        else:
                            x = start_x + x_value
                            align = 'left'
                    diameter = safe_float(row.iloc[3], default=0.1)
                    msp.add_circle((x, y), radius=diameter / 2, dxfattribs={'layer': shape_layer})
                    text_x = x
                    print(f"デフォルトの円を追加: ({x}, {y}), 半径: {diameter/2}")
            else:
                shape_layer, text_layer = layer_names["other"], layer_names["other"]
                x_value = row.iloc[2]
                if pd.isna(x_value) or x_value == "":
                    x = start_x + h_value
                    align = 'right'
                else:
                    x_value = safe_float(x_value)
                    if x_value < 0:
                        x = start_x + h_value + x_value
                        align = 'right'
                    else:
                        x = start_x + x_value
                        align = 'left'
                diameter = safe_float(row.iloc[3], default=0.1)
                msp.add_circle((x, y), radius=diameter / 2, dxfattribs={'layer': shape_layer})
                text_x = x
                print(f"デフォルトの円（{label}）を追加: ({x}, {y}), 半径: {diameter/2}")

            # テキスト描画：コメントは元々E列（インデックス4）の値を使用
            comment = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            if comment:
                msp.add_text(f"{label} {comment}", dxfattribs={
                    'height': 0.45,
                    'insert': (text_x, y),
                    'layer': text_layer,
                    'style': 'JAPANESE'
                })
                print(f"テキストを追加: '{label} {comment}' at ({text_x}, {y})")
            else:
                msp.add_text(label, dxfattribs={
                    'height': 0.45,
                    'insert': (text_x, y),
                    'layer': text_layer,
                    'style': 'JAPANESE'
                })
                print(f"テキストを追加: '{label}' at ({text_x}, {y})")
        except Exception as e:
            print(f"警告: 行 {index + 2} の処理中にエラーが発生しました: {e}")

    print(f"生成されたエンティティの数: {len(msp)}")

    print("\n=== 文字による指定リスト ===")
    print("ラベル設定:")
    for key, setting in label_settings.items():
        print(f"  {key}: {setting}")

    output_filename = os.path.splitext(os.path.basename(file_path))[0] + '.dxf'
    output_path = os.path.join(os.path.dirname(file_path), output_filename)

    print("\nDXFファイル保存開始")
    doc.saveas(output_path)
    print("DXFファイル保存完了")

    file_size = os.path.getsize(output_path)
    print(f"生成されたDXFファイルのサイズ: {file_size} bytes")
    print(f"DXF file saved to: {output_path}")
    print("DXF file has been created successfully.\nPlease check the file to ensure all elements are displayed correctly.")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
