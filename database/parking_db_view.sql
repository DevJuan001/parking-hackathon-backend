CREATE VIEW vw_parking_summary AS
SELECT
  p.plate AS plate,
  vt.name as vehicle_type,
  en.created_at AS entry_time,
  ex.created_at AS exit_time,
  TIMEDIFF(ex.created_at, en.created_at) AS time_parked,
  pay.value AS payment_value
  FROM PAYMENTS AS pay
  INNER JOIN PLATES AS p
    ON p.id = pay.plate_id
  INNER JOIN ENTRIES AS en
    ON pay.plate_id = en.plate_id
  INNER JOIN EXITS AS ex
    ON pay.plate_id = ex.plate_id
  LEFT JOIN VEHICLE_TYPES AS vt
    ON vt.id = p.vehicle_type_id
  INNER JOIN RATES AS r
    ON r.vehicle_type_id = vt.id;

SELECT * FROM vw_parking_summary;