from PIL import Image, ImageDraw, ImageFont

WIDTH = 1000
HEIGHT = 1000

SCALE = 100
LINE_WIDTH = 3


def draw_path(draw, pathData):
    color, path = pathData[0], pathData[1]
    
    if (len(path) < 2):
        return
    
    real_path = [(int(i[0] * SCALE) + WIDTH / 2, HEIGHT / 2 - int(i[1] * SCALE)) for i in path]

    for i in range(1, len(real_path)):
        draw.line((real_path[i], real_path[i - 1]), fill=color, width=LINE_WIDTH)


def make_plot(planet_radius, paths, saveas):
    image = Image.new('RGBA', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    draw.rectangle(((0, 0), (WIDTH, HEIGHT)), fill=(255, 255, 255))

    real_radius = int(planet_radius * SCALE)
    draw.ellipse((WIDTH / 2 - real_radius, HEIGHT / 2 - real_radius, WIDTH / 2 + real_radius, HEIGHT / 2 + real_radius), width=LINE_WIDTH, fill=(255, 255, 255), outline=(0, 0, 0))

    draw.line(((0, HEIGHT / 2), (WIDTH, HEIGHT / 2)), fill=(0, 0, 0), width=LINE_WIDTH)  
    draw.line(((WIDTH / 2, 0), (WIDTH / 2, HEIGHT)), fill=(0, 0, 0), width=LINE_WIDTH) 

    for i in paths:
        draw_path(draw, i)    

    image.save(saveas)