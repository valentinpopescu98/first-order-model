import os, os.path
from argparse import ArgumentParser
from PIL import Image

# 1. Run next line in console to convert from GIF to MP4 file:
# ffmpeg -r 30 -i drv_video/input.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" drv_video/output.mp4

# 2. Run next line in console to generate a demo:
# python demo.py  --config config/mgif-256.yaml --driving_video drv_video/output.mp4 --source_image src_image/image.png --checkpoint checkpoints/mgif-cpk.pth.tar --result_video results/result.mp4 --relative --adapt_scale

# 3. Run next line in console to generate frames as images:
# python extract-frames.py --inp results/input.mp4

# 4. Run next line in console to generate sprite sheet:
# python spritesheet-generator.py --inp results/inputFrames

def addTransparency(img):
    datas = img.getdata()

    newData = []

    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def generator(args):
    inputFolder = os.path.abspath(f"{args.inp}")
    os.chdir(inputFolder)
    images = [Image.open(x) for x in os.listdir(inputFolder)]
    os.chdir(inputFolder + "\\..\\..")

    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    new_im = addTransparency(new_im)

    new_im.save(f"{args.inp[:-6]}Spritesheet.png", "PNG")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--inp", required=True, help='Input sprites folder')
    args = parser.parse_args()

    generator(args)
    print("Successful")