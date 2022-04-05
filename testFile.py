import cv2
import os
import shutil
import glob
from PIL import Image

import numpy as np

########################################################################
###                          EXTRACT FRAMES                          ###
########################################################################
def offset(nr, max_nr):
    nr_temp = nr
    max_nr_temp = max_nr

    nr_len = len(str(nr_temp))
    max_len = len(str(max_nr_temp))

    return '0' * (max_len - nr_len) + str(nr)

def extract_frames(gif):
    input = gif

    vid_cap = cv2.VideoCapture(input)
    success, image = vid_cap.read()
    count = 0

    while success:
        if not os.path.exists(f"{input[:-4]}-frames"):
            os.makedirs(f"{input[:-4]}-frames")
        cv2.imwrite(f"{input[:-4]}-frames\\frame%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vid_cap.read()
        print('Read a new frame: ', success)
        count += 1

    max_count = len([name for name in os.listdir(f"{input[:-4]}-frames\\.")]) - 1
    for count in range(max_count + 1):
        os.rename(f"{input[:-4]}-frames\\frame%d.jpg" % count,
                  f"{input[:-4]}-frames\\frame%s.jpg" % offset(count, max_count))

    print("Successful")

########################################################################
###                       REMOVE BACKGROUNDS                         ###
########################################################################
def remove_backgrounds(frames_dir_path):
    for img_path in glob.glob(f"{frames_dir_path}/*"):
        img = cv2.imread(img_path)

        # Convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold input image as mask
        mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]

        # Negate mask
        mask = 255 - mask

        # Apply morphology to remove isolated extraneous noise
        # Use border constant of black since foreground touches the edges
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Anti-alias the mask -- blur then stretch
        # Blur alpha channel
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT)

        # Linear stretch so that 127.5 goes to 0, but 255 stays 255
        mask = (2 * (mask.astype(np.float32)) - 255.0).clip(0, 255).astype(np.uint8)

        # Put mask into alpha channel
        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask

        cv2.imwrite(f"{img_path[:-4]}.png", result)
        os.remove(img_path)

########################################################################
###                           GENERATE GIF                           ###
########################################################################
def overlap(foreground, background, size, offset):
    for current_frame in foreground:
        current_background = background.copy()
        current_foreground = current_frame.convert(mode="RGBA").resize(size)
        current_background.alpha_composite(current_foreground, dest=offset)
        yield current_background

def generate_gif(frames_dir_path, background_image_path):
    images = []

    for frame in range(15):
        images.append(Image.open(f"{frames_dir_path}/frame%02d.png" % frame))

    bg_image = Image.open(background_image_path).convert(mode="RGBA")

    frames = tuple(overlap(images, bg_image, (100, 100), (220, 25)))
    frames[0].save('results/result.gif', save_all=True, append_images=frames[1:], loop=0, duration=30)

########################################################################

if __name__ == '__main__':
    gif = "results/calul-alearga.gif"

    extract_frames(gif)
    remove_backgrounds(f"{gif[:-4]}-frames")
    generate_gif(f"{gif[:-4]}-frames", "cartoon_env/forest.jpg")
    shutil.rmtree(f"{gif[:-4]}-frames")
