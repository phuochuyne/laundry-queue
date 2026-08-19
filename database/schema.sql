CREATE TABLE f_589af8dc__machines (
  id CHAR(36) NOT NULL,
  machine_number VARCHAR(50) NOT NULL,
  status VARCHAR(255) NOT NULL,
  building_id CHAR(36) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_machines_building FOREIGN KEY (building_id) REFERENCES f_589af8dc__buildings(id)
) ENGINE=InnoDB;

CREATE TABLE f_589af8dc__buildings (
  id CHAR(36) NOT NULL,
  name VARCHAR(200) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;


CREATE TABLE `f_e876dcda__users` (
  `id` CHAR(36) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `role` ENUM('resident','admin') NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_e6daa139__machines` (
  `id` CHAR(36) NOT NULL,
  `machine_number` VARCHAR(50) NOT NULL,
  `machine_type` ENUM('washer','dryer') NOT NULL,
  `qr_code_payload` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_85677965__buildings` (
  `id` CHAR(36) NOT NULL,
  `building_code` VARCHAR(50) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `f_85677965__approved_emails` (
  `id` CHAR(36) NOT NULL,
  `building_id` CHAR(36) NOT NULL,
  `email_address` VARCHAR(320) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_approved_emails_building` FOREIGN KEY (`building_id`) REFERENCES `f_85677965__buildings`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `f_85677965__user_building_memberships` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `building_id` CHAR(36) NOT NULL,
  `join_method` VARCHAR(20) NOT NULL,
  `joined_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_memberships_building` FOREIGN KEY (`building_id`) REFERENCES `f_85677965__buildings`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_a1e10606__machine_qr_codes` (
  `id` CHAR(36) NOT NULL,
  `qr_code_value` VARCHAR(255) NOT NULL,
  `machine_id` CHAR(36) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `f_a1e10606__machine_claims` (
  `id` CHAR(36) NOT NULL,
  `machine_id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `claimed_at` TIMESTAMP NOT NULL,
  `status` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_f115b2e6__laundry_sessions` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `machine_id` CHAR(36) NOT NULL,
  `started_at` TIMESTAMP NOT NULL,
  `duration_minutes` INT NOT NULL,
  `ended_at` TIMESTAMP NULL DEFAULT NULL,
  `status` ENUM('active','completed') NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_271c7167__sessions` (
  `session_id` CHAR(36) NOT NULL,
  `machine_id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `started_at` TIMESTAMP NOT NULL,
  `duration_minutes` INT NOT NULL,
  `status` ENUM('in_use','completed','cancelled') NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE f_a72b87c1__device_tokens (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  token VARCHAR(1024) NOT NULL,
  platform ENUM('ios','android') NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE f_a72b87c1__notifications (
  id CHAR(36) NOT NULL,
  session_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  machine_id CHAR(36) NOT NULL,
  title VARCHAR(100) NOT NULL,
  body VARCHAR(500) NOT NULL,
  sent_at TIMESTAMP NOT NULL,
  delivery_status ENUM('pending','sent','delivered','failed') NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;


CREATE TABLE f_342bee96__laundry_sessions (
  id CHAR(36) NOT NULL,
  machine_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP NULL,
  status ENUM('active','completed') NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_laundry_sessions_machine FOREIGN KEY (machine_id) REFERENCES f_342bee96__machines(id)
) ENGINE=InnoDB;

CREATE TABLE f_342bee96__machines (
  id CHAR(36) NOT NULL,
  status ENUM('available','in_use') NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;