import glob
import os
import os.path
import shutil
import subprocess
import sys
import cv2
import numpy as np

from PIL import Image
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox


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
def extract_frames(gif):
    vid_cap = cv2.VideoCapture(gif)
    success, image = vid_cap.read()
    count = 0

    while success:
        if not os.path.exists(f"{gif[:-4]}-frames"):
            os.makedirs(f"{gif[:-4]}-frames")
        cv2.imwrite(f"{gif[:-4]}-frames\\frame%02d.jpg" % count, image)  # save frame as JPEG file
        success, image = vid_cap.read()
        count += 1

    print("Frames extraction successful!")


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
def create_spritesheet(frames_dir_path):
    images = [Image.open(img_path) for img_path in glob.glob(f"{frames_dir_path}/*")]

    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGBA', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(f"{frames_dir_path[:-7]}-spritesheet.png", "PNG")


########################################################################
###                                                                  ###
########################################################################
def generate_spritesheet(image, video):
    # Generate the demo using the created variables for files names inputs
    exec_terminal_command(30, image, video, "spritesheet.gif")

    extract_frames(f"results/spritesheet.gif")
    remove_backgrounds(f"results/spritesheet-frames")
    create_spritesheet(f"results/spritesheet-frames")

    shutil.rmtree(f"results/spritesheet-frames")
    os.remove(f"results/spritesheet.gif")


########################################################################
###                          USER INTERFACE                          ###
########################################################################
def show_dialog(title, description, icon, font):
    mbox = QMessageBox()

    mbox.setIcon(icon)
    mbox.setFont(font)
    mbox.setWindowTitle(title)
    mbox.setText(description)

    mbox.exec_()


def on_generate_click(image_text, video_text):
    image = image_text.text()
    video = video_text.text()

    if not image and not video:
        show_dialog("Error", "Please input the source image and driving video name!", QMessageBox.Critical, text_font)
    elif not image:
        show_dialog("Error", "Please input the source image name!", QMessageBox.Critical, text_font)
    elif not video:
        show_dialog("Error", "Please input the driving video name!", QMessageBox.Critical, text_font)
    else:
        generate_spritesheet(image, video)
        show_dialog("Success", "The spritesheet was generated!", QMessageBox.Information, text_font)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(500, 400)
    w.setWindowTitle('Cartoon generator')

    text_font = QFont("Arial", 12)

    image_label = QLabel(w)
    image_label.setFont(text_font)
    image_label.setText("Source image name:")
    image_label.move(25, 15)
    image_label.show()

    image_text = QLineEdit(w)
    image_text.setFont(text_font)
    image_text.resize(450, 20)
    image_text.move(20, 35)
    image_text.show()

    video_label = QLabel(w)
    video_label.setFont(text_font)
    video_label.setText("Driving video name:")
    video_label.move(25, 60)
    video_label.show()

    video_text = QLineEdit(w)
    video_text.setFont(text_font)
    video_text.resize(450, 20)
    video_text.move(20, 80)
    video_text.show()

    generate_btn = QPushButton(w)
    generate_btn.setFont(text_font)
    generate_btn.setText('GENERATE')
    generate_btn.resize(400, 20)
    generate_btn.move(50, 360)
    generate_btn.clicked.connect(lambda: on_generate_click(image_text, video_text))
    generate_btn.show()

    w.show()
    sys.exit(app.exec_())
