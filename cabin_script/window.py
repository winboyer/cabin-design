# 接收窗户locate列表，返回空隙列表（从对侧开始从1开始计数）
def find_gap_locate(win_locate: list) -> list:

    sorted_nums = sorted(win_locate)
    gaps = []

    for i in range(1, len(sorted_nums)):
        prev = sorted_nums[i - 1]
        current = sorted_nums[i]

        if current - prev > 1:
            for gap_num in range(prev + 1, current):
                gaps.append(gap_num)

    return gaps

# 寻找窗户两侧的框架梁的位置序号（窗户数量大于1的时候会使用，这里窗户不可以位于最边上，即 locate中的数>=2）
def find_win_frame_column(win_locate: list) -> list:
    column_list = []
    for locate in win_locate:
        column_list.append(locate)
        column_list.append(locate+1)
    column_list = sorted(list(set(column_list)))
    c_list = []
    # 去除序号为1的框架柱
    for x in column_list:
        if x != 1:
            c_list.append(x)
    return c_list

# 寻找环向主梁的位置序号
def find_win_main_column(win_locate: list, params: dict) -> list:
    column_list = []
    for i in range(params["dis"]["side"]["num"]+1):
        column_list.append(i+1)
    frame_column_list = find_win_frame_column(win_locate)
    for column in frame_column_list:
        if column in column_list:
            column_list.remove(column)
    for column in column_list:
        if column == 1:
            column_list.remove(column)
    return column_list







