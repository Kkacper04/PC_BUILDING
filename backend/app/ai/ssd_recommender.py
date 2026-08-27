from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.components import Storage


def _min_max_normalize(values: list[float]) -> list[float]:
    #Min-max normalize a list of floats to [0, 1].
    v_min = min(values)
    v_max = max(values)
    spread = v_max - v_min if v_max != v_min else 1e-5
    return [(v - v_min) / spread for v in values]


def recommend_best_disc(db: Session) -> dict | None:
    """Recommend the best SSD based on value score (price/capacity/speed)."""
    from app.models.enums import StorageType
    
    discs = db.query(Storage).filter(
        Storage.storage_type.in_([StorageType.NVME_SSD, StorageType.SATA_SSD])
    ).all()

    if not discs:
        return None

    prices = [float(d.price or 9999.0) for d in discs]
    capacities = [float(d.capacity_gb or 1.0) for d in discs]
    read_speeds = [float(d.read_speed_mbps or 1.0) for d in discs]

    norm_price = _min_max_normalize(prices)
    norm_capacity = _min_max_normalize(capacities)
    norm_read_speed = _min_max_normalize(read_speeds)

    # Lower price = more points, higher capacity/speed = more points
    scores = [
        (1.0 - np) * 0.5 + nc * 0.3 + ns * 0.2
        for np, nc, ns in zip(norm_price, norm_capacity, norm_read_speed)
    ]

    winner_idx = scores.index(max(scores))
    best_disc = discs[winner_idx]

    result_dict = {
        column.name: getattr(best_disc, column.name)
        for column in best_disc.__table__.columns
    }
    result_dict["value_score"] = round(scores[winner_idx], 4)

    return result_dict


if __name__ == "__main__":
    gen = get_db()
    db = next(gen)
    try:
        recommend_best_disc(db)
    finally:
        gen.close()
