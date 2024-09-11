from PIL import Image

def count_xmp_fields(image_path):

    with Image.open(image_path) as img:
        xmp_data = img.info.get('XMP')
        xmp_field_count = len(xmp_data) if xmp_data else 0
        
        return xmp_field_count