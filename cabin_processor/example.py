params = {
    "cabin_length":  12000.0,
    "window": {
        "width":  680.0,
        "right": {
            "num": 1,
            "locate": 4
        },
        "left": {
            "num": 0,
            "locate": 5
        },
        "offside": {
            "num": 3
        }
    },
    "work_path": "F:\CAE\cube1"
}

import cabin_processor.submitter_old as p
a = p.Submitter(params)
a.put_into_job()
