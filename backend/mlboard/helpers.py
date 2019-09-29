import math
import os
import io

import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFont

from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels


def generate_normalized_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    classes = list(unique_labels(y_true, y_pred))

    image_dim = 800
    fig_dim = 600
    font_size = 120

    image = Image.new("RGB", (image_dim, image_dim), "white")
    draw = ImageDraw.Draw(image)

    cell_size = fig_dim // len(classes)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            shade = 255 - int(cm[i][j] * 255)
            offset_y = image_dim - fig_dim
            draw.rectangle(
                [
                    i * cell_size,
                    offset_y + j * cell_size,
                    (i + 1) * cell_size,
                    offset_y + (j + 1) * cell_size,
                ],
                fill=(shade, shade, shade),
            )

    font_path = os.path.join(os.getcwd(), "resources/arial.ttf")
    font = ImageFont.truetype(font_path, font_size)
    for i in range(len(classes)):
        top_offset_y = image_dim - fig_dim - int(font_size * 1.2)
        right_offset_x = fig_dim + int(font_size * 0.2)
        right_offset_y = image_dim - fig_dim + cell_size - font_size
        draw.text((i * cell_size, top_offset_y), str(classes[i]), font=font, fill=0)
        draw.text(
            (right_offset_x, right_offset_y + i * cell_size),
            str(classes[i]),
            font=font,
            fill=0,
        )

    buffer = io.BytesIO()
    image.save(buffer, "PNG")

    return buffer.getvalue()
