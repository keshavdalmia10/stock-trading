import base64

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def create_image_url(imageUrl):
  encodedImage = encode_image(imageUrl)
  return f"data:image/png;base64,{encodedImage}"