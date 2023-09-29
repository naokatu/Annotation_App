import re

import PySimpleGUI as sg
import cv2 as cv
import label_file
from icecream import ic


def write_file_label(dict_label, filename):
    filename = sg.popup_get_file('　ラベルを書き込むファイルを指定してください　', save_as=True,
                                 default_path='label_text/' + filename + '.txt')
    with open(filename, 'w') as f:
        for time, label in enumerate(dict_label.values()):
            f.write(f'{time},{label}\n')


# メイン関数
def main():
    # ポップアップでファイル名を取得する
    filename = sg.popup_get_file('　再生する動画ファイルを指定してください　')

    # 　取得したファイルがNoneなら、終了
    if filename is None:
        return

    # 　選択された動画ファイルの読み込み
    vidFile = cv.VideoCapture(filename)

    # 　動画ファイルのプロパティを取得（総フレーム数、FPS）
    num_frames = vidFile.get(cv.CAP_PROP_FRAME_COUNT)
    fps = vidFile.get(cv.CAP_PROP_FPS)
    num_sec = int(num_frames // fps)
    print(num_sec)

    sg.theme('Black')

    # ラベルの読み込み部分
    filename_without_extension = filename.split('.')[0].split('/')[-1]
    print(filename_without_extension)
    # skeleton_label = label_file.read_skeleton_label('label_new/' + filename_without_extension + '_skeleton_PoseC3D.txt')
    # spatio_label = label_file.read_spatio_temporal_label(
    #     'label_new/' + filename_without_extension + '_spatiotemporal_det0.8_act0.3_sec1.txt')
    # time_labels_list = label_file.annotating(skeleton_label, spatio_label)
    # labels_list = label_file.extract_label(time_labels_list)

    # ラベル選択部分のレイアウト
    groupA_button = ['歩く', '走る', '止まる', 'なし']
    groupB_button = ['前を向く', '左を向く', '右を向く', '上を向く', '下を向く', '振り返る(左)', '振り返る(右)', 'なし']
    groupC_button = ['手を挙げる(高)', '手を挙げる(中)', '手を挙げる(低)', 'お辞儀する', '帽子(髪型)を直す',
                     '荷物を持ち帰る(左から右)',
                     '荷物を持ち帰る(右から左)', '障害物を避ける', 'なし']
    groupX_button = ['じゃり道', 'アスファルト', '溝蓋の上', 'なし']
    groupY_button = ['平地', '上り坂道', '下り坂道', '上り階段', '下り階段', 'なし']

    half = len(groupB_button) // 2

    labels_Button_layout_A = [[sg.Button(label, key=f'-Button_Label_A-', size=(12, 3))] for label in
                              groupA_button]
    labels_Button_layout_B = [[sg.Button(label, key=f'-Button_Label_B-', size=(12, 3))] for label in
                              groupB_button]
    labels_Button_layout_C_1 = [[sg.Button(label, key=f'-Button_Label_C-', size=(10, 3))] for label in
                                groupC_button[:half + 1]]
    labels_Button_layout_C_2 = [[sg.Button(label, key=f'-Button_Label_C-', size=(10, 3))] for label in
                                groupC_button[half + 1:]]
    labels_Button_layout_column3 = [[sg.Column(labels_Button_layout_C_1), sg.Column(labels_Button_layout_C_2)]]

    labels_Button_layout_X = [[sg.Button(label, key=f'-Button_Label_X-', size=(12, 3))] for label in
                              groupX_button]

    labels_Button_layout_Y = [[sg.Button(label, key=f'-Button_Label_Y-', size=(12, 3))] for label in
                              groupY_button]

    choice_labels_edit = sg.Frame("ラベル選択", layout=[
        [sg.Frame('A', layout=labels_Button_layout_A, size=(80, 600)),
         sg.Frame('B', layout=labels_Button_layout_B, size=(100, 600)),
         sg.Frame('C', layout=labels_Button_layout_column3, size=(230, 600)),
         sg.Frame('X', layout=labels_Button_layout_X, size=(100, 600)),
         sg.Frame('Y', layout=labels_Button_layout_Y, size=(80, 600))
         ]
    ])

    # 編集部分のレイアウト
    edit_input_layout = [[sg.Text('時間（秒）', size=(8, 1)), sg.Text('ラベルA', size=(10, 1)),
                          sg.Text('ラベルB', size=(10, 1)),
                          sg.Text('ラベルC', size=(10, 1)), sg.Text('ラベルX', size=(10, 1)),
                          sg.Text('ラベルY', size=(10, 1))]] + \
                        [[sg.Text(str(time_label + 1), size=(3, 1)),
                          sg.Text(size=(1, 1), key=f'-isChanged-{time}'),
                          # sg.Text(size=(1, 1), key=f'-isLow-{time}',
                          #         background_color='#dc143c' if time_label[1][1] < 0.3 else '#000'),
                          *[sg.Text(
                              '歩く' if i == 0 else '前を向く' if i == 1 else 'なし' if i == 2 else 'アスファルト' if i == 3 else '平地',
                              key=f'-Label-{time}{i}', size=(10, 1), expand_x=True, font='Helvetica 9',
                          ) for i in range(0, 5)]] for time, time_label in enumerate(range(0, num_sec + 1))]
    layout_edit = sg.Frame("ラベル編集", layout=[
        [sg.Button('ラベル読み込み', key='-Btn_Input-')],
        [sg.Column(edit_input_layout, scrollable=True, vertical_scroll_only=True, size=(520, 600))],
        [sg.Button('出力', key='-Btn_Output-'), sg.Text('', key='-copy_List-')]
    ])

    # 動画部分のレイアウト
    layout_movie = [[sg.Image(filename='', key='-image-', size=(60, 60)), layout_edit, choice_labels_edit],
                    [sg.Slider(range=(0, num_frames), size=(60, 10), orientation='h', key='-slider-')],
                    [sg.Text(f'{0}秒', pad=((600, 0), 3), font='Helvetica 20', key='-Sec-')],
                    [sg.Button('再生 / 停止', key='-Btn_Play-', size=(9, 1), pad=((600, 0), 3), font='Helvetica 14')],
                    [sg.Button('終了', key='Exit', size=(7, 1), pad=((600, 0), 3), font='Helvetica 14')]]

    window = sg.Window('　動画ファイルを再生するアプリ　', layout_movie, no_titlebar=False, location=(0, 0),
                       finalize=True)

    image_elem = window['-image-']
    slider_elem = window['-slider-']
    sec_elem = window['-Sec-']

    # ラベルショートカット
    window.bind('<g>', 'cap')

    # 1次元移動
    window.bind('<k>', 'play/stop')
    window.bind('<j>', 'back')
    window.bind('<l>', 'forward')

    # 方向キーで2次元移動
    window.bind('<Up>', 'back')
    window.bind('<Down>', 'forward')
    window.bind('<Left>', 'left')
    window.bind('<Right>', 'right')

    # コピー＆ペースト
    window.bind('<Control-Key-c>', 'copy')
    window.bind('<Control-Key-v>', 'paste')

    # for i in range(0, len(time_labels_list)):
    for i in range(0, num_sec + 1):
        for j in range(0, 5):
            window['-Label-' + str(i) + str(j)].bind('<ButtonPress>', f'click_on{i}{j}')

    cur_col = 0
    prev_col = 0
    cur_frame = 0
    prev_sec = 0
    stop_flag = True
    copy_list = []

    # 　ビデオファイルが開かれている間は、ループ
    while vidFile.isOpened():

        # イベントを取得
        event, values = window.read(timeout=20)

        cur_sec = cur_frame // 30

        sec_elem.update(f'{cur_frame // 30 + 1}秒')

        if 'copy' in event:
            copy_list = []
            for i in range(0, 5):
                copy_list.append(window['-Label-' + str(cur_sec) + str(i)].DisplayText)

            window['-copy_List-'].update(copy_list)

        if 'paste' in event:
            if copy_list:
                for i, element in enumerate(copy_list):
                    window['-Label-' + str(cur_sec) + str(i)].update(element)
                    window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')

                cur_frame += 30
                values['-slider-'] = cur_frame
                prev_sec = cur_sec
                cur_sec = cur_frame // 30

        if 'back' in event:
            if cur_sec > 0:
                cur_frame -= 30
                cur_frame -= cur_frame % 30
            else:
                cur_frame = 0

            values['-slider-'] = cur_frame
            prev_sec = cur_sec
            cur_sec = cur_frame // 30

        if 'forward' in event:
            if num_frames - 30 > cur_frame:
                cur_frame += 30
                cur_frame -= cur_frame % 30

            values['-slider-'] = cur_frame
            prev_sec = cur_sec
            cur_sec = cur_frame // 30

        if 'left' in event:
            if cur_col > 0:
                prev_col = cur_col
                cur_col -= 1
            else:
                cur_frame -= 30
                values['-slider-'] = cur_frame
                prev_col = cur_col
                cur_col = 2
                prev_sec = cur_sec
                cur_sec = cur_frame // 30

        if 'right' in event:
            if cur_col < 4:
                prev_col = cur_col
                cur_col += 1
            else:
                cur_frame += 30
                values['-slider-'] = cur_frame
                prev_col = cur_col
                cur_col = 0
                prev_sec = cur_sec
                cur_sec = cur_frame // 30

        if 'cap' in event:
            window['-Label-' + str(cur_sec) + str(3)].update('溝蓋の上')
            window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')

        changed = False
        # ラベル選択部分のボタンが押されたらText置換
        if 'Button_Label' in event:

            if 'A-' in event:
                window['-Label-' + str(cur_sec) + str(0)].update(window[event].ButtonText)
                window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')
                changed = True
            elif 'B-' in event:
                window['-Label-' + str(cur_sec) + str(1)].update(window[event].ButtonText)
                window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')
                changed = True
            elif 'C-' in event:
                window['-Label-' + str(cur_sec) + str(2)].update(window[event].ButtonText)
                window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')
                changed = True
            elif 'X-' in event:
                window['-Label-' + str(cur_sec) + str(3)].update(window[event].ButtonText)
                window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')
                changed = True
            elif 'Y-' in event:
                window['-Label-' + str(cur_sec) + str(4)].update(window[event].ButtonText)
                window['-isChanged-' + str(cur_sec)].update(background_color='#4682b4')
                changed = True
            else:
                pass

            ## ラベルを変えたら次のマスに
            # if changed:
            #     if cur_col < 4:
            #         prev_col = cur_col
            #         cur_col += 1
            #     else:
            #         cur_frame += 30
            #         values['-slider-'] = cur_frame
            #         prev_col = cur_col
            #         cur_col = 0
            #         prev_sec = cur_sec
            #         cur_sec = cur_frame // 30

        # 現在のラベルを緑色にハイライト　時間が変わったら前のラベルは黒に戻す
        if cur_sec != prev_sec or cur_col != prev_col:
            window['-Label-' + str(cur_sec) + str(cur_col)].update(background_color="#3cb371")
            window['-Label-' + str(prev_sec) + str(prev_col)].update(background_color="#000")
            prev_col = cur_col
        else:
            window['-Label-' + str(cur_sec) + str(cur_col)].update(background_color="#3cb371")

        if event in ('Exit', None):
            break

        # 出力ボタンが押されたら入力値をすべて取得
        if event in ('-Btn_Output-', None):
            all_input_label_dict = {}
            for i in range(0, num_sec + 1):
                temp_List = []
                for j in range(0, 5):
                    temp_List.append(window['-Label-' + str(i) + str(j)].DisplayText)
                all_input_label_dict[i] = temp_List

            ic(all_input_label_dict)
            # ファイル出力
            write_file_label(all_input_label_dict, filename_without_extension)
            break

        # ラベル読み込み
        if event in ('-Btn_Input-', None):
            filename = sg.popup_get_file('　ラベルを読み込むファイルを指定してください　',
                                         default_path='label_text/' + filename_without_extension + '.txt')

            label = label_file.read_label(filename)

            for i in range(0, len(label)):
                for j in range(0, 5):
                    window['-Label-' + str(i) + str(j)].update(label[i][j])

        if event in ('-Btn_Play-', None) or 'play/stop' in event:
            stop_flag = not stop_flag

        # 指定したラベルのフレームにジャンプ
        if 'click_on' in event:
            print(event)
            cur_frame = int(re.findall(r"\d+", event)[1][:-1]) * 30
            prev_col = cur_col
            cur_col = int(re.findall(r"\d+", event)[1][-1])
            values['-slider-'] = cur_frame
            prev_sec = cur_sec

            # window['-Label-' + str(prev_sec) + str(prev_col)].update(background_color="#000")

        # スライダーを手動で動かした場合は、指定したフレームにジャンプ
        if int(values['-slider-']) != cur_frame - 1:
            cur_frame = int(values['-slider-'])
            prev_sec = cur_sec
            vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)

        # ビデオファイルからの読み込み
        ret, frame = vidFile.read()

        # データが不足している場合は、一時停止
        if not ret:  # if out of data stop looping
            continue

        # スライダー表示を更新
        if stop_flag:
            vidFile.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
        else:
            slider_elem.update(cur_frame)
            cur_frame += 1

        # カメラ映像を圧縮して、画像表示画面'-image-'を更新する

        img = cv.resize(frame, dsize=None, fx=0.5, fy=0.5)
        imggs = cv.imencode('.png', img)[1]
        imgbytes = imggs.tobytes()
        image_elem.update(data=imgbytes)

        # ストップボタンが押されたらcontinue
        if stop_flag:
            slider_elem.update(cur_frame)
            continue

        prev_sec = cur_sec


# メイン関数をCALL
main()
