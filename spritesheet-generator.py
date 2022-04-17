import glob
import os
import os.path
import shutil
import subprocess

import cv2
import numpy as np
from PIL import Image

########################################################################
###                          GENERATE DEMO                           ###
########################################################################
def exec_terminal_command(fps, image, video, result):
    os.chdir("fom")

    subprocess.run([
        "python", "demo.py", "--fps", f"{fps}", "--config", "config/mgif-256.yaml", "--driving_video",
        f"drv_video/{video}", "--source_image", f"src_image/{image}", "--checkpoint",
        "checkpoints/mgif-cpk.pth.tar", "--result_video", f"../results/{result}", "--relative", "--adapt_scale"
    ], shell=True)

    os.chdir("..")


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
    vid_cap = cv2.VideoCapture(gif)
    success, image = vid_cap.read()
    count = 0

    while success:
        if not os.path.exists(f"{gif[:-4]}-frames"):
            os.makedirs(f"{gif[:-4]}-frames")
        cv2.imwrite(f"{gif[:-4]}-frames\\frame%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vid_cap.read()
        print('Read a new frame: ', success)
        count += 1

    max_count = len([name for name in os.listdir(f"{gif[:-4]}-frames\\.")]) - 1
    for count in range(max_count + 1):
        os.rename(f"{gif[:-4]}-frames\\frame%d.jpg" % count,
                  f"{gif[:-4]}-frames\\frame%s.jpg" % offset(count, max_count))

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
###                       GENERATE SPRITESHEET                       ###
########################################################################
def generate_spritesheet(frames_dir_path):
    images = [Image.open(img_path) for img_path in glob.glob(f"{frames_dir_path}/*")]

    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGBA', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    # new_im = add_transparency(new_im)

    new_im.save(f"{frames_dir_path[:-7]}-spritesheet.png", "PNG")


########################################################################


if __name__ == "__main__":
    # Create 2 variables and input them from keyboard
    words = input("Enter the sentence: ").split()

    image = "horse.jpg"
    video = "horse-canter.gif"

    # Generate a name for the result file with given character and action separated by "_"
    result = f"{words[0]}-{words[1]}.gif"

    # Generate the demo using the created variables for files names inputs
    exec_terminal_command(30, image, video, result)

    extract_frames(f"results/{result}")
    remove_backgrounds(f"results/{result[:-4]}-frames")
    generate_spritesheet(f"results/{result[:-4]}-frames")
    shutil.rmtree(f"results/{result[:-4]}-frames")
