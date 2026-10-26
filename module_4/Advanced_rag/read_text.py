
def load_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


text = load_text_file("data/sample.txt")
print(text)
