import os
import shutil
import cv2

from PIL import Image, ImageFont, ImageDraw

file_name = "2.gif"
folder_name = "2-frames"

frames_fg = []
x, y = 0, 0
font = ImageFont.truetype('arial', 20)
string = "Salut fratelo. Ce pula mea mai faci?"

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

    print([name for name in os.listdir(f"{gif[:-4]}-frames\\.")])
    max_count = len([name for name in os.listdir(f"{gif[:-4]}-frames\\.")]) - 1
    for count in range(max_count + 1):
        os.rename(f"{gif[:-4]}-frames\\frame%d.jpg" % count,
                  f"{gif[:-4]}-frames\\frame%s.jpg" % offset(count, max_count))

    print("Successful")

def create_image_with_text(size, text, font):
    width, height = size
    img = Image.new('RGBA', (400, 400))
    draw = ImageDraw.Draw(img)
    draw.text((width, height), text, font=font, fill="black")
    return img

def create_text_animation():
    for i in range(len(string) + 20):
        if i < len(string):
            new_frame = create_image_with_text((x, y), string[:i], font)
        else:
            new_frame = create_image_with_text((x, y), string, font)
        frames_fg.append(new_frame)

def overlap_text_on_gif():
    extract_frames(f"results/{file_name}")
    frames_bg = []

    for frame in range(Image.open(f"results/{file_name}").n_frames):
        frames_bg.append(Image.open(f"results/{folder_name}/frame%02d.jpg" % frame).convert("RGBA"))

    longest = len(frames_fg) if len(frames_fg) > len(frames_bg) else len(frames_bg)

    results = []

    for i in range(longest):
        i_bg = i % len(frames_bg)
        i_fg = i % len(frames_fg)

        bg = frames_bg[i_bg].copy()
        fg = frames_fg[i_fg].copy()

        bg.alpha_composite(fg, (0, 0))
        results.append(bg)

    results[0].save('results/result.gif', save_all=True, append_images=results[1:], loop=0, duration=30)
    shutil.rmtree(f"results/{folder_name}")


create_text_animation()
overlap_text_on_gif()
