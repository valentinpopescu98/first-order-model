from PIL import Image
from PIL import ImageSequence

def overlap(foreground, background, size, offset):
    for frame in range(foreground.n_frames):
        foreground.seek(frame)
        foreground.show()

    # for current_frame in ImageSequence.Iterator(foreground):
    #     current_background = background.copy()
    #     current_foreground = current_frame.convert(mode="RGBA").resize(size)
    #     current_background.alpha_composite(current_foreground, dest=offset)
    #     yield current_background

fg_animation = Image.open("results/alearga.gif")
bg_image = Image.open("cartoon_env/forest.jpg").convert(mode="RGBA")

# frames = tuple(overlap(fg_animation, bg_image, (100, 100), (220, 25)))
overlap(fg_animation, bg_image, (100, 100), (220, 25))

# frames[0].save("results/output.gif", save_all=True, append_images=frames[1:], duration=30, loop=0)
