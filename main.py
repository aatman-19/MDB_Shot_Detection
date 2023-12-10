import cv2
import os
import numpy as np


def intensity_code_feature(image):
    # Extract the R, G, and B channels
    b_channel = image[:, :, 0]
    g_channel = image[:, :, 1]
    r_channel = image[:, :, 2]

    # calculating intensity acc to the provided formula
    intensity = 0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel

    # initially dividing into bins of edge 10 ranging from 0 to 260
    hist, bin_edges = np.histogram(intensity, bins=26, range=(0, 260), density=False)

    # Since max range is actually 255, adding all the values of 26th bin to the 25th - adjust for uneven bin size (
    # 240,255)
    hist[24] += hist[25]

    # 0th index - image size, concat it with rest of the hist to get final histogram
    histogram = list(hist.astype(np.int64)[:25])
    return histogram


def frame_capture(path):
    vid_obj = cv2.VideoCapture(path)
    frame_count = 0
    success = 1
    temp_mat = []

    while success:
        success, image = vid_obj.read()
        # create a histogram
        if not success or frame_count >= 5000:
            break

        if 1000 <= frame_count <= 4999:
            temp_mat.append(intensity_code_feature(image))

        if frame_count == 1000 or frame_count == 4999:
            cv2.imwrite("frame%d.jpg" % frame_count, image)

        frame_count += 1

    feature_matrix = np.zeros((4000, 25), dtype=np.int32)

    for i in range(0, len(temp_mat)):
        feature_matrix[i] = temp_mat[i]

    print(len(feature_matrix))
    return feature_matrix


def sd_array(feature_matrix):
    sd = list()
    length = len(feature_matrix)
    for i in range(0, length-1):
        diff = 0
        for j in range(0, 25):
            diff += abs(feature_matrix[i][j] - feature_matrix[i + 1][j])
        sd.append(diff)
    return sd


def get_thresholds(sd_array):
    deviation = np.std(sd_array)
    m = np.mean(sd_array)
    t_cut = round(m + deviation * 11)
    t_transition = round(2 * m)
    return t_cut, t_transition


def get_ce(sd_array):
    ce = list()
    for i in range(0, len(sd_array)):
        if sd_array[i] >= tb:
            cut = [1000 + i, 1000 + i + 1]
            ce.append(cut)
    return ce


def get_fs_candidates(sd_array):
    fs_candidate = list()
    fe_candidate = list()
    length = len(sd_array)
    i = 0
    while i < length:
        if ts <= sd_array[i] < tb:
            #fs_candidate.append(i)
            temp_fs = i
            tor = 2
            j = i + 1
            while tor > 0:
                if sd_array[j] < ts:
                    tor -= 1
                elif ts <= sd_array[j] < tb:
                    tor = 2
                else:
                    break
                j += 1
            #fe_candidate.append(j)
            temp_fe = j
            if temp_fe-temp_fs > 1:
                fs_candidate.append(temp_fs)
                fe_candidate.append(temp_fe)
            i = j
            continue
        i += 1
    return fs_candidate, fe_candidate


def get_real_fs(fs_candidate, fe_candidate, sd_array, tb):
    f_real = list()
    length = len(fs_candidate)
    for i in range(0, length):
        total = 0
        for j in range(fs_candidate[i], fe_candidate[i]+1):
            total += sd_array[j]
        if total >= tb:
            f_element = [1000+fs_candidate[i],1000+fe_candidate[i]]
            f_real.append(f_element)
    return f_real


if __name__ == '__main__':
    # Calling the function
    f_mat = frame_capture('20020924_juve_dk_02a.mpg')
    # print(f_mat)
    sd = sd_array(f_mat)
    # print(sd)
    tb, ts = get_thresholds(sd)
    # print(f"Thresholds - cut: {tb}, gradual transition: {ts}")
    cuts = get_ce(sd)
    print(cuts)
    fs_c, fe_c = get_fs_candidates(sd)
    print(fs_c)
    print(fe_c)
    print(f"fs_candidates = {len(fs_c)}, fe_candidates = {len(fe_c)}")
    transitions = get_real_fs(fs_c, fe_c, sd, tb)
    print(transitions)
    print(len(transitions))
