import copy
from cabin_result.summary import process_all_folders
import cabin_processor.iterator as i

if __name__ == "__main__":

    base_params = {
        "cabin_length": 12000.0,
        "window": {
            "width": 1200.0,
            "right": {
                "locate": [2,4,5]
            },
            "left": {
                "locate": [2,4,3,5,6]
            },
            "offside": {
                "num": 2
            }
        }
    }


    window_widths = [500.0, 700.0, 800.0, 1000.0, 1200.0]

    for k in range(5):
        params = copy.deepcopy(base_params)
        params["window"]["width"] = window_widths[k]
        globals()[f'params{k + 1}'] = params

    base_dir = "F:\\CAE\\cube_test3"   # 这个地址是迭代文件夹存放的地方

    a = i.PartsIterator(params1, base_dir)
    a.run()
    a = i.PartsIterator(params2, base_dir)
    a.run()
    a = i.PartsIterator(params3, base_dir)
    a.run()
    a = i.PartsIterator(params4, base_dir)
    a.run()

    docx_savepath = process_all_folders(base_dir)