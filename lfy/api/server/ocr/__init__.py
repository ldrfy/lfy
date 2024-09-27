from PIL import Image, ImageDraw, ImageFont


def gen_img(text="success"):
    """生成图片，TODO:这里应该生成需要语言字体的文字，现在有问题

    Args:
        text (str, optional): _description_. Defaults to "success".
    """
    w,h = 256,128
    # 创建一个白色背景的图片 (宽1024px，高1024px)
    img = Image.new('RGB', (w, h), color='white')

    # 创建一个绘图对象
    d = ImageDraw.Draw(img)

    # 使用 Pillow 自带的默认字体
    font = ImageFont.load_default(60)

    # 定义文本
    text = "success"

    # 使用 textbbox 计算文本的边界框，返回 (left, top, right, bottom)
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 将文本居中
    position = ((w - text_width) // 2, (h - text_height) // 2)

    # 在图片上添加文本，设置颜色为绿色
    d.text(position, text, fill=(0, 128, 0), font=font)

    # 保存图片
    path = "/tmp/lfy.png"
    img.save(path)
    return path


if __name__== "__main__":
    img_path = gen_img()

    import pytesseract
    s = pytesseract.image_to_string(img_path, lang="eng")
    print(s)
