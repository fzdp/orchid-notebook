CREATE TABLE IF NOT EXISTS `notebooks` (
  `id` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `name` varchar(20) NOT NULL DEFAULT ''
,  `parent_id` integer  DEFAULT NULL
,  `description` varchar(300) DEFAULT ''
,  `updated_at` timestamp NOT NULL DEFAULT current_timestamp
,  `created_at` timestamp NOT NULL DEFAULT current_timestamp
,  CONSTRAINT `notebooks_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `notebooks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS `tags` (
  `id` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `name` varchar(15) NOT NULL DEFAULT ''
,  `created_at` timestamp NULL DEFAULT current_timestamp
,  `updated_at` timestamp NULL DEFAULT current_timestamp
);
CREATE TABLE IF NOT EXISTS `note_tags` (
  `id` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `tag_id` integer  NOT NULL
,  `note_id` integer  NOT NULL
,  `created_at` timestamp NOT NULL DEFAULT current_timestamp
,  `updated_at` timestamp NOT NULL DEFAULT current_timestamp
,  CONSTRAINT `note_tags_ibfk_1` FOREIGN KEY (`note_id`) REFERENCES `notes` (`id`) ON DELETE CASCADE
,  CONSTRAINT `note_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
);
CREATE TABLE IF NOT EXISTS `notes` (
  `id` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `title` varchar(30) DEFAULT ''
,  `note_tag_id` integer  DEFAULT NULL
,  `notebook_id` integer  DEFAULT NULL
,  `created_at` timestamp NULL DEFAULT current_timestamp
,  `updated_at` timestamp NULL DEFAULT current_timestamp
,  `is_markdown` integer DEFAULT '0'
,  `local_uuid` varchar(36) DEFAULT ''
,  CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`note_tag_id`) REFERENCES `note_tags` (`id`)
,  CONSTRAINT `notes_ibfk_3` FOREIGN KEY (`notebook_id`) REFERENCES `notebooks` (`id`) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS `todos` (
  `id` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `title` varchar(150) NOT NULL DEFAULT ''
,  `content` varchar(5000) DEFAULT ''
,  `remark` varchar(5000) DEFAULT ''
,  `finished_at` datetime DEFAULT NULL
,  `is_finished` integer DEFAULT '0'
,  `note_id` integer  DEFAULT NULL
,  `created_at` timestamp NULL DEFAULT current_timestamp
,  `updated_at` timestamp NULL DEFAULT current_timestamp
,  `group` varchar(200) DEFAULT NULL
,  `priority` integer NOT NULL DEFAULT '0'
,  CONSTRAINT `todos_ibfk_1` FOREIGN KEY (`note_id`) REFERENCES `notes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_note_tags_note_id" ON "note_tags" (`note_id`);
CREATE INDEX IF NOT EXISTS "idx_note_tags_tag_id" ON "note_tags" (`tag_id`);
CREATE INDEX IF NOT EXISTS "idx_notebooks_parent_id" ON "notebooks" (`parent_id`);
CREATE INDEX IF NOT EXISTS "idx_notes_note_tag_id" ON "notes" (`note_tag_id`);
CREATE INDEX IF NOT EXISTS "idx_notes_notebook_id" ON "notes" (`notebook_id`);
CREATE INDEX IF NOT EXISTS "idx_notes_title" ON "notes" (`title`);
CREATE INDEX IF NOT EXISTS "idx_tags_name" ON "tags" (`name`);
CREATE INDEX IF NOT EXISTS "idx_todos_content" ON "todos" (`content`);
CREATE INDEX IF NOT EXISTS "idx_todos_note_id" ON "todos" (`note_id`);
