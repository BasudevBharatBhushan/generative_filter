from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from database.dbclient import  generated_images_collection
from bson.binary import Binary
from typing import List
from bson import ObjectId
from api.methods import get_collection
from scripts.generate_image import blend_image
from typing import Optional
from utils.logging import logging
import base64
import json

app = APIRouter()


# Routes
@app.post("/images/{category}")
async def upload_images(images: List[UploadFile] = File(...), category: str = None):

    try:
        collection = get_collection(category)
        
        for image in images:
            contents = await image.read()
            db_image = {
                'name': image.filename,
                'data': Binary(contents)
            }
            collection.insert_one(db_image)
        return {"message": "Images uploaded successfully."}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/images/{category}")
async def get_images(category: str = None, skip: int = 0, next: int = 4):
    try:
        collection = get_collection(category)

        images = collection.find({}).skip(skip).limit(next)
        if images is None:
            raise HTTPException(status_code=404, detail="No images found")
        response_images = []
        for image in images:
            response_images.append({
                "id": str(image.get("_id")),
                "name": image["name"],
                "data": str(base64.b64encode(image["data"]), 'utf-8')
            })
        return {"images": response_images}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.get("/images/{category}/{image_id}")
async def get_image(image_id: str, category: str = None):
    try:
        collection = get_collection(category)
        db_image = collection.find_one({'_id': ObjectId(image_id)})
        if db_image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        filename = db_image['name']
        contents = str(base64.b64encode(db_image['data']), 'utf-8')
        return {"id": str(db_image.get("_id")), "name": filename, "data": contents}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/generate-image")
async def generate_image(ids: dict):
    try:
        background_id = ids.get("background_id")
        body_id = ids.get("body_id")
        cloths_id = ids.get("cloths_id")
        goggles_id = ids.get("goggles_id")
        head_id = ids.get("head_id")

        existing_image = generated_images_collection.find_one({
            "blended_images.01Backgrounds.id": background_id,
            "blended_images.02Body.id": body_id,
            "blended_images.03Cloths.id": cloths_id,
            "blended_images.04Goggles.id": goggles_id,
            "blended_images.05Head.id": head_id
        })

        if existing_image is not None:
            logging.info("Image already exists in the database")
            return {
                "id": str(existing_image.get("_id")),
                "name": existing_image.get("name"),
                "blended_images": existing_image.get("blended_images"),
                "data": existing_image.get("data")
            }

        # Blend the images
        blended_image = await blend_image(background_id, body_id, cloths_id, goggles_id, head_id)

        blended_image_pattern = blended_image.get("blended_images")
        blended_image_data = blended_image.get("data")

        return {
            "name": "generated_image",
            "blended_images": blended_image_pattern,
            "data": str(base64.b64encode(blended_image_data), 'utf-8')
        }

    except Exception as e:
        logging.error(f"Failed to generate image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/save-data")
async def save_data(data: dict):
    try:
        blended_images = data.get("blended_images")
        if blended_images is None:
            raise HTTPException(status_code=400, detail="Invalid request: blended_images field is missing")

        # Check if the blended images already exist in the database
        existing_image = generated_images_collection.find_one({
            "blended_images.01Backgrounds.id": blended_images.get("01Backgrounds", {}).get("id"),
            "blended_images.02Body.id": blended_images.get("02Body", {}).get("id"),
            "blended_images.03Cloths.id": blended_images.get("03Cloths", {}).get("id"),
            "blended_images.04Goggles.id": blended_images.get("04Goggles", {}).get("id"),
            "blended_images.05Head.id": blended_images.get("05Head", {}).get("id")
        })

        if existing_image is not None:
            logging.info("Image already exists in the database")
            return {
                "id": str(existing_image.get("_id")),
                "name": existing_image.get("name"),
                "blended_images": existing_image.get("blended_images"),
                "data": data.get("data")
            }

        # Save the data in the database
        result = generated_images_collection.insert_one(data)

        # Retrieve the inserted document ID
        document_id = str(result.inserted_id)

        # Add the ID to the JSON data
        data["_id"] = document_id

        return {
            "id": data.get("_id"),
            "name": data.get("name"),
            "blended_images": data.get("blended_images"),
            "data": data.get("data")
        }

    except Exception as e:
        logging.error(f"Failed to save data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.get("/generated-image/all")
async def get_all_generated_image(skip: int = 0, next: int = 4):
    try:
        generated_images = generated_images_collection.find({}).skip(skip).limit(next)
        if generated_images is None:
            raise HTTPException(status_code=404, detail="No images found")
        response_images = []
        for image in generated_images:
            response_images.append({
                "id": str(image.get("_id")),
                "name": image.get("name"),
                "blended_images": image.get("blended_images"),
                "data": str(base64.b64encode(image.get("data")), 'utf-8')
            })
        return {"images": response_images}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/generated-image/{image_id}")
async def get_generated_image(image_id: str):
    try:
        generated_image = generated_images_collection.find_one({'_id': ObjectId(image_id)})
        if generated_image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        filename = generated_image['name']
        contents = str(base64.b64encode(generated_image['data']), 'utf-8')
        return {"id": str(generated_image.get("_id")), "name": filename, "blended_images": generated_image.get("blended_images"), "data": contents}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")



