import glob
import json
import os
import shutil
import subprocess
import cv2
import numpy

from PIL import Image, ImageDraw, ImageFont


########################################################################
###                        PARSE INPUT JSONS                         ###
########################################################################
def get_files_data(file):
    file = open(file)
    data = json.load(file)
    file.close()

    return data


########################################################################
###                         PARSE INPUT DATA                         ###
########################################################################
def get_character(words, characters_json):
    return characters_json[words[0]]["file"]


def get_action(words, characters_json, actions_json):
    if characters_json[words[0]]["type"] == "humanoid":
        return actions_json[words[1]]["file_for_humanoid"]
    elif characters_json[words[0]]["type"] == "quadruped":
        return actions_json[words[1]]["file_for_quadruped"]


def get_place(words, places_json):
    if len(words) < 3 or words[2] not in places_json:
        return

    return places_json[words[2]]


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

    print("GIF generation successful!")


########################################################################
###                          EXTRACT FRAMES                          ###
########################################################################
# TODO: alternativa pt scriere fizica de fisiere (ca nu e eficienta)
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

    print("Frame extraction successful!")


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
        kernel = numpy.ones((3, 3), numpy.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Anti-alias the mask -- blur then stretch
        # Blur alpha channel
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT)

        # Linear stretch so that 127.5 goes to 0, but 255 stays 255
        mask = (2 * (mask.astype(numpy.float32)) - 255.0).clip(0, 255).astype(numpy.uint8)

        # Put mask into alpha channel
        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask

        cv2.imwrite(f"{img_path[:-4]}.png", result)
        os.remove(img_path)

    print("Frame background removal successful!")


########################################################################
###                     GENERATE GIF WITH BACKGROUND                 ###
########################################################################
def overlap_gif_on_background(foreground, background, size, offset):
    for current_frame in foreground:
        current_background = background.copy()
        current_foreground = current_frame.convert(mode="RGBA").resize(size)
        current_background.alpha_composite(current_foreground, dest=offset)
        yield current_background


def generate_gif_with_background(fg_frames_dir_path, bg_image_path, frames_count):
    images = []

    for frame in range(frames_count):
        images.append(Image.open(f"{fg_frames_dir_path}/frame%02d.png" % frame))

    bg_image = Image.open(bg_image_path).convert(mode="RGBA")

    frames = tuple(overlap_gif_on_background(images, bg_image, (300, 300), (100, 200)))
    frames[0].save(f'{fg_frames_dir_path[:-7]}.gif', save_all=True, append_images=frames[1:], loop=0, duration=30)

    print("GIF overlap on background successful!")


########################################################################
###                    GENERATE GIF WITH ONLY TEXT                   ###
########################################################################
def create_image_with_text(text, font, color, offset):
    x, y = offset

    img = Image.new('RGBA', (400, 400))
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=color)
    return img


def create_text_animation_frames(text, font, color, offset):
    x, y = offset
    frames = []

    for i in range(len(text) + 20):
        if i < len(text):
            new_frame = create_image_with_text(text[:i], font, color, (x, y))
        else:
            new_frame = create_image_with_text(text, font, color, (x, y))
        frames.append(new_frame)

    return frames


########################################################################
###                GENERATE GIF WITH TEXT AND ANIMATION              ###
########################################################################
def generate_gif_with_text(text, bg_frames_dir_path):
    frames_bg = []
    frames_fg = create_text_animation_frames(text, ImageFont.truetype('arial', 20), "black", (0, 0))

    for frame in range(Image.open(f"{bg_frames_dir_path[:-7]}.gif").n_frames):
        frames_bg.append(Image.open(f"{bg_frames_dir_path}/frame%02d.jpg" % frame).convert("RGBA"))

    longest = len(frames_fg) if len(frames_fg) > len(frames_bg) else len(frames_bg)

    results = []

    for i in range(longest):
        i_bg = i % len(frames_bg)
        i_fg = i % len(frames_fg)

        bg = frames_bg[i_bg].copy()
        fg = frames_fg[i_fg].copy()

        bg.alpha_composite(fg, (0, 0))
        results.append(bg)

    results[0].save(f"{bg_frames_dir_path[:-7]}.gif", save_all=True, append_images=results[1:], loop=0, duration=30)


########################################################################


if __name__ == "__main__":
    # Create 2 variables and input them from keyboard
    phrase = input("Enter the sentence: ").split(". ")

    gifs = []

    for sentence in phrase:
        is_text_given = False
        say_verb = "spune"

        # If the 'say' verb is parsed, split the given story from the character's dialogue
        if say_verb in sentence:
            is_text_given = True
            sentence, text = sentence.split(": ")

        # Split the words from the story part
        sentence = sentence.split()

        # Read the characters and actions JSONs and parse their data
        characters_data = get_files_data("characters.json")
        actions_data = get_files_data("actions.json")
        places_data = get_files_data("places.json")

        # Make a variable for the driving image and store in it the "file" attribute from the given character
        image = get_character(sentence, characters_data)
        # Make a variable for the driving video and store in it the corresponding file attribute
        # depending on the noun's "type" attribute
        video = get_action(sentence, characters_data, actions_data)

        # Make a variable for an optional background image
        place = get_place(sentence, places_data)

        is_place_given = place is not None

        # Generate a name for the result file with given character and action separated by "_"
        result = f"{sentence[0]}-{sentence[1]}-{sentence[2]}.gif" if is_place_given\
            else f"{sentence[0]}-{sentence[1]}.gif"

        # Generate the demo using the created variables for files names inputs
        exec_terminal_command(30, image, video, result)

        # If there is a place given, generate background
        if is_place_given:
            # Get the resulted GIF as input and remove its white background
            extract_frames(f"results/{result}")
            remove_backgrounds(f"results/{result[:-4]}-frames")

            # Create a new GIF and overlap it on the background image
            frames_count = Image.open(f"results/{result}").n_frames

            generate_gif_with_background(f"results/{result[:-4]}-frames", f"cartoon_env/{place}", frames_count)
            shutil.rmtree(f"results/{result[:-4]}-frames")

        # If the 'say' verb is parsed, animate character dialogue
        if is_text_given:
            # Get the resulted GIF as input
            extract_frames(f"results/{result}")
            gifs.append(f"results/{result}")

            # Create a new GIF with text and overlap it on the old GIF without text
            generate_gif_with_text(text, f"results/{result[:-4]}-frames")
            shutil.rmtree(f"results/{result[:-4]}-frames")

    if len(phrase) > 1:
        frames = []

        for gif in gifs:
            extract_frames(gif)

            for frame in range(Image.open(gif).n_frames):
                frames.append(Image.open(f"{gif[:-4]}-frames/frame%02d.jpg" % frame))

        frames[0].save('results/result.gif', save_all=True, append_images=frames[1:], loop=0, duration=30)

        for gif in gifs:
            shutil.rmtree(f"{gif[:-4]}-frames")
