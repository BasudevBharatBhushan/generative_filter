from fastapi import  HTTPException
from PIL import Image
import io
import base64
from api import api
from typing import Optional


async def blend_image(background_id: Optional[str] = None, body_id: Optional[str] = None, clothes_id: Optional[str] = None, goggles_id: Optional[str] = None, head_id: Optional[str] = None):
    try:
        # Fetch the images from the database based on the provided IDs
        images = {
            "01Backgrounds": background_id,
            "02Body": body_id,
            "03Cloths": clothes_id,
            "04Goggles": goggles_id,
            "05Head": head_id
        }

        loaded_images = {}
        loaded_images_data = {}
        for category, image_id in images.items():
            if image_id is not None:
                image_data = await api.get_image(image_id, category)
                if image_data is None:
                    raise HTTPException(status_code=404, detail=f"Image not found for category {category}")
                loaded_images[category] = {
                    "id": image_id,
                    "name": image_data.get("name"),
                }
                loaded_images_data[category]={
                    "data":image_data.get("data"),  # base64 encoded image data
                }


        # Check if any images are loaded
        if len(loaded_images) == 0:
            raise HTTPException(status_code=400, detail="No valid image IDs provided")

        # # Load the images and blend them together
        blended_img = None
        for category, image_data in loaded_images_data.items():
            img = Image.open(io.BytesIO(base64.b64decode(image_data.get('data')))).convert('RGBA')
            if blended_img is None:
                blended_img = img
            else:
                blended_img = Image.alpha_composite(blended_img, img)

        # # Save the blended image to a new file
        with io.BytesIO() as buffer:
            blended_img.save(buffer, format='PNG')
            data = buffer.getvalue()


        blended_img.save("new.png", format="png")
        # # Return the blended data along with the loaded image names

        return {
            "blended_images": loaded_images,
            "data": data
        }

    except:
        raise HTTPException(status_code=500, detail="Internal server error")
