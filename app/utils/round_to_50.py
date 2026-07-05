from decimal import Decimal, ROUND_UP


def round_up_to_next_50(value: float) -> float:
    """Redondea un valor monetario hacia arriba al siguiente multiplo de 50.

    Regla: si el total es mayor a 0, se cobra al menos 50 y el valor final
    siempre termina en .00 o .50.

    Ejemplos:
        round_up_to_next_50(0)    -> 0
        round_up_to_next_50(1)    -> 50
        round_up_to_next_50(49)   -> 50
        round_up_to_next_50(50)   -> 50
        round_up_to_next_50(51)   -> 100
        round_up_to_next_50(74)   -> 100
        round_up_to_next_50(99)   -> 100
        round_up_to_next_50(100)  -> 100
        round_up_to_next_50(1234) -> 1250
    """
    if value <= 0:
        return 50

    step = Decimal("50")
    value_decimal = Decimal(str(value))

    return float((value_decimal / step).to_integral_value(rounding=ROUND_UP) * step)
