import torch
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.components import Storage

def recommend_best_disc(db: Session):
    discs = db.query(Storage).all()

    if not discs:
        return "No discs available in database"

    features = [
        [
            float(d.price or 9999.0), 
            float(d.capacity_gb or 1.0), 
            float(d.read_speed_mbps or 1.0)
        ]
        for d in discs
    ]
    feature_tensor = torch.tensor(features,dtype=torch.float32)
    #slicing
    price_tensor = feature_tensor[:,0]
    capacity_tensor = feature_tensor[:,1]
    read_speed_tensor = feature_tensor[:,2]

    norm_price = (price_tensor - price_tensor.min()) / (price_tensor.max() - price_tensor.min() + 1e-5)
    norm_capacity = (capacity_tensor - capacity_tensor.min()) / (capacity_tensor.max() - capacity_tensor.min() + 1e-5)
    norm_read_speed = (read_speed_tensor - read_speed_tensor.min()) / (read_speed_tensor.max() - read_speed_tensor.min() + 1e-5)
    #lower price means more points
    points = (1.0 - norm_price) * 0.5 + (norm_capacity) * 0.3 + (norm_read_speed) * 0.2

    winner_idx = torch.argmax(points).item()
    best_disc = discs[winner_idx]

    print("RECOMMENDED SSD ")
    print(f"Model: {best_disc.name}")
    print(f"Price: {best_disc.price} PLN")
    print(f"Capacity: {best_disc.capacity_gb} GB")
    print(f"Speed: {best_disc.read_speed_mbps} MB/s")
    print(f"Score: {points[winner_idx].item():.4f} / 1.000")
    
    return best_disc


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    gen = get_db()
    db = next(gen)
    
    recommend_best_disc(db)