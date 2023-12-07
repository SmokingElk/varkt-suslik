from PIL import Image, ImageDraw, ImageFont

WIDTH = 1000
HEIGHT = 1000

SCALE = 100 / 2 / 10**5
LINE_WIDTH = 3

MARKS_SIZE = 12
MARKS_COLOR = (0, 220, 106)

FIELD_PADDING = 0.2
FIELD_GRID_COLOR = (230, 230, 230)
FIELD_POINTS_COLORS = [
    (0, 220, 106),
    (220, 194, 0),
    (220,220,220),
]

FONT = ImageFont.truetype('./model_1/resources/roboto.ttf', 25) 

def drawPath(draw, pathData):
    color, path = pathData[0], pathData[1]
    
    if len(path) < 2:
        return
    
    realPath = [(int(i[0] * SCALE) + WIDTH / 2, HEIGHT / 2 - int(i[1] * SCALE)) for i in path]

    for i in range(1, len(realPath)):
        draw.line((realPath[i], realPath[i - 1]), fill=color, width=LINE_WIDTH)


def drawOrbitData(draw, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist, orbitWasReached):
    if not orbitWasReached:
        draw.text((57, HEIGHT - 50), f"Orbit wasn't reached", (0, 0, 0), font=FONT, align="left")    
        return

    apoX = WIDTH / 2 + apocenterPoint[0] * SCALE 
    apoY = HEIGHT / 2 - apocenterPoint[1] * SCALE
    periX = WIDTH / 2 + pericenterPoint[0] * SCALE
    periY = HEIGHT / 2 - pericenterPoint[1] * SCALE
    
    draw.rectangle(((periX - MARKS_SIZE, periY - MARKS_SIZE), (periX + MARKS_SIZE, periY + MARKS_SIZE)), width=LINE_WIDTH, outline=MARKS_COLOR)
    draw.ellipse((apoX - MARKS_SIZE, apoY - MARKS_SIZE, apoX + MARKS_SIZE, apoY + MARKS_SIZE), width=LINE_WIDTH, outline=MARKS_COLOR)

    draw.rectangle(((35 - MARKS_SIZE, HEIGHT - 35 - MARKS_SIZE), (35 + MARKS_SIZE, HEIGHT - 35 + MARKS_SIZE)), width=LINE_WIDTH, outline=MARKS_COLOR)
    draw.ellipse((35 - MARKS_SIZE, HEIGHT - 85 - MARKS_SIZE, 35 + MARKS_SIZE, HEIGHT - 85 + MARKS_SIZE), width=LINE_WIDTH, outline=MARKS_COLOR)

    draw.text((57, HEIGHT - 100), f"Apocenter: {int(apocenterDist)}", (0, 0, 0), font=FONT, align="left")
    draw.text((57, HEIGHT - 50), f"Pericenter: {int(pericenterDist)}", (0, 0, 0), font=FONT, align="left")


def makeOrbitPlot(planet_radius, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist, orbitWasReached, paths, saveas):
    image = Image.new('RGBA', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    draw.rectangle(((0, 0), (WIDTH, HEIGHT)), fill=(255, 255, 255))

    realRadius = int(planet_radius * SCALE)
    draw.ellipse((WIDTH / 2 - realRadius, HEIGHT / 2 - realRadius, WIDTH / 2 + realRadius, HEIGHT / 2 + realRadius), width=LINE_WIDTH, fill=(255, 255, 255), outline=(0, 0, 0))

    draw.line(((0, HEIGHT / 2), (WIDTH, HEIGHT / 2)), fill=(0, 0, 0), width=LINE_WIDTH)  
    draw.line(((WIDTH / 2, 0), (WIDTH / 2, HEIGHT)), fill=(0, 0, 0), width=LINE_WIDTH) 

    for i in paths:
        drawPath(draw, i)    

    drawOrbitData(draw, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist, orbitWasReached)

    image.save(saveas)


def makeFieldPlot(field, fuelMin, fuelMax, payloadMin, payloadMax, saveas):
    image = Image.new('RGBA', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    fieldSize = len(field)
    padding = FIELD_PADDING * WIDTH
    circleRad = (WIDTH - padding * 2) / (fieldSize - 1) / 3

    draw.rectangle(((0, 0), (WIDTH, HEIGHT)), fill=(255, 255, 255))
    
    for i in range(0, fieldSize):
        x = padding + (WIDTH - padding * 2) / (fieldSize - 1) * i
        y = HEIGHT - (padding + (HEIGHT - padding * 2) / (fieldSize - 1) * i)

        draw.line(((x, 0), (x, HEIGHT)), fill=FIELD_GRID_COLOR, width=LINE_WIDTH) 
        draw.line(((0, y), (WIDTH, y)), fill=FIELD_GRID_COLOR, width=LINE_WIDTH)    

    for j in range(0, fieldSize):
        for i in range(0, fieldSize):
            y = HEIGHT - (padding + (HEIGHT - padding * 2) / (fieldSize - 1) * j)
            x = padding + (WIDTH - padding * 2) / (fieldSize - 1) * i

            pointColor = FIELD_POINTS_COLORS[field[j][i]]

            draw.ellipse((x - circleRad, y - circleRad, x + circleRad, y + circleRad), width=LINE_WIDTH, fill=pointColor)

    draw.line(((0, HEIGHT - padding / 2), (WIDTH, HEIGHT - padding / 2)), fill=(0, 0, 0), width=LINE_WIDTH)  
    draw.line(((padding / 2, 0), (padding / 2, HEIGHT)), fill=(0, 0, 0), width=LINE_WIDTH) 

    draw.text((padding / 2 + 10, 20), f"Payload mass", (0, 0, 0), font=FONT, anchor="lt")
    draw.text((WIDTH - 20, HEIGHT - padding / 2 - 10), f"Fuel mass", (0, 0, 0), font=FONT, anchor="rb")

    draw.text((padding, HEIGHT - padding / 2 + 10), f"{fuelMin}", (0, 0, 0), font=FONT, anchor="mt")
    draw.text((WIDTH - padding, HEIGHT - padding / 2 + 10), f"{fuelMax}", (0, 0, 0), font=FONT, anchor="mt")

    draw.text((padding / 2 - 10, HEIGHT - padding), f"{payloadMin}", (0, 0, 0), font=FONT, anchor="rm")
    draw.text((padding / 2 - 10, padding), f"{payloadMax}", (0, 0, 0), font=FONT, anchor="rm")
    
    image.save(saveas)