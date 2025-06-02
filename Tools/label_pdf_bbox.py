# --- 前置：同原始碼 ---
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')  
# 設定工作路徑
work_dir = './data_0511'
esg_env = os.path.join(work_dir, '0_raw','esg_env')
years = list(range(2021,2024,1))
esg_env_files = os.listdir(esg_env)
esg_env_files = sorted(esg_env_files)
if '.DS_Store' in esg_env_files:
    esg_env_files.remove('.DS_Store')
pdf_pageimg_folder = os.path.join(work_dir, '1_processed','extract_pdf_0513','page_image')
pdf_page_list = os.listdir(pdf_pageimg_folder)
pdf_page_list = sorted(pdf_page_list)
if '.DS_Store' in pdf_page_list :
    pdf_page_list.remove('.DS_Store')
output_path = os.path.join(work_dir, '1_processed','extract_pdf_0513','manual_text')

def manual_add_boxes(page_path):
    page_img = Image.open(page_path).convert("RGBA")

    # === 新增：先問當頁 Material Topic ===
    page_topic = input("請輸入本頁 Material Topic (GRI/TCFD 或簡述)：").strip()

    manual_boxes = []                         # list of dict
    overlay = Image.new('RGBA', page_img.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    last_bbox = {'coords': None}
    control_state = {'exit': False}

    # --------- callbacks ----------
    def onselect(eclick, erelease):
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        last_bbox['coords'] = (x1, y1, x2, y2)
        draw_and_show()

    def draw_and_show():
        overlay_draw.rectangle(last_bbox['coords'], outline="blue", width=3)
        combined = Image.alpha_composite(page_img, overlay)
        ax.clear()
        ax.imshow(combined)
        ax.set_title("按 y = keep, n = ignore, q = quit")
        ax.axis('off')
        fig.canvas.draw()

    def on_key(event):
        if event.key == 'y' and last_bbox['coords']:
            # === 新增：詢問框類型 F/T ===
            label = ''
            while label not in ('F', 'T'):
                label = input("此區域類型？(F=圖表, T=文字)：").strip().upper()
            manual_boxes.append({
                'bbox': list(last_bbox['coords']),
                'label': label,
                'topic': page_topic          # 同頁共用
            })
            print(f"[✔] 已保存 {last_bbox['coords']}  | 類型={label}")
            last_bbox['coords'] = None
        elif event.key == 'n':
            print("[✘] 上一框已捨棄")
            last_bbox['coords'] = None
        elif event.key == 'q':
            print("[🛑] 結束手動標記")
            toggle_selector.set_active(False)
            fig.canvas.mpl_disconnect(cid)
            control_state['exit'] = True
            plt.close(fig)

    # --------- 畫面 ----------
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.imshow(page_img)
    ax.set_title("拖曳選框後 → 鍵盤 y/n/q")
    ax.axis('off')
    toggle_selector = RectangleSelector(ax, onselect, useblit=True,
                                        button=[1], minspanx=5, minspany=5,
                                        spancoords='pixels', interactive=True)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show(block=True)
    plt.close(fig)
    return manual_boxes

page_bboxes = manual_add_boxes(page_path)
if page_bboxes:
    np.save(os.path.join(output_path, export_name),
            page_bboxes, allow_pickle=True)  # ← 關鍵

