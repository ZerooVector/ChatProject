from PIL import Image

def get_image_size(image_path):
    # Open an image using PIL (Python Imaging Library)
    image = Image.open(image_path)
    
    # Get the dimensions of the image
    width, height = image.size
    
    return width, height

# Sample usage
image_path = "E:/2023-2024 # 1(now)/finaltest/client_Trial/image.jpg"  # Replace this with the path to your image
width, height = get_image_size(image_path)
print(f"The size of the image is {width} x {height}.")