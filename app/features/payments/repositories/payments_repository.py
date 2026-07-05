from datetime import datetime
from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.payments.models.payments_responses import PaymentResponse, PaymentMethodResponse

logger = get_logger("payments.repository")


class PaymentsRepository:

    @staticmethod
    def find_all_payments(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            pay.id,
            p.plate,
            s.spot,
            pay.value,
            pay.created_at,
            pay.payment_method_id
        FROM PAYMENTS AS pay
        INNER JOIN PLATES AS p ON p.id = pay.plate_id
        INNER JOIN SPOTS  AS s ON s.spot_id = pay.spot_id
        WHERE pay.parking_id = %s
        ORDER BY pay.created_at DESC
        """

        try:
            cursor.execute(query, (parking_id,))
            results = cursor.fetchall()

            payments = [
                PaymentResponse(
                    id=item[0],
                    plate=item[1],
                    spot=item[2],
                    value=item[3],
                    created_at=date_formatter(item[4]),
                    payment_method=item[5]
                )
                for item in results
            ]
            return None, payments

        except Exception as e:
            logger.error("Error en find_all_payments: %s", e, exc_info=True)
            return "Error al intentar obtener los pagos", None

        finally:
            cursor.close()

    @staticmethod
    def find_payment_by_id(parking_id: int, payment_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            pay.id,
            p.plate,
            s.spot,
            pay.value,
            pay.created_at,
            pay.payment_method_id
        FROM PAYMENTS AS pay
        INNER JOIN PLATES AS p ON p.id = pay.plate_id
        INNER JOIN SPOTS  AS s ON s.spot_id = pay.spot_id
        WHERE pay.parking_id = %s AND pay.id = %s
        """

        try:
            cursor.execute(query, (parking_id, payment_id))
            result = cursor.fetchone()

            if not result:
                return "Pago no encontrado", None

            payment = PaymentResponse(
                id=result[0],
                plate=result[1],
                spot=result[2],
                value=result[3],
                created_at=date_formatter(result[4]),
                payment_method=result[5]
            )
            return None, payment

        except Exception as e:
            logger.error("Error en find_payment_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener el pago", None

        finally:
            cursor.close()

    @staticmethod
    def find_payments_by_plate(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            pay.id,
            p.plate,
            s.spot,
            pay.value,
            pay.created_at,
            pay.payment_method_id
        FROM PAYMENTS AS pay
        INNER JOIN PLATES AS p ON p.id = pay.plate_id
        INNER JOIN SPOTS  AS s ON s.spot_id = pay.spot_id
        WHERE pay.parking_id = %s AND pay.plate_id = %s
        ORDER BY pay.created_at DESC
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            results = cursor.fetchall()

            payments = [
                PaymentResponse(
                    id=item[0],
                    plate=item[1],
                    spot=item[2],
                    value=item[3],
                    created_at=date_formatter(item[4]),
                    payment_method=item[5]
                )
                for item in results
            ]
            return None, payments

        except Exception as e:
            logger.error(
                "Error en find_payments_by_plate: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los pagos de la placa", None

        finally:
            cursor.close()

    @staticmethod
    def create_payment(parking_id: int, plate_id: int, spot_id: int, value: float, payment_method_id: str, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO PAYMENTS (parking_id, plate_id, spot_id, value, payment_method_id)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query, (
                    parking_id,
                    plate_id,
                    spot_id,
                    value,
                    payment_method_id
                )
            )
            return None, True, "Pago registrado correctamente"

        except Exception as e:
            logger.error("Error en create_payment: %s", e, exc_info=True)
            return "Error al intentar registrar el pago", False, None

        finally:
            cursor.close()

    @staticmethod
    def find_all_payment_methods(connection):
        cursor = connection.cursor()

        query = """
        SELECT id, name, icon
        FROM PAYMENT_METHODS
        ORDER BY id ASC
        """

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            methods = [
                PaymentMethodResponse(
                    id=item[0],
                    name=item[1],
                    icon=item[2]
                )
                for item in results
            ]
            return None, methods

        except Exception as e:
            logger.error(
                "Error en find_all_payment_methods: %s", e, exc_info=True
            )
            return "Error al intentar obtener los metodos de pago", None

        finally:
            cursor.close()

    @staticmethod
    def sum_payment_stats(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            COALESCE(SUM(value), 0) AS total,
            COALESCE(SUM(CASE WHEN DATE(p.created_at) = CURDATE() THEN value ELSE 0 END), 0) AS today,
            COALESCE(SUM(CASE WHEN p.created_at >= (NOW() - INTERVAL 7 DAY) THEN value ELSE 0 END), 0) AS this_week,
            COALESCE(
                SUM(
                    CASE WHEN YEAR(p.created_at) = YEAR(CURDATE())
                              AND MONTH(p.created_at) = MONTH(CURDATE())
                         THEN value ELSE 0 END
                ), 0
            ) AS this_month
        FROM PAYMENTS AS p
        WHERE p.parking_id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            result = cursor.fetchone()

            return None, {
                "total": float(result[0] or 0),
                "today": float(result[1] or 0),
                "this_week": float(result[2] or 0),
                "this_month": float(result[3] or 0)
            }

        except Exception as e:
            logger.error("Error en sum_payment_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadisticas de pagos", None

        finally:
            cursor.close()
