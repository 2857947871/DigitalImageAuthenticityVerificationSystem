import struct

def get_jpeg_quality_from_quantization_table(image_path):

    def read_marker_length(file):
        return struct.unpack(">H", file.read(2))[0]
    
    def read_quantization_table(file, length):
        # The length includes the two bytes of the length field itself, so subtract 2
        data = file.read(length - 2)
        # Extract the quantization table
        precision_and_identifier = data[0]
        precision = precision_and_identifier >> 4
        identifier = precision_and_identifier & 0x0F
        if precision == 0:
            quant_table = list(data[1:65])  # 8x8 table with 1-byte values
        else:
            quant_table = list(data[1:129])  # 8x8 table with 2-byte values
        return quant_table

    with open(image_path, 'rb') as f:
        # Check the JPEG file's SOI marker (Start of Image)
        try:
            if f.read(2) != b'\xFF\xD8':
                raise ValueError("Not a valid JPEG file")

            while True:
                marker, = struct.unpack(">H", f.read(2))
                length = read_marker_length(f)
                
                if marker == 0xFFDB:  # DQT (Define Quantization Table)
                    quant_table = read_quantization_table(f, length)
                    # Using the method from jpeg-archive to estimate quality factor
                    quality = estimate_quality_factor(quant_table)
                    return quality
                else:
                    # Skip over other markers
                    f.seek(length - 2, 1)
            return None
        except:
            return None
def estimate_quality_factor(quant_table):

    # This function provides an estimation of the JPEG quality factor
    # based on the quantization table using a heuristic method.
    # This method is derived from jpeg-archive.
    quality = 0
    for q in quant_table:
        quality += q
    quality = quality / len(quant_table)
    return quality

if __name__ == "__main__":

    image_path = "tools/00006_fake.jpg"
    get_jpeg_quality_from_quantization_table(image_path)
