from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory database (replace with a real database in production)
database = {}

class Item(BaseModel):
    item_number: int
    item_name: str
    value: float

@app.post("/items/")
async def create_item(item: Item):
    database[item.item_number] = item
    return {"message": "Item created successfully"}

@app.get("/items/{item_number}")
async def get_item(item_number: int):
    if item_number not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    return database[item_number]

@app.delete("/items/{item_number}")
async def delete_item(item_number: int):
    if item_number not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    del database[item_number]
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)