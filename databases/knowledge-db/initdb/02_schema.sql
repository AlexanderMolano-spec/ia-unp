/*
 Navicat Premium Dump SQL

 Source Server         : local_posgresql
 Source Server Type    : PostgreSQL
 Source Server Version : 170006 (170006)
 Source Host           : localhost:5432
 Source Catalog        : mcp-unp-db
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170006 (170006)
 File Encoding         : 65001

 Date: 29/01/2026 17:01:19
*/


-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- Sequence structure for eco_aqua_base_conocimiento_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_base_conocimiento_id_seq";
CREATE SEQUENCE "public"."eco_aqua_base_conocimiento_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_base_conocimiento_id_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_documento_id_documento_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_documento_id_documento_seq";
CREATE SEQUENCE "public"."eco_aqua_documento_id_documento_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_documento_id_documento_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq";
CREATE SEQUENCE "public"."eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_etiquetariesgo_id_etiquetariesgo_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_etiquetariesgo_id_etiquetariesgo_seq";
CREATE SEQUENCE "public"."eco_aqua_etiquetariesgo_id_etiquetariesgo_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_etiquetariesgo_id_etiquetariesgo_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_fragmento_id_fragmento_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_fragmento_id_fragmento_seq";
CREATE SEQUENCE "public"."eco_aqua_fragmento_id_fragmento_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_fragmento_id_fragmento_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_fragmento_vector_id_analisis_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_fragmento_vector_id_analisis_seq";
CREATE SEQUENCE "public"."eco_aqua_fragmento_vector_id_analisis_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_fragmento_vector_id_analisis_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_fuente_abierta_id_fuente_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_fuente_abierta_id_fuente_seq";
CREATE SEQUENCE "public"."eco_aqua_fuente_abierta_id_fuente_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_fuente_abierta_id_fuente_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Sequence structure for eco_aqua_objetivo_busqueda_id_objetivo_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."eco_aqua_objetivo_busqueda_id_objetivo_seq";
CREATE SEQUENCE "public"."eco_aqua_objetivo_busqueda_id_objetivo_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."eco_aqua_objetivo_busqueda_id_objetivo_seq" OWNER TO "knowledge_db_user";

-- ----------------------------
-- Table structure for eco_aqua_base_conocimiento
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_base_conocimiento";
CREATE TABLE "public"."eco_aqua_base_conocimiento" (
  "id" int4 NOT NULL DEFAULT nextval('eco_aqua_base_conocimiento_id_seq'::regclass),
  "texto" text COLLATE "pg_catalog"."default" NOT NULL,
  "tipo_dato" varchar(20) COLLATE "pg_catalog"."default",
  "embedding" vector(768),
  "id_etiquetariesgo" int4
)
;
ALTER TABLE "public"."eco_aqua_base_conocimiento" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_documento
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_documento";
CREATE TABLE "public"."eco_aqua_documento" (
  "id_documento" int4 NOT NULL DEFAULT nextval('eco_aqua_documento_id_documento_seq'::regclass),
  "titulo" text COLLATE "pg_catalog"."default",
  "url" text COLLATE "pg_catalog"."default" NOT NULL,
  "texto_completo" text COLLATE "pg_catalog"."default",
  "fecha_registro" timestamp(6) DEFAULT now(),
  "id_ejecucionconsulta" int4
)
;
ALTER TABLE "public"."eco_aqua_documento" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_documento_vector
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_documento_vector";
CREATE TABLE "public"."eco_aqua_documento_vector" (
  "id_documento" int4 NOT NULL,
  "embedding" vector(768),
  "modelo_embedding" varchar(50) COLLATE "pg_catalog"."default" DEFAULT 'paraphrase-multilingual-MiniLM-L12-v2'::character varying,
  "fecha_vectorizacion" timestamp(6) DEFAULT now()
)
;
ALTER TABLE "public"."eco_aqua_documento_vector" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_ejecucionconsulta
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_ejecucionconsulta";
CREATE TABLE "public"."eco_aqua_ejecucionconsulta" (
  "id_ejecucionconsulta" int4 NOT NULL DEFAULT nextval('eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq'::regclass),
  "consulta" text COLLATE "pg_catalog"."default",
  "fecha_inicio" timestamp(6) DEFAULT now(),
  "id_objetivo" int4
)
;
ALTER TABLE "public"."eco_aqua_ejecucionconsulta" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_etiquetariesgo
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_etiquetariesgo";
CREATE TABLE "public"."eco_aqua_etiquetariesgo" (
  "id_etiquetariesgo" int4 NOT NULL DEFAULT nextval('eco_aqua_etiquetariesgo_id_etiquetariesgo_seq'::regclass),
  "nombre" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "descripcion" text COLLATE "pg_catalog"."default",
  "nivel_prioridad" int4 DEFAULT 0
)
;
ALTER TABLE "public"."eco_aqua_etiquetariesgo" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_fragmento
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_fragmento";
CREATE TABLE "public"."eco_aqua_fragmento" (
  "id_fragmento" int4 NOT NULL DEFAULT nextval('eco_aqua_fragmento_id_fragmento_seq'::regclass),
  "texto_fragmento" text COLLATE "pg_catalog"."default" NOT NULL,
  "nro_secuencia" int4,
  "id_documento" int4
)
;
ALTER TABLE "public"."eco_aqua_fragmento" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_fragmento_vector
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_fragmento_vector";
CREATE TABLE "public"."eco_aqua_fragmento_vector" (
  "id_analisis" int4 NOT NULL DEFAULT nextval('eco_aqua_fragmento_vector_id_analisis_seq'::regclass),
  "id_fragmento" int4,
  "embedding" vector(768),
  "confianza" float8,
  "fatalidad_detectada" bool DEFAULT false,
  "fecha_analisis" timestamp(6) DEFAULT now(),
  "id_etiquetariesgo" int4
)
;
ALTER TABLE "public"."eco_aqua_fragmento_vector" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_fuente_abierta
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_fuente_abierta";
CREATE TABLE "public"."eco_aqua_fuente_abierta" (
  "id_fuente" int4 NOT NULL DEFAULT nextval('eco_aqua_fuente_abierta_id_fuente_seq'::regclass),
  "nombre_medio" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "url_fuente" text COLLATE "pg_catalog"."default" NOT NULL,
  "departamento" varchar(100) COLLATE "pg_catalog"."default" DEFAULT 'NACIONAL'::character varying,
  "municipio" varchar(100) COLLATE "pg_catalog"."default",
  "tipo_medio" varchar(50) COLLATE "pg_catalog"."default",
  "nivel_relevancia" int4 DEFAULT 1,
  "activo" bool DEFAULT true
)
;
ALTER TABLE "public"."eco_aqua_fuente_abierta" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- Table structure for eco_aqua_objetivo_busqueda
-- ----------------------------
DROP TABLE IF EXISTS "public"."eco_aqua_objetivo_busqueda";
CREATE TABLE "public"."eco_aqua_objetivo_busqueda" (
  "id_objetivo" int4 NOT NULL DEFAULT nextval('eco_aqua_objetivo_busqueda_id_objetivo_seq'::regclass),
  "nombre" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "activo" bool DEFAULT true,
  "fecha_registro" timestamp(6) DEFAULT now(),
  "partido" varchar(100) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "public"."eco_aqua_objetivo_busqueda" OWNER TO "knowledge_db_user";

-- ----------------------------

-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_base_conocimiento_id_seq"
OWNED BY "public"."eco_aqua_base_conocimiento"."id";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_documento_id_documento_seq"
OWNED BY "public"."eco_aqua_documento"."id_documento";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_ejecucionconsulta_id_ejecucionconsulta_seq"
OWNED BY "public"."eco_aqua_ejecucionconsulta"."id_ejecucionconsulta";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_etiquetariesgo_id_etiquetariesgo_seq"
OWNED BY "public"."eco_aqua_etiquetariesgo"."id_etiquetariesgo";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_fragmento_id_fragmento_seq"
OWNED BY "public"."eco_aqua_fragmento"."id_fragmento";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_fragmento_vector_id_analisis_seq"
OWNED BY "public"."eco_aqua_fragmento_vector"."id_analisis";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_fuente_abierta_id_fuente_seq"
OWNED BY "public"."eco_aqua_fuente_abierta"."id_fuente";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."eco_aqua_objetivo_busqueda_id_objetivo_seq"
OWNED BY "public"."eco_aqua_objetivo_busqueda"."id_objetivo";

-- ----------------------------
-- Indexes structure for table eco_aqua_base_conocimiento
-- ----------------------------
CREATE INDEX "idx_aqua_know" ON "public"."eco_aqua_base_conocimiento" USING hnsw (
  "embedding" "public"."vector_cosine_ops"
);

-- ----------------------------
-- Primary Key structure for table eco_aqua_base_conocimiento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_base_conocimiento" ADD CONSTRAINT "eco_aqua_base_conocimiento_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table eco_aqua_documento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_documento" ADD CONSTRAINT "unique_url_doc" UNIQUE ("url");

-- ----------------------------
-- Primary Key structure for table eco_aqua_documento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_documento" ADD CONSTRAINT "eco_aqua_documento_pkey" PRIMARY KEY ("id_documento");

-- ----------------------------
-- Primary Key structure for table eco_aqua_documento_vector
-- ----------------------------
ALTER TABLE "public"."eco_aqua_documento_vector" ADD CONSTRAINT "eco_aqua_documento_vector_pkey" PRIMARY KEY ("id_documento");

-- ----------------------------
-- Primary Key structure for table eco_aqua_ejecucionconsulta
-- ----------------------------
ALTER TABLE "public"."eco_aqua_ejecucionconsulta" ADD CONSTRAINT "eco_aqua_ejecucionconsulta_pkey" PRIMARY KEY ("id_ejecucionconsulta");

-- ----------------------------
-- Uniques structure for table eco_aqua_etiquetariesgo
-- ----------------------------
ALTER TABLE "public"."eco_aqua_etiquetariesgo" ADD CONSTRAINT "eco_aqua_etiquetariesgo_nombre_key" UNIQUE ("nombre");

-- ----------------------------
-- Primary Key structure for table eco_aqua_etiquetariesgo
-- ----------------------------
ALTER TABLE "public"."eco_aqua_etiquetariesgo" ADD CONSTRAINT "eco_aqua_etiquetariesgo_pkey" PRIMARY KEY ("id_etiquetariesgo");

-- ----------------------------
-- Primary Key structure for table eco_aqua_fragmento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_fragmento" ADD CONSTRAINT "eco_aqua_fragmento_pkey" PRIMARY KEY ("id_fragmento");

-- ----------------------------
-- Indexes structure for table eco_aqua_fragmento_vector
-- ----------------------------
CREATE INDEX "idx_aqua_frag_vec" ON "public"."eco_aqua_fragmento_vector" USING hnsw (
  "embedding" "public"."vector_cosine_ops"
);

-- ----------------------------
-- Primary Key structure for table eco_aqua_fragmento_vector
-- ----------------------------
ALTER TABLE "public"."eco_aqua_fragmento_vector" ADD CONSTRAINT "eco_aqua_fragmento_vector_pkey" PRIMARY KEY ("id_analisis");

-- ----------------------------
-- Primary Key structure for table eco_aqua_fuente_abierta
-- ----------------------------
ALTER TABLE "public"."eco_aqua_fuente_abierta" ADD CONSTRAINT "eco_aqua_fuente_abierta_pkey" PRIMARY KEY ("id_fuente");

-- ----------------------------
-- Indexes structure for table eco_aqua_objetivo_busqueda
-- ----------------------------
CREATE INDEX "idx_objetivo_nombre_trgm" ON "public"."eco_aqua_objetivo_busqueda" USING gin (
  "nombre" COLLATE "pg_catalog"."default" "public"."gin_trgm_ops"
);

-- ----------------------------
-- Uniques structure for table eco_aqua_objetivo_busqueda
-- ----------------------------
ALTER TABLE "public"."eco_aqua_objetivo_busqueda" ADD CONSTRAINT "eco_aqua_objetivo_busqueda_nombre_key" UNIQUE ("nombre");

-- ----------------------------
-- Primary Key structure for table eco_aqua_objetivo_busqueda
-- ----------------------------
ALTER TABLE "public"."eco_aqua_objetivo_busqueda" ADD CONSTRAINT "eco_aqua_objetivo_busqueda_pkey" PRIMARY KEY ("id_objetivo");

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_base_conocimiento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_base_conocimiento" ADD CONSTRAINT "eco_aqua_base_conocimiento_id_etiquetariesgo_fkey" FOREIGN KEY ("id_etiquetariesgo") REFERENCES "public"."eco_aqua_etiquetariesgo" ("id_etiquetariesgo") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_documento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_documento" ADD CONSTRAINT "eco_aqua_documento_id_ejecucionconsulta_fkey" FOREIGN KEY ("id_ejecucionconsulta") REFERENCES "public"."eco_aqua_ejecucionconsulta" ("id_ejecucionconsulta") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_documento_vector
-- ----------------------------
ALTER TABLE "public"."eco_aqua_documento_vector" ADD CONSTRAINT "eco_aqua_documento_vector_id_documento_fkey" FOREIGN KEY ("id_documento") REFERENCES "public"."eco_aqua_documento" ("id_documento") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_ejecucionconsulta
-- ----------------------------
ALTER TABLE "public"."eco_aqua_ejecucionconsulta" ADD CONSTRAINT "fk_consulta_objetivo" FOREIGN KEY ("id_objetivo") REFERENCES "public"."eco_aqua_objetivo_busqueda" ("id_objetivo") ON DELETE SET NULL ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_fragmento
-- ----------------------------
ALTER TABLE "public"."eco_aqua_fragmento" ADD CONSTRAINT "eco_aqua_fragmento_id_documento_fkey" FOREIGN KEY ("id_documento") REFERENCES "public"."eco_aqua_documento" ("id_documento") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table eco_aqua_fragmento_vector
-- ----------------------------
ALTER TABLE "public"."eco_aqua_fragmento_vector" ADD CONSTRAINT "eco_aqua_fragmento_vector_id_etiquetariesgo_fkey" FOREIGN KEY ("id_etiquetariesgo") REFERENCES "public"."eco_aqua_etiquetariesgo" ("id_etiquetariesgo") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."eco_aqua_fragmento_vector" ADD CONSTRAINT "eco_aqua_fragmento_vector_id_fragmento_fkey" FOREIGN KEY ("id_fragmento") REFERENCES "public"."eco_aqua_fragmento" ("id_fragmento") ON DELETE CASCADE ON UPDATE NO ACTION;
