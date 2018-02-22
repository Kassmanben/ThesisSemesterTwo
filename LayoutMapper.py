import cv2
import numpy as np
import scipy.misc
import pickle

width_of_whitespace = 23
isBorder = True
searching = False
pages_part_counters = {}

def mark_state(test_img):
    global isBorder, searching
    start_Coord = 0
    part_counter = 0
    border_whitespace_counter = 0
    for y in range(len(test_img)):
        # print(isBorder)
        if np.min(test_img[y]) == 255:
            isBorder = True
            border_whitespace_counter += 1

        else:
            isBorder = False
            border_whitespace_counter = 0

        if isBorder and searching and border_whitespace_counter>width_of_whitespace:
            scipy.misc.imsave(str(pg_num) +"Part "+ str(part_counter) + '.bmp',
                              test_img[start_Coord:y])
            searching = False
            part_counter += 1

        if not isBorder and not searching:
            searching = True
            start_Coord = y
    pages_part_counters[pg_num] = part_counter

for x in range(12, 14):
    # print(x)
    pg_num = x
    if pg_num < 10:
        img = cv2.imread('/Users/Ben/Desktop/Algorithms/Algorithms-0' + str(pg_num) + '.png', 0)
    else:
        img = cv2.imread('/Users/Ben/Desktop/Algorithms/Algorithms-' + str(pg_num) + '.png', 0)
    # img = cv2.imread('building.jpg', 0)
    imageWidth = img.shape[1]  # Get image width
    imageHeight = img.shape[0]
    mark_state(img)
for key in pages_part_counters.keys():
    print(str(key) + " : " + str(pages_part_counters[key]))

with open('ppc.pickle', 'wb') as handle:
    pickle.dump(pages_part_counters, handle, protocol=pickle.HIGHEST_PROTOCOL)

