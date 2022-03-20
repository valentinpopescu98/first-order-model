import subprocess
import json

def get_files_data(file):
    file = open(file)
    data = json.load(file)
    file.close()

    return data

def get_demo_src_image():
    image = charactersData[words[0]]["file"]

    return image

def get_demo_drv_video():
    if (charactersData[words[0]]["type"] == "humanoid"):
        video = actionsData[words[1]]["file_for_humanoid"]
    elif (charactersData[words[0]]["type"] == "quadruped"):
        video = actionsData[words[1]]["file_for_quadruped"]

    return video

def exec_terminal_command(fps, image, video, result):
    subprocess.run([
        "python", "demo.py", "--fps", f"{fps}", "--config", "config/mgif-256.yaml", "--driving_video", f"drv_video/{video}",
        "--source_image", f"src_image/{image}", "--checkpoint", "checkpoints/mgif-cpk.pth.tar", "--result_video",
        f"results/{result}", "--relative", "--adapt_scale"
    ], shell=True)

if __name__ == "__main__":
    # Create 2 variables and input them from keyboard
    words = input("Enter the sentence: ").split()

    # Read the characters and actions JSONs and parse their data
    charactersData = get_files_data("characters.json")
    actionsData = get_files_data("actions.json")

    # Make a variable for the driving image and store in it the "file" attribute from the given character
    image = get_demo_src_image()
    # Make a variable for the driving video and store in it the corresponding file attribute
    # depending on the noun's "type" attribute
    video = get_demo_drv_video()

    # Generate a name for the result file with given character and action separated by "_"
    result = f"{words[0]}-{words[1]}.gif"

    # Generate the demo using the created variables for files names inputs
    exec_terminal_command(15, image, video, result)