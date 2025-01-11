import rembg
import numpy as np
from PIL import Image
from io import BytesIO

def process_image(photo_bytes):

    input_image = Image.open(BytesIO(photo_bytes))
    input_array = np.array(input_image)
    output_array = rembg.remove(input_array)
    output_image = Image.fromarray(output_array)

    output_buffer = BytesIO()
    output_image.save(output_buffer, format='png')
    output_buffer.seek(0)

    return output_buffer
