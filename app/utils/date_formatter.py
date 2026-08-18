from datetime import datetime, date, time

MONTHS_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def date_formatter(date_str):
    if isinstance(date_str, (datetime, date)):
        dt = date_str
    elif isinstance(date_str, str):
        dt = datetime.fromisoformat(date_str)
    else:
        raise TypeError(f"date_formatter: tipo no soportado: {type(date_str)}")

    mes = MONTHS_ES[dt.month]
    return f"{mes} {dt.day:02d} {dt.year}"


def time_to_12h(time_value):
    if isinstance(time_value, datetime):
        hour, minutes = time_value.hour, time_value.minute

    elif isinstance(time_value, time):
        hour, minutes = time_value.hour, time_value.minute

    elif isinstance(time_value, str):
        parts = time_value.strip().split(":")
        hour, minutes = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0

    else:
        raise TypeError(f"time_to_12h: tipo no soportado: {type(time_value)}")

    periodo = "A.M." if hour < 12 else "P.M."
    hora_12 = hour % 12 or 12

    return f"{hora_12}:{minutes:02d} {periodo}"
