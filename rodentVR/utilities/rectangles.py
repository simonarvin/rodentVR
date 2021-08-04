import numpy as np

def extract_rectangles(arr, detect:int = 1):
    arr_ = arr.copy()
    empty_canvas = np.zeros(shape = arr.shape[:2])

    rectangles = []
    holded = []
    w, h = arr_.shape
    while True:
        rectangle = []
        for y in range(h):
            for x in range(w):

                if arr_[x, y] == detect:
                    rectangle.append((x, y))
                elif len(rectangle) != 0:
                    break
            else:
                continue
            break

        if len(rectangle) == 0:
            break

        lower_corner = {"sum": -1, "index": -1}

        for i, r in enumerate(rectangle):
            sum_=r[0] + r[1]
            arr_[r[0], r[1]] = detect - 1
            if lower_corner["sum"] < sum_:
                lower_corner["sum"] = sum_
                lower_corner["r"] = r

        x, y = rectangle[0]
        w_, h_ = lower_corner["r"][0] - x, lower_corner["r"][1] - y
        rect_ = (x, y, w_ + 1, h_ + 1)

        if (w_, h_) != (0, 0):
            rectangles.append(rect_)
        else:

            empty_canvas[x, y] = detect
            holded.append(rect_)

    if len(holded) > 0:
        while True:
            rectangle = []
            for x in range(w):
                for y in range(h):

                    if empty_canvas[x, y] == detect:
                        rectangle.append((x, y))
                    elif len(rectangle) != 0:
                        break
                else:
                    continue
                break

            if len(rectangle) == 0:
                break

            lower_corner = {"sum": -1, "index": -1}

            for i, r in enumerate(rectangle):
                sum_=r[0] + r[1]
                empty_canvas[r[0], r[1]] = detect - 1
                if lower_corner["sum"] < sum_:
                    lower_corner["sum"] = sum_
                    lower_corner["r"] = r

            x, y = rectangle[0]
            w_, h_ = lower_corner["r"][0] - x, lower_corner["r"][1] - y
            rect_ = (x, y, w_ + 1, h_ + 1)
            rectangles.append(rect_)

    elif len(holded) != 0:
        rectangles = np.hstack((rectangles, holded))

    return rectangles
