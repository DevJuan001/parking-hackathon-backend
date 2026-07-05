from datetime import datetime, date

MESES_ES = {
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

    mes = MESES_ES[dt.month]
    return f"{mes} {dt.day:02d} {dt.year}"
