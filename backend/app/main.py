from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.components import Storage
import uvicorn
from app.ai.ssd_recommender import recommend_best_disc

app = FastAPI(title="PC Builder API")

@app.get("/")
def health_check():
    return {"Message": "msg check"}

@app.get("/api/disc")
def get_discs(db: Session = Depends(get_db)):
    discs = db.query(Storage).all()
    return discs

@app.get("/api/recommend-ssd")
def get_ssd_recommendation(db: Session = Depends(get_db)):
    best_disc = recommend_best_disc(db)
    return best_disc

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)