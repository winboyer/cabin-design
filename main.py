import cabin_processor.iterator as i
import cabin_processor.submitter as s

if __name__ == "__main__":

    base_params = params = {
        "cabin_length": 12000.0,
        "window": {
            "width": 1250.0,
            "right": {
                "num": 1,
                "locate": 2
            },
            "left": {
                "num": 1,
                "locate": 2
            },
            "offside": {
                "num": 2
            }
        },
        "work_path": "F:\CAE\cube"
    }
    # base_dir = "F:\\CAE\\cube_test"   #把这个文件夹换成你自己的
    base_dir = "F:\\jinyfeng\\datas\\CAE"

    a = i.PartsIterator(base_params, base_dir)
    final_df = a.run()
    print(final_df)
    print(a.over_limit_df)
