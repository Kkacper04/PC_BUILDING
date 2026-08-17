from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.components import Storage
import uvicorn



app = FastAPI(title="PC Builder API")
@app.get("/")
def strona_glowna():
    return {"Message": "msg check"}

@app.get("/api/disc")
def download_discs(db: Session = Depends(get_db)):
   
    discs = db.query(Storage).all()
    return discs


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)