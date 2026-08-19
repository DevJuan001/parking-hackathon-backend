from app.core.database import get_connection
from app.features.entries.repositories.entries_repository import EntriesRepository
from app.features.floors.repositories.floors_repository import FloorsRepository
from app.features.parking.repositories.vehicle_types_repository import (
    VehicleTypesRepository,
)
from app.features.parking.services.parking_service import ParkingService
from app.features.payments.repositories.payments_repository import PaymentsRepository
from app.features.spots.repositories.spots_repository import SpotsRepository
from app.features.tariffs.repositories.tariffs_repository import TariffsRepository
from app.utils.logger import get_logger

logger = get_logger("chatbot.context_builder")


class ContextBuilder:

    @staticmethod
    def build_snapshot(parking_id: str, role: str = "Admin") -> str:
        connection = get_connection()

        if not connection:
            return "No se pudo establecer conexión con la base de datos."

        try:
            error, parking = ParkingService.get_parking_by_id(parking_id)

            if error or not parking:
                return "No se pudo consultar el estado del estacionamiento."

            parts = [
                f"Estacionamiento: {parking.name}",
                f"Dirección: {parking.address}",
            ]

            error, floors = FloorsRepository.find_all_floors(parking_id, connection)

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            parts.append(f"Total de pisos: {len(floors)}")

            error, total_spots = SpotsRepository.count_total_spots(
                parking_id, connection
            )

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            occupied_spots = 0

            for floor in floors:
                err, count = SpotsRepository.count_occupied_spots_by_floor(
                    parking_id, floor.id, connection
                )

                if err:
                    return "No se pudo consultar el estado del estacionamiento."

                occupied_spots += count

            parts.append(f"Total de plazas: {total_spots}")
            parts.append(f"Plazas ocupadas: {occupied_spots}")

            error, active_entries = EntriesRepository.count_active_entries(
                parking_id, connection
            )

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            parts.append(f"Ingresos activos: {active_entries}")

            error, tariffs = TariffsRepository.find_all_tariffs(
                parking_id, connection
            )

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            error, vehicle_types = VehicleTypesRepository.find_all_vehicle_types(
                connection
            )

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            vt_by_id = {vt.id: vt.name for vt in vehicle_types}

            if tariffs:
                tariff_parts = [
                    f"{vt_by_id.get(t.vehicle_type, str(t.vehicle_type))}: ${t.value:.2f}"
                    for t in tariffs
                ]
                parts.append("Tarifas: " + " | ".join(tariff_parts))

            if total_spots > 100:
                parts.append(
                    "Plazas por piso: [más de 100, consulta list_spots para verlas]"
                )
            else:
                error, floors_with_spots = FloorsRepository.find_all_floors_with_spots(
                    parking_id, connection
                )

                if error:
                    return "No se pudo consultar el estado del estacionamiento."

                if floors_with_spots:
                    floor_lines = [
                        f"{name}: {', '.join(str(s) for s in spots)}"
                        for _, name, spots in floors_with_spots
                    ]
                    parts.append("Plazas: " + " | ".join(floor_lines))

            if role == "Admin":
                error, pay_stats = PaymentsRepository.sum_payment_stats(
                    parking_id, connection
                )

                if not error and pay_stats is not None:
                    parts.append(
                        f"Pagos de hoy (recaudación): ${pay_stats['today']:.2f}"
                    )

            if not parts:
                return "No se encontró información para este estacionamiento."

            return " | ".join(parts)

        except Exception:
            logger.exception("Error al construir el snapshot del parking")
            return "No se pudo obtener el estado actual del estacionamiento."

        finally:
            connection.close()