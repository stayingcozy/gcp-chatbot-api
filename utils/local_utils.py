from PIL import Image
from datetime import datetime
from google.genai import types

def generate_image(client): 
    # Generate Image
    img_response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='A photorealistic picture of a dogs healthly teeth and gums.',
        config=types.GenerateImagesConfig(
            negative_prompt='human',
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/jpeg',
        ),
    )

    # Convert binary image data to PIL Image
    image_data = img_response.generated_images[0].image  # This is likely bytes

    # Get current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    # Generate file name with timestamp
    file_name = f"generated_image_{timestamp}.jpg"

    # Save the image to a temporary file
    image_data.save(file_name)

    # Open manually or with an image viewer
    Image.open(file_name).show()

    return img_response