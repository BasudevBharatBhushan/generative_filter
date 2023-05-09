from fastapi import  HTTPException
from PIL import Image
import io
import base64
from api import api


async def blend_image(background_id: str, body_id: str, clothes_id: str, goggles_id: str, head_id: str):
    try:
        # Fetch the images from the database
        background_data = await api.get_image(background_id, "01Backgrounds")
        body_data = await api.get_image(body_id, "02Body")
        clothes_data = await api.get_image(clothes_id, "03Cloths")
        goggles_data = await api.get_image(goggles_id, "04Goggles")
        head_data = await api.get_image(head_id, "05Head")

        # Check if any image is missing
        if background_data is None or body_data is None or clothes_data is None or goggles_data is None or head_data is None:
            raise HTTPException(status_code=404, detail="One or more images not found")

        # Load the images
        img1 = Image.open(io.BytesIO(base64.b64decode(background_data.get('data')))).convert("RGBA")
        img2 = Image.open(io.BytesIO(base64.b64decode(body_data.get('data')))).convert('RGBA')
        img3 = Image.open(io.BytesIO(base64.b64decode(clothes_data.get('data')))).convert('RGBA')
        img4 = Image.open(io.BytesIO(base64.b64decode(goggles_data.get('data')))).convert('RGBA')
        img5 = Image.open(io.BytesIO(base64.b64decode(head_data.get('data')))).convert('RGBA')

        # Blend the images together
        blended_img = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(img1, img2), img3), img4), img5)

        # Save the blended image to a new file
        with io.BytesIO() as buffer:
            blended_img.save(buffer, format='PNG')
            data = buffer.getvalue()

        # Return the blended data along with the image names
        return {
            "blended_images": {
                "01Backgrounds": {
                    "id": background_id,
                    "name": background_data.get("name")
                },
                "02Body": {
                    "id": body_id,
                    "name": body_data.get("name")
                },
                "03Cloths": {
                    "id": clothes_id,
                    "name": clothes_data.get("name")
                },
                "04Goggles": {
                    "id": goggles_id,
                    "name": goggles_data.get("name")
                },
                "05Head": {
                    "id": head_id,
                    "name": head_data.get("name")
                }
            },
            "data": data
        }
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

