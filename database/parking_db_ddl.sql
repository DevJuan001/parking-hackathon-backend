DROP DATABASE IF EXISTS parking_db;

CREATE DATABASE IF NOT EXISTS parking_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE parking_db;

CREATE TABLE ROLES(
  id INT NOT NULL AUTO_INCREMENT,
  name TEXT NOT NULL,
  PRIMARY KEY(id)
);

CREATE TABLE COUNTRIES (
  id        INT         NOT NULL AUTO_INCREMENT,
  name      TEXT        NOT NULL,
  iso_code  VARCHAR(2)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX uq_countries_iso_code (iso_code)
);

CREATE TABLE PARKINGS (
  id INT NOT NULL AUTO_INCREMENT,
  country_id INT NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id),
  FOREIGN KEY (country_id) REFERENCES COUNTRIES(id),
  INDEX idx_parkings_country_id (country_id)
);

CREATE TABLE USERS (
  role_id INT NOT NULL,
  parking_id INT NULL,
	id INT NOT NULL AUTO_INCREMENT,
  name TEXT NULL,
  first_surname TEXT NULL,
  second_surname TEXT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status INT NOT NULL DEFAULT 2,
  PRIMARY KEY(id),
  FOREIGN KEY (role_id) REFERENCES ROLES(id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id)
);

CREATE TABLE FLOORS (
  id INT NOT NULL AUTO_INCREMENT,
  parking_id INT NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  INDEX idx_floors_parking_id (parking_id)
);

CREATE TABLE VEHICLE_TYPES (
  id          INT       NOT NULL AUTO_INCREMENT,
  name        TEXT      NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE PLATES (
  id               INT          NOT NULL AUTO_INCREMENT,
  parking_id       INT          NOT NULL,
  plate            VARCHAR(6)  NOT NULL,
  vehicle_type_id  INT          NOT NULL,
  created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (vehicle_type_id) REFERENCES VEHICLE_TYPES(id),
  UNIQUE INDEX uq_plates_parking_plate (parking_id, plate),
  INDEX idx_plates_parking_id (parking_id)
);

CREATE TABLE SPOTS (
  spot_id         INT       NOT NULL AUTO_INCREMENT,
  floor_id        INT       NULL,
  spot            TEXT      NOT NULL,
  spot_status     INT       NOT NULL DEFAULT 2 COMMENT '1: deshabilitada, 2: dispnible, 3: ocupado',
  vehicle_type_id INT       NOT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (spot_id),
  FOREIGN KEY (floor_id) REFERENCES FLOORS(id) ON DELETE SET NULL,
  FOREIGN KEY (vehicle_type_id) REFERENCES VEHICLE_TYPES(id),
  INDEX idx_spots_floor_id (floor_id),
  INDEX idx_spots_vehicle_type_id (vehicle_type_id)
);

-- Dependent tables
CREATE TABLE ENTRIES (
  id          INT       NOT NULL AUTO_INCREMENT,
  parking_id  INT       NOT NULL,
  plate_id    INT       NOT NULL,
  spot_id     INT       NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (plate_id) REFERENCES PLATES(id),
  FOREIGN KEY (spot_id)  REFERENCES SPOTS(spot_id) ON DELETE SET NULL,
  INDEX idx_entries_parking_id (parking_id)
);

CREATE TABLE EXITS (
  id          INT       NOT NULL AUTO_INCREMENT,
  parking_id  INT       NOT NULL,
  plate_id    INT       NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (plate_id) REFERENCES PLATES(id),
  INDEX idx_exits_parking_id (parking_id)
);

CREATE TABLE RATES (
  id                INT       NOT NULL AUTO_INCREMENT,
  parking_id        INT       NOT NULL,
  vehicle_type_id   INT      NOT NULL,
  value          FLOAT     NOT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                           ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (vehicle_type_id) REFERENCES VEHICLE_TYPES(id),
  UNIQUE INDEX uq_rates_parking_vehicle_type (parking_id, vehicle_type_id),
  INDEX idx_rates_parking_id (parking_id)
);

CREATE TABLE PAYMENT_METHODS (
  id INT NOT NULL AUTO_INCREMENT,
  name TEXT NOT NULL,
  icon TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);


CREATE TABLE PAYMENTS (
  id          INT       NOT NULL AUTO_INCREMENT,
  parking_id  INT       NOT NULL,
  plate_id    INT       NOT NULL,
  spot_id     INT       NULL,
  value       FLOAT     NOT NULL,
  payment_method_id INT NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (plate_id) REFERENCES PLATES(id),
  FOREIGN KEY (spot_id)  REFERENCES SPOTS(spot_id) ON DELETE SET NULL,
  FOREIGN KEY (payment_method_id)  REFERENCES PAYMENT_METHODS(id),
  INDEX idx_payments_parking_id (parking_id)
);
