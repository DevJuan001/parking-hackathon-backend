def plate_formatter(plate: str):
    return plate.replace("-", "").replace(" ", "").strip().upper()