import hashlib

def file_MD5(image_path):

    # 创建 MD5 哈希对象
    md5 = hashlib.md5()

    md5.update(image_path.encode('utf-8'))

    result = md5.hexdigest()

    return result
