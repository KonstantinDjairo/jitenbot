from bs4 import BeautifulSoup
from PIL import Image
from functools import cache


@cache
def calculate_ratio(path):
    if path.endswith(".svg"):
        ratio = __calculate_svg_ratio(path)
    else:
        ratio = __calculate_bitmap_ratio(path)
    return ratio


@cache
def make_rectangle(path, text, rect_stroke, rect_fill, text_fill):
    svg = __svg_text_rectangle(text, rect_stroke, rect_fill, text_fill)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


@cache
def make_monochrome_fill_rectangle(path, text):
    svg = __svg_masked_rectangle(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


def __calculate_svg_ratio(path):
    with open(path, "r", encoding="utf-8") as f:
        xml = f.read()
    soup = BeautifulSoup(xml, "xml")
    svg = soup.svg
    if svg.has_attr("width") and svg.has_attr("height"):
        width = float(svg.attrs["width"])
        height = float(svg.attrs["height"])
        ratio = width / height
    elif svg.has_attr("viewBox"):
        _, _, width, height = svg.attrs["viewBox"].split(" ")
        ratio = float(width) / float(height)
    else:
        raise Exception(f"Cannot calculate ratio for SVG\n{svg.prettify()}")
    return ratio


def __calculate_bitmap_ratio(path):
    img = Image.open(path)
    img_w = img.size[0]
    img_h = img.size[1]
    ratio = img_w / img_h
    return ratio


def __svg_text_rectangle(text, rect_stroke, rect_fill, text_fill):
    height = 128
    width = len(text) * height
    svg = f"""
<svg lang='ja' width='{width}' height='{height}' viewBox='0 0 {width} {height}'
     xmlns='http://www.w3.org/2000/svg' version='1.1'>
    <rect width='{width}' height='{height}' ry='20' stroke='{rect_stroke}'
          fill='{rect_fill}' stroke-width='8'/>
    <text text-anchor='middle' x='50%' y='50%' dy='.35em'
          font-family='sans-serif' font-size='100px'
          fill='{text_fill}'>{text}</text>
</svg>"""
    return svg.strip()


def __svg_masked_rectangle(text):
    height = 128
    width = len(text) * height
    svg = f"""
<svg lang='ja' width='{width}' height='{height}' viewBox='0 0 {width} {height}'
     xmlns='http://www.w3.org/2000/svg' version='1.1'>
    <mask id='a'>
        <rect width='{width}' height='{height}' fill='white'/>
        <text text-anchor='middle' x='50%' y='50%' dy='.35em'
              font-family='sans-serif' font-size='100px'
              fill='black'>{text}</text>
    </mask>
    <rect width='{width}' height='{height}' ry='20'
          fill='black' mask='url(#a)'/>
</svg>"""
    return svg.strip()
