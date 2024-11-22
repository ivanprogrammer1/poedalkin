def get_content_file(filepath):
    
    with open(filepath, "rb") as f:
        content = f.read()

    return content
