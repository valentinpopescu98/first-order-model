from PIL import Image, ImageFont, ImageDraw

frames = []
x, y = 0, 0
font = ImageFont.truetype('arial', 20)
string = "Salut fratelo. Ce pula mea mai faci?"

def create_image_with_text(size, text, font):
    width, height = size
    img = Image.new('RGBA', (400, 400))
    draw = ImageDraw.Draw(img)
    draw.text((width, height), text, font=font, fill="white")
    return img

for i in range(len(string)+20):
    if i < len(string):
        new_frame = create_image_with_text((x, y), string[:i], font)
    else:
        new_frame = create_image_with_text((x, y), string, font)
    frames.append(new_frame)

frames[0].save('results/moving_text.gif', save_all=True, append_images=frames[1:], loop=0, duration=30)
