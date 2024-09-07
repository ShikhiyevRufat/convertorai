from PIL import Image, UnidentifiedImageError
import io

allowed_input_formats = ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'avif', 'webp']
allowed_output_formats = ['png', 'jpg', 'jpeg', 'gif', 'tiff', 'pdf', 'avif', 'webp']

def convert_image(input_image, output_image, output_format):
    try:
        img = Image.open(input_image)
        file_extension = img.format.lower()
        if file_extension not in allowed_input_formats:
            return f"The file format .{file_extension} is not supported."

        if output_format.lower() not in allowed_output_formats:
            return f"Unsupported output format. Supported formats are: {allowed_output_formats}"

        output_format_upper = output_format.upper()

        if output_format_upper == 'GIF':
            img = img.convert("RGB")
            img.save(output_image, format='GIF', save_all=True, duration=200, loop=0)
        elif output_format_upper == 'TIFF':
            img = img.convert("RGB")
            img.save(output_image, format='TIFF')
        elif output_format_upper == 'PDF':
            img = img.convert("RGB")
            img.save(output_image, format='PDF')
        elif output_format_upper in ['JPEG', 'JPG']:
            if img.mode in ['RGBA', 'LA'] or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert("RGB")
            img.save(output_image, format='JPEG')
        elif output_format_upper == 'AVIF':
            img.save(output_image, format='AVIF')
        else:
            img.save(output_image, format=output_format_upper)

        return None
    except UnidentifiedImageError:
        return "Cannot identify image file. Please check the input path."
    except Exception as e:
        return f"An error occurred: {e}"
