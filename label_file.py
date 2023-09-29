# skeletonファイル,PoseC3Dを読み込み、データをリストに格納する
# [[[label1, score1],[label2, score2]],[labelA, scoreA], [labelB, scoreB]]
def read_skeleton_label(file_path):
    result_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split(',', 1)[1]
            line = line.replace(']', '],')
            # 最後のコンマは除外
            elements = eval(line[:-1])
            # 「walk」に置き換え
            # if 'support somebody' in elements[0][0] or 'walking' in elements[0][0]:
            #     elements[0][0] = 'walk'
            # 信頼度が一番高いラベルを抽出
            result_list.append(list(elements[0]))

    return result_list


def read_csn_label(file_path):
    result_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split(',', 1)[1]
            line = line.replace(')', '],')
            line = line.replace('(', '[')
            # 最後のコンマは除外
            elements = eval(line[:-1])
            result_list.append(list(elements[0]))

    return result_list


def read_spatio_temporal_label(file_path):
    result_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split(',', 1)[1]
            line = line.replace(')', ']')
            line = line.replace('(', '[')
            # 複数人数検知したとき一人目を抽出
            if line.count('[[') >= 2:
                line = line.rsplit('[[', line.count('[[') - 1)[0]
            line = line.replace('[]', '')
            # 要素があるとき
            if line:
                elements = eval(line)
                result_list.append(list(elements[0]))
            else:
                result_list.append([])

    return result_list

def read_label(file_path):
    result_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split(',', 1)[1]
            elements = eval(line)
            result_list.append(elements)

    return result_list

def calc_top_score(skl_label, spa_label):
    if skl_label[1] * 6 > spa_label[1] * 4:
        return skl_label
    else:
        return spa_label


def annotating(skeleton_list, spatio_list):
    spatio_list_len = len(spatio_list)
    time = 0
    result_label = []
    count = 1
    for skl, spa in zip(skeleton_list, spatio_list):
        # spatioが空の時
        if not spa:
            better_score = skl
        else:
            better_score = calc_top_score(skl, spa)

        result_label.append([count, better_score])
        count += 1

    # spatioの方が短いため最後の数秒はskeleton
    for skl in skeleton_list[spatio_list_len:]:
        result_label.append([count, skl])
        count += 1

    return result_label


def extract_label(time_label_list):
    label_list = []
    for label in time_label_list:
        label_list.append(label[1][0])
        # print(label[1][0])

    label_set = list(set(label_list))

    return label_set
