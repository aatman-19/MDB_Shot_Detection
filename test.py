from VideoShot import VideoShot

if __name__ == "__main__":
    path = '20020924_juve_dk_02a.mpg'
    shot_obj = VideoShot(path)

    print("-" * 20 + "cuts" + "-" * 20)
    print(shot_obj.cuts)
    print("-" * 20 + "Transition" + "-" * 20)
    print(shot_obj.transitions)


