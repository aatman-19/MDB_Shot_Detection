from VideoShot import VideoShot
import numpy as np
import os

if __name__ == "__main__":
    path = '20020924_juve_dk_02a.mpg'
    shot_obj = VideoShot(path)
    shot_obj.feature_matrix = shot_obj.frame_capture(shot_obj.video_path)
    shot_obj.sd = shot_obj.sd_array(shot_obj.feature_matrix)
    shot_obj.tb, shot_obj.ts = shot_obj.get_thresholds(shot_obj.sd)
    shot_obj.cuts = shot_obj.get_ce(shot_obj.sd,shot_obj.tb)
    fs_c = []
    fe_c = []
    fs_c, fe_c = shot_obj.get_fs_candidates(shot_obj.sd,shot_obj.tb,shot_obj.ts)
    shot_obj.transitions = shot_obj.get_real_fs(fs_c,fe_c,shot_obj.sd,shot_obj.tb)
    print("-"*20+"cuts"+"-"*20)
    print(shot_obj.cuts)
    print("-" * 20 + "Transition" + "-" * 20)
    print(shot_obj.transitions)

    shot_obj.output_cuts(shot_obj.cuts,shot_obj.video_path)
    shot_obj.output_transitions(shot_obj.transitions,shot_obj.video_path)