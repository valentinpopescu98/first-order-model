from PIL import Image

images = []

# def gen_frame(path):
#     im = Image.open(path)
#     alpha = im.getchannel('A')
#
#     # Convert the image into P mode but only use 255 colors in the palette out of 256
#     im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
#
#     # Set all pixel values below 128 to 255 , and the rest to 0
#     mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
#
#     # Paste the color of index 255 and use alpha as a mask
#     im.paste(255, mask)
#
#     # The transparency index is 255
#     im.info['transparency'] = 255
#
#     return im

def overlap(foreground, background, size, offset):
    for current_frame in foreground:
        current_background = background.copy()
        current_foreground = current_frame.convert(mode="RGBA").resize(size)
        current_background.alpha_composite(current_foreground, dest=offset)
        yield current_background

for frame in range(15):
    images.append(Image.open("results/calul-alearga-frames/frame%02d.png" % frame))
    # images.append(gen_frame("results/calul-alearga-frames/frame%02d.png" % frame))

bg_image = Image.open("cartoon_env/forest.jpg").convert(mode="RGBA")
frames = tuple(overlap(images, bg_image, (100, 100), (220, 25)))

frames[0].save('results/result.gif', save_all=True, append_images=frames[1:], loop=0, duration=30)
