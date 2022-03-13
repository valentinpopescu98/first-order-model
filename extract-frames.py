from argparse import ArgumentParser
import os
import cv2

def offset(nr, maxNr):
    nrTemp = nr
    maxNrTemp = maxNr

    nrLen = len(str(nrTemp))
    maxLen = len(str(maxNrTemp))

    return '0' * (maxLen - nrLen) + str(nr)

def extraction(args):
    input = args.inp

    vidcap = cv2.VideoCapture(input)
    success, image = vidcap.read()
    count = 0

    while success:
        if not os.path.exists(f"{input[:-4]}Frames"):
            os.makedirs(f"{input[:-4]}Frames")
        cv2.imwrite(f"{input[:-4]}Frames\\frame%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vidcap.read()
        print('Read a new frame: ', success)
        count += 1

    maxCount = len([name for name in os.listdir(f"{input[:-4]}Frames\\.")]) - 1
    for count in range(maxCount + 1):
        os.rename(f"{input[:-4]}Frames\\frame%d.jpg" % count,
                  f"{input[:-4]}Frames\\frame%s.jpg" % offset(count, maxCount))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--inp", required=True, help='Input video')
    args = parser.parse_args()

    extraction(args)
    print("Successful")