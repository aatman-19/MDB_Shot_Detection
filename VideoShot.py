import cv2
import os
import numpy as np


class VideoShot:
    def __init__(self, path):
        self.video_path = path
        self.feature_matrix = self.frame_capture(self.video_path)
        self.sd = self.sd_array(self.feature_matrix)
        self.tb, self.ts = self.get_thresholds(self.sd)
        self.cuts = self.get_ce(self.sd, self.tb)
        self.fs_c, self.fe_c = self.get_fs_candidates(self.sd, self.tb, self.ts)
        self.transitions = self.get_real_fs(self.fs_c,self.fe_c,self.sd,self.tb)
        self.output_cuts(self.cuts,self.video_path)
        self.output_transitions(self.transitions,self.video_path)

    def intensity_code_feature(self, image):
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

    def frame_capture(self, path):
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
                temp_mat.append(self.intensity_code_feature(image))

            # if frame_count == 1000 or frame_count == 4999:
            #     cv2.imwrite("frame%d.jpg" % frame_count, image)

            frame_count += 1

        feature_matrix = np.zeros((4000, 25), dtype=np.int32)

        for i in range(0, len(temp_mat)):
            feature_matrix[i] = temp_mat[i]

        print(len(feature_matrix))
        return feature_matrix

    def sd_array(self, feature_matrix):
        sd = list()
        length = len(feature_matrix)
        for i in range(0, length - 1):
            diff = 0
            for j in range(0, 25):
                diff += abs(feature_matrix[i][j] - feature_matrix[i + 1][j])
            sd.append(diff)
        return sd

    def get_thresholds(self, sd_array):
        deviation = np.std(sd_array)
        m = np.mean(sd_array)
        t_cut = round(m + deviation * 11)
        t_transition = round(2 * m)
        return t_cut, t_transition

    def get_ce(self, sd_array, tb):
        ce = list()
        for i in range(0, len(sd_array)):
            if sd_array[i] >= tb:
                cut = [1000 + i, 1000 + i + 1]
                ce.append(cut)
        return ce

    def get_fs_candidates(self, sd_array, tb, ts):
        fs_candidate = list()
        fe_candidate = list()
        length = len(sd_array)
        i = 0
        while i < length:
            if ts <= sd_array[i] < tb:
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
                temp_fe = j
                if temp_fe - temp_fs > 1:
                    fs_candidate.append(temp_fs)
                    fe_candidate.append(temp_fe)
                i = j
                continue
            i += 1
        return fs_candidate, fe_candidate

    def get_real_fs(self, fs_candidate, fe_candidate, sd_array, tb):
        f_real = list()
        length = len(fs_candidate)
        for i in range(0, length):
            total = 0
            for j in range(fs_candidate[i], fe_candidate[i] + 1):
                total += sd_array[j]
            if total >= tb:
                f_element = [1000 + fs_candidate[i], 1000 + fe_candidate[i]]
                f_real.append(f_element)
        return f_real

    def output_cuts(self, cuts, video_path):
        vid_obj = cv2.VideoCapture(video_path)

        for ce in cuts:
            vid_obj.set(cv2.CAP_PROP_POS_FRAMES, ce[1])
            success, image = vid_obj.read()

            if not success:
                print("Error loading the cut scenes")
                return

            cv2.imwrite("outputs/cuts/frame%d.jpg" % ce[1], image)
        print("cuts extracted successfully!")

    def output_transitions(self, transitions, video_path):
        vid_obj = cv2.VideoCapture(video_path)

        for fs in transitions:
            vid_obj.set(cv2.CAP_PROP_POS_FRAMES, fs[0] + 1)
            success, image = vid_obj.read()

            if not success:
                print("Error loading the cut scenes")
                return

            cv2.imwrite("outputs/transitions/frame%d.jpg" % (fs[0] + 1), image)

        print("transitions extracted successfully!")

    def get_nearest_end_frame(self, curr_frame, cuts, transitions):
        combined = cuts + transitions
        combined_ = [row[0] for row in combined]
        search_space = [num for num in combined_ if num > curr_frame]
        if search_space:
            next_frame = min(search_space)
            return next_frame
        else:
            return 4999
