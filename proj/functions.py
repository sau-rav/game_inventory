# funtions file separated for clairty

def disp_list_generator(page, list_size):
    disp_dict = {}
    disp_list = []
    for i in range(1, 4):
        disp_dict[i] = 1
    for i in range(list_size-2, list_size+1):
        disp_dict[i] = 1
    for i in range(page-1, page+3):
        if i >= 1 and i <= list_size:
            disp_dict[i] = 1
    for e in disp_dict:
        disp_list.append(e)
    disp_list.sort()
    return disp_list

def extract_data(data, delimiter):
    data_list = []
    element = ''
    idx = 0
    for i in range(len(data)):
        if data[i] != delimiter:
            element += data[i]
        else:
            data_list.append(element)
            element = ''
    if len(element) > 0:
        data_list.append(element)
    print(data_list)
    return data_list