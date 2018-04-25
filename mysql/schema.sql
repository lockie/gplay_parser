USE `default`;

CREATE TABLE IF NOT EXISTS `PermissionGroups` (
       `id` INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
       `title` VARCHAR(128) NOT NULL,
       `icon` VARCHAR(256) NOT NULL,
       UNIQUE (`title`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Permissions` (
       `id` INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
       `title` VARCHAR(128) NOT NULL,
       `group_id` INTEGER NOT NULL,
       FOREIGN KEY (`group_id`) REFERENCES `PermissionGroups`(`id`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Apps` (
       `id` INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
       `identifier` VARCHAR(128) NOT NULL,
       `language` VARCHAR(4) NOT NULL,
       UNIQUE (`identifier`, `language`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `AppPermissions` (
       `app_id` INTEGER NOT NULL,
       `permission_id` INTEGER NOT NULL,
       PRIMARY KEY (`app_id`, `permission_id`),
       FOREIGN KEY (`app_id`) REFERENCES `Apps`(`id`),
       FOREIGN KEY (`permission_id`) REFERENCES `Permissions`(`id`)
) DEFAULT CHARSET=utf8;
