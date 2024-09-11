import hashlib

def file_sha1(file_path):

    # 以二进制方式打开文件
    with open(file_path, "rb") as f:
        # 创建 SHA-1 哈希对象
        sha1 = hashlib.sha1()

        # 逐块读取文件并更新哈希对象
        while True:
            # 读取文件块
            data = f.read(4096)
            if not data:
                break
            # 更新哈希对象
            sha1.update(data)

    # 获取并返回最终的哈希值（以十六进制表示）
    return sha1.hexdigest()

def file_sha256(file_path):

    # 以二进制方式打开文件
    with open(file_path, "rb") as f:
        # 创建 SHA-256 哈希对象
        sha256 = hashlib.sha256()

        # 逐块读取文件并更新哈希对象
        while True:
            # 读取文件块
            data = f.read(4096)
            if not data:
                break
            # 更新哈希对象
            sha256.update(data)

    # 获取并返回最终的哈希值（以十六进制表示）
    return sha256.hexdigest()

def file_sha512(filepath):

    with open(filepath, "rb") as f:
        # 创建 SHA-256 哈希对象
        sha256 = hashlib.sha512()

        # 逐块读取文件并更新哈希对象
        while True:
            # 读取文件块
            data = f.read(4096)
            if not data:
                break
            # 更新哈希对象
            sha256.update(data)

    # 获取并返回最终的哈希值（以十六进制表示）
    return sha256.hexdigest()