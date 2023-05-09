from fastapi import HTTPException

from database.dbclient import background_collection, body_collection, cloths_collection, goggles_collection, head_collection, goggles_collection, head_collection

def get_collection(category: str):
    collections = {
        "01Backgrounds": background_collection,
        "02Body": body_collection,
        "03Cloths": cloths_collection,
        "04Goggles": goggles_collection,
        "05Head": head_collection,
    }
    try:
        return collections[category]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid category")
