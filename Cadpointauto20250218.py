import pandas as pd                     # オープンソース、無料、オフラインで動作
import ezdxf                            # オープンソース、無料、オフラインで動作
import os                               # Python標準ライブラリ（無料、オフライン）
import tkinter as tk                    # Python標準ライブラリ（無料、オフライン）※GUI用
from tkinter import filedialog          # Python標準ライブラリ（無料、オフライン）
import sys                              # Python標準ライブラリ（無料、オフライン）
import math                             # Python標準ライブラリ（無料、オフライン）

# =============================================================================
# 定数・ラベル設定の一元管理（編集しやすいように先頭にまとめています）
# "灯" に関する設定は削除済みです。
# =============================================================================
label_settings = {
    "下": {"type": "circle", "diameter": 0.75},
    "下水": {"type": "circle", "diameter": 0.75},
    "D": {"type": "circle", "diameter": 0.75},
    "d": {"type": "circle", "diameter": 0.75},
    "S": {"type": "circle", "diameter": 0.45},
    "s": {"type": "circle", "diameter": 0.45},
    "F0": {"type": "circle", "diameter": 0.6},
    "f0": {"type": "circle", "diameter": 0.6},
    "SV": {"type": "circle", "diameter": 0.3},
    "sv": {"type": "circle", "diameter": 0.3},
    "w": {"type": "circle", "diameter": 0.3},
    "W": {"type": "circle", "diameter": 0.3},
    "t": {"type": "circle", "diameter": 0.75},
    "T": {"type": "circle", "diameter": 0.75},
    "e": {"type": "circle", "diameter": 0.75},
    "E": {"type": "circle", "diameter": 0.75},

    # 四角形（中央配置）→内部に十字線は描画しない
    "桝": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "マス": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "ms": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "MS": {"type": "rectangle", "size": (0.5, 0.6), "draw_cross": False},
    "F": {"type": "rectangle", "size": (0.4, 0.6), "draw_cross": False},
    "f": {"type": "rectangle", "size": (0.4, 0.6), "draw_cross": False},
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
    "左枡900700": {"type": "rectangle", "size": (0.9, 0.7), "group": "left_masu"},

    # 右側桝（枡）
    "msr": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "rms": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "MSR": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "RMS": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "右桝": {"type": "rectangle", "size": (0.5, 0.6), "group": "right_masu"},
    "右桝900700": {"type": "rectangle", "size": (0.9, 0.7), "group": "right_masu"},
    "右桝700550": {"type": "rectangle", "size": (0.7, 0.55), "group": "right_masu"},
    # メジ（破線C列(OFF)は読まない）
    "メジ": {"type": "line", "linetype": "DASHED"},
    "コメントライン": {"type": "line", "linetype": "DASHED"},

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

    # 灯の半円塗りつぶしはいまいちうまくできないのでただの円にしました
    "灯": {"type": "circle", "diameter": 0.3},
    # 特殊記号（電柱・信号など）→poleタイプ
    "電": {"type": "pole", "radius": 0.15},
    "EP": {"type": "pole", "radius": 0.15},
    "ep": {"type": "pole", "radius": 0.15},
    "電柱": {"type": "pole", "radius": 0.15},
    "信号": {"type": "pole", "radius": 0.15},
    "信": {"type": "pole", "radius": 0.15}
}

# カラーパレット（DXFの色番号） - すべて無料、オフラインで動作
colors = [1, 2, 3, 4, 6]  # 赤, 黄, 緑, シアン, マゼンタ

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls *.xlsm *.xlsb")]
    )
    return file_path

def safe_float(value, default=0.0):
    try:
        float_value = float(value)
        return float_value if not math.isnan(float_value) and float_value != 0 else default
    except (ValueError, TypeError):
        return default

# 半円塗りつぶし（HATCH方式）：円の上半分または下半分を塗りつぶす
def add_half_filled_circle(msp, x, y, radius, fill='top'):
    import math
    # 外周の円を描画（輪郭用）
    msp.add_circle(center=(x, y), radius=radius, dxfattribs={'layer': 'WHITE_LINES'})
    # ハッチの境界パスを作成
    n = 40  # 分割数
    if fill == 'top':
        start_angle = 0
        end_angle = math.pi
        chord = [(x - radius, y), (x + radius, y)]
    else:
        start_angle = math.pi
        end_angle = 2 * math.pi
        chord = [(x + radius, y), (x - radius, y)]
    arc_points = [
        (x + radius * math.cos(start_angle + (end_angle - start_angle) * i / n),
         y + radius * math.sin(start_angle + (end_angle - start_angle) * i / n))
        for i in range(n+1)
    ]
    boundary_points = arc_points + chord
    hatch = msp.add_hatch(color=7, dxfattribs={'layer': 'WHITE_LINES'})
    hatch.paths.add_polyline_path(boundary_points, is_closed=True)

def add_cross_in_rectangle(msp, x, y, width, height):
    """四角形内部に十字線を描く"""
    half_width, half_height = width / 2, height / 2
    msp.add_line((x - half_width, y), (x + half_width, y), dxfattribs={'layer': 'WHITE_LINES'})
    msp.add_line((x, y - half_height), (x, y + half_height), dxfattribs={'layer': 'WHITE_LINES'})

def add_rectangle(msp, x, y, width, height, align='center'):
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
    msp.add_lwpolyline(points, dxfattribs={'layer': 'WHITE_LINES'})
    return center_x, y

def add_pole_symbol(msp, x, y, radius, align='left'):
    """電柱などのpoleシンボルを描く"""
    if align == 'left':
        center_x = x - radius
    elif align == 'right':
        center_x = x + radius
    else:
        center_x = x
    msp.add_circle((center_x, y), radius=radius, dxfattribs={'layer': 'WHITE_LINES'})
    msp.add_line((center_x, y + radius), (center_x, y + radius + 0.3), dxfattribs={'layer': 'WHITE_LINES'})
    msp.add_line((center_x, y - radius), (center_x, y - radius - 0.3), dxfattribs={'layer': 'WHITE_LINES'})
    return center_x

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
    doc.styles.new('JAPANESE', dxfattribs={'font': 'MS Gothic'})
    print("日本語フォントスタイルを作成しました")
    doc.layers.new(name='COLORED_LINES', dxfattribs={'color': 7})
    doc.layers.new(name='FOUR_MAIN_LINES', dxfattribs={'color': 7})
    doc.layers.new(name='WHITE_LINES', dxfattribs={'color': 7})
    doc.layers.new(name='WHITE_TEXT', dxfattribs={'color': 7})
    doc.linetypes.new('DASHED', dxfattribs={'description': 'Dashed line', 'pattern': [0.5, -0.25]})
    doc.linetypes.new('DASHDOT', dxfattribs={'description': 'Dash-dot line', 'pattern': [0.5, -0.25, 0.0, -0.25]})

    def draw_lines(start_x, h_value, g_value, i_value, f_value=None, j_value=None):
        second_line_x = start_x + h_value
        third_line_x  = start_x + g_value
        fourth_line_x = second_line_x - i_value
        line_end_y = start_y + 200
        msp.add_line((start_x, start_y), (start_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
        msp.add_line((second_line_x, start_y), (second_line_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
        msp.add_line((third_line_x, start_y), (third_line_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
        msp.add_line((fourth_line_x, start_y), (fourth_line_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
        parallel_f_x = None
        parallel_j_x = None
        if f_value is not None:
            parallel_f_x = start_x - f_value
            msp.add_line((parallel_f_x, start_y), (parallel_f_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
            print(f"F列の平行オフセットを描画: ({parallel_f_x}, {start_y}) -> ({parallel_f_x}, {line_end_y})")
        if j_value is not None:
            parallel_j_x = second_line_x + j_value
            msp.add_line((parallel_j_x, start_y), (parallel_j_x, line_end_y), dxfattribs={'layer': 'FOUR_MAIN_LINES'})
            print(f"J列の平行オフセットを描画: ({parallel_j_x}, {start_y}) -> ({parallel_j_x}, {line_end_y})")
        return second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x

    try:
        excel_data = pd.read_excel(file_path, usecols='F:J', nrows=4)
        f_value = safe_float(excel_data.iloc[1, 0]) if pd.notna(excel_data.iloc[1, 0]) else None
        g_value = safe_float(excel_data.iloc[1, 1], default=0.0)
        h_value = safe_float(excel_data.iloc[1, 2], default=10.0)
        i_value = safe_float(excel_data.iloc[1, 3], default=0.0)
        j_value = safe_float(excel_data.iloc[1, 4]) if pd.notna(excel_data.iloc[1, 4]) else None
        sidewalk_l_value = 1.0 if f_value is not None else 0.0
        sidewalk_r_value = 1.0 if j_value is not None else 0.0
    except ValueError:
        print("警告: F, G, H, I, J列が見つかりません。デフォルト値を使用します。")
        f_value, g_value, h_value, i_value, j_value = None, 0.0, 10.0, 0.0, None
        sidewalk_l_value, sidewalk_r_value = 0.0, 0.0

    second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x = draw_lines(
        start_x, h_value, g_value, i_value, f_value, j_value
    )

    msp.add_text(
        f"歩道(L)={sidewalk_l_value:.2f} 側溝(L)={i_value:.2f} 幅員={h_value:.2f} 側溝(R)={g_value:.2f} 歩道(R)={sidewalk_r_value:.2f}",
        dxfattribs={
            'height': 0.3,
            'insert': (start_x - 1, start_y - 0.5),
            'layer': 'WHITE_TEXT',
            'style': 'JAPANESE'
        }
    )
    print("起点の位置に値を表示しました")

    filename = os.path.basename(file_path)
    msp.add_text(filename, dxfattribs={
        'height': 0.3,
        'insert': (start_x - 1, start_y - 1),
        'layer': 'WHITE_TEXT',
        'style': 'JAPANESE'
    })
    print(f"ファイル名を表示: {filename}")

    def add_colored_line_and_labels(y, x, label, b_value, color_index):
        color = colors[color_index % len(colors)]
        msp.add_line((start_x, y), (start_x, start_y), dxfattribs={'color': color, 'layer': 'COLORED_LINES'})
        msp.add_text(f"{b_value:.2f}", dxfattribs={
            'height': 0.3,
            'color': color,
            'layer': 'COLORED_LINES',
            'insert': (start_x - 1, y),
            'style': 'JAPANESE'
        })
        skip_horizontal = {
            "左境", "右境", "LS", "RS", "ls", "rs", "sl", "sr", "SL", "SR",
            "舗装境", "新舗装", "切下げ", "切下", "メジ"
        }
        if label in label_settings and label_settings[label].get("type") == "pole":
            skip = False
        else:
            skip = label in skip_horizontal
        if not skip:
            msp.add_line((start_x, y), (x, y), dxfattribs={'color': color, 'layer': 'COLORED_LINES'})
            msp.add_text(f"{x - start_x:.2f}", dxfattribs={
                'height': 0.3,
                'color': color,
                'layer': 'COLORED_LINES',
                'insert': (x, y + 0.5),
                'style': 'JAPANESE'
            })

    def add_rectangle(msp, x, y, width, height, align='center'):
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
        msp.add_lwpolyline(points, dxfattribs={'layer': 'WHITE_LINES'})
        return center_x, y

    def add_cross_in_rectangle(msp, x, y, width, height):
        half_width, half_height = width / 2, height / 2
        msp.add_line((x - half_width, y), (x + half_width, y), dxfattribs={'layer': 'WHITE_LINES'})
        msp.add_line((x, y - half_height), (x, y + half_height), dxfattribs={'layer': 'WHITE_LINES'})

    def add_half_filled_circle(msp, x, y, radius, fill='top'):
        import math
        msp.add_circle(center=(x, y), radius=radius, dxfattribs={'layer': 'WHITE_LINES'})
        n = 40
        if fill == 'top':
            start_angle = 0
            end_angle = math.pi
            chord = [(x - radius, y), (x + radius, y)]
        else:
            start_angle = math.pi
            end_angle = 2 * math.pi
            chord = [(x + radius, y), (x - radius, y)]
        arc_points = [
            (x + radius * math.cos(start_angle + (end_angle - start_angle) * i / n),
             y + radius * math.sin(start_angle + (end_angle - start_angle) * i / n))
            for i in range(n+1)
        ]
        boundary_points = arc_points + chord
        hatch = msp.add_hatch(color=7, dxfattribs={'layer': 'WHITE_LINES'})
        hatch.paths.add_polyline_path(boundary_points, is_closed=True)

    def add_pole_symbol(msp, x, y, radius, align='left'):
        if align == 'left':
            center_x = x - radius
        elif align == 'right':
            center_x = x + radius
        else:
            center_x = x
        msp.add_circle((center_x, y), radius=radius, dxfattribs={'layer': 'WHITE_LINES'})
        msp.add_line((center_x, y + radius), (center_x, y + radius + 0.3), dxfattribs={'layer': 'WHITE_LINES'})
        msp.add_line((center_x, y - radius), (center_x, y - radius - 0.3), dxfattribs={'layer': 'WHITE_LINES'})
        return center_x

    row_counter = 2

    for index, row in df.iterrows():
        try:
            label = str(row.iloc[0]).strip()
            if pd.isna(label) or label == "":
                print(f"A列が空白のため、行 {index + 2} で処理を終了します。")
                break

            if label == "***":
                start_x += 30
                start_y = 0
                row_counter += 1
                if row_counter >= 4:
                    row_counter = 4
                f_value = safe_float(excel_data.iloc[row_counter - 1, 0]) if pd.notna(excel_data.iloc[row_counter - 1, 0]) else None
                g_value = safe_float(excel_data.iloc[row_counter - 1, 1], default=g_value)
                h_value = safe_float(excel_data.iloc[row_counter - 1, 2], default=h_value)
                i_value = safe_float(excel_data.iloc[row_counter - 1, 3], default=i_value)
                j_value = safe_float(excel_data.iloc[row_counter - 1, 4]) if pd.notna(excel_data.iloc[row_counter - 1, 4]) else None
                sidewalk_l_value = 1.0 if f_value is not None else 0.0
                sidewalk_r_value = 1.0 if j_value is not None else 0.0
                second_line_x, third_line_x, fourth_line_x, parallel_f_x, parallel_j_x = draw_lines(
                    start_x, h_value, g_value, i_value, f_value, j_value
                )
                msp.add_text(
                    f"歩道(L)={sidewalk_l_value:.2f} 側溝(L)={i_value:.2f} 幅員={h_value:.2f} 側溝(R)={g_value:.2f} 歩道(R)={sidewalk_r_value:.2f}",
                    dxfattribs={'height': 0.3, 'insert': (start_x - 1, start_y - 0.5),
                                'layer': 'WHITE_TEXT', 'style': 'JAPANESE'}
                )
                print(f"新しい起点を作成しました: {index + 2}行目")
                continue

            b_value = safe_float(row.iloc[1])
            y = start_y + b_value

            if label in {"msr", "rms", "MSR", "RMS"}:
                x = start_x + h_value
                align = 'right'
            elif label in {"msl", "lms", "MSL", "LMS"}:
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

            add_colored_line_and_labels(y, x, label, b_value, index)
            text_x = x

            if label in label_settings:
                setting = label_settings[label]
                t = setting.get("type")
                if t == "rectangle":
                    group = setting.get("group")
                    if group == "right_masu":
                        x = start_x + h_value
                        align = 'right'
                    elif group == "left_masu":
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
                    if group in {"right_masu", "left_masu"}:
                        center_x, center_y = add_rectangle(msp, x, y, width, height, align=align)
                    else:
                        center_x, center_y = add_rectangle(msp, x, y, width, height, align='center')
                        if setting.get("draw_cross", False):
                            add_cross_in_rectangle(msp, center_x, center_y, width, height)
                    text_x = center_x
                    print(f"四角形（{label}）を追加: ({x}, {y}), サイズ: ({width}, {height}), 配置: {align}")
                elif t == "line":
                    linetype = setting["linetype"]
                    group = setting.get("group")
                    if group == "left_boundary":
                        boundary_x = parallel_f_x if parallel_f_x is not None else start_x
                        msp.add_line((boundary_x, y), (boundary_x - 6, y),
                                     dxfattribs={'layer': 'WHITE_LINES', 'linetype': linetype})
                        text_x = boundary_x
                    elif group == "right_boundary":
                        boundary_x = parallel_j_x if parallel_j_x is not None else second_line_x
                        msp.add_line((boundary_x, y), (boundary_x + 6, y),
                                     dxfattribs={'layer': 'WHITE_LINES', 'linetype': linetype})
                        text_x = boundary_x - 1.5
                    else:
                        msp.add_line((start_x, y), (second_line_x, y),
                                     dxfattribs={'layer': 'WHITE_LINES', 'linetype': linetype})
                        text_x = start_x + 0.2
                    print(f"線（{label}）を追加: y={y}, linetype={linetype}")
                elif t == "circle":
                    diameter = setting["diameter"]
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
                    msp.add_circle((x, y), radius=diameter/2, dxfattribs={'layer': 'WHITE_LINES'})
                    text_x = x
                    print(f"円（{label}）を追加: ({x}, {y}), 半径: {diameter/2}")
                elif t == "pole":
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
                    center_x = add_pole_symbol(msp, x, y, radius, align)
                    text_x = center_x
                    print(f"電柱記号（{label}）を追加: ({x}, {y}), 半径: {radius}, 配置: {align}")
                # "lamp" タイプは削除済み
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
                    msp.add_circle((x, y), radius=diameter/2, dxfattribs={'layer': 'WHITE_LINES'})
                    text_x = x
                    print(f"デフォルトの円を追加: ({x}, {y}), 半径: {diameter/2}")
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
                msp.add_circle((x, y), radius=diameter/2, dxfattribs={'layer': 'WHITE_LINES'})
                text_x = x
                print(f"デフォルトの円を追加: ({x}, {y}), 半径: {diameter/2}")

            comment = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            if comment:
                msp.add_text(f"{label} {comment}", dxfattribs={
                    'height': 0.45,
                    'insert': (text_x, y),
                    'layer': 'WHITE_TEXT',
                    'style': 'JAPANESE'
                })
                print(f"テキストを追加: '{label} {comment}' at ({text_x}, {y})")
            else:
                msp.add_text(label, dxfattribs={
                    'height': 0.45,
                    'insert': (text_x, y),
                    'layer': 'WHITE_TEXT',
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
    print("DXF file has been created successfully.")
    print("Please check the file to ensure all elements are displayed correctly.")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
