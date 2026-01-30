# Diccionario de Datos - Agente Aqua

Este documento describe la estructura de la base de datos `knowledge_db` para el Agente Aqua. Proporciona el contexto necesario para que el LLM genere consultas SQL precisas y entienda las relaciones semánticas del sistema.

## Notas Técnicas Generales
- **Embeddings**: Las columnas de tipo `vector(768)` contienen representaciones numéricas de texto generadas por el modelo `paraphrase-multilingual-MiniLM-L12-v2`. Se utilizan para búsquedas de similitud semántica.
- **Motor**: PostgreSQL con la extensión `pgvector`.

---

## Tablas de Configuración y Metadatos

### `eco_aqua_objetivo_busqueda`
Almacena los perfiles o personas de interés que son objeto de investigación.
- `id_objetivo` (PK): Identificador único.
- `nombre`: Nombre del objetivo (persona, empresa, etc.).
- `activo`: Estado booleano.
- `partido`: Afiliación política si aplica.

### `eco_aqua_etiquetariesgo`
Diccionario de categorías de riesgo detectadas por el sistema.
- `id_etiquetariesgo` (PK): Identificador de la etiqueta.
- `nombre`: Nombre de la categoría (ej: 'Amenaza', 'Corrupción', 'Atentado').
- `descripcion`: Explicación de qué significa la etiqueta.
- `nivel_prioridad`: Entero donde valores más altos indican mayor riesgo.

### `eco_aqua_fuente_abierta`
Catálogo de medios de comunicación y portales web utilizados para la extracción.
- `id_fuente` (PK): Identificador de la fuente.
- `nombre_medio`: Nombre del portal (ej: 'El Tiempo', 'Revista Semana').
- `url_fuente`: URL base.
- `departamento` / `municipio`: Ubicación geográfica del medio.
- `tipo_medio`: Categoría (Prensa, Radio, TV, etc.).

---

## Tablas de Datos Dinámicos (Resultados)

### `eco_aqua_ejecucionconsulta`
Registra cada vez que el agente inicia una nueva investigación.
- `id_ejecucionconsulta` (PK): ID de ejecución.
- `consulta`: Términos de búsqueda utilizados.
- `fecha_inicio`: Timestamp de inicio.
- `id_objetivo` (FK): Relación con `eco_aqua_objetivo_busqueda`.

### `eco_aqua_documento`
Almacena el texto completo y metadatos de las noticias o documentos extraídos de la web.
- `id_documento` (PK): ID del documento.
- `titulo`: Título de la fuente original.
- `url`: Enlace directo a la fuente.
- `texto_completo`: El contenido crudo del documento.
- `id_ejecucionconsulta` (FK): Relación con la ejecución que lo generó.

### `eco_aqua_documento_vector`
Vectores semánticos de los documentos (embeddings globales).
- `id_documento` (FK): Relación 1:1 con `eco_aqua_documento`.
- `embedding`: Vector de 768 dimensiones.
- `modelo_embedding`: Nombre del modelo usado.

---

## Tablas de Análisis Granular

### `eco_aqua_fragmento`
Divide los documentos largos en trozos más pequeños (chunks) para análisis preciso.
- `id_fragmento` (PK): ID del fragmento.
- `texto_fragmento`: Contenido del trozo de texto.
- `nro_secuencia`: Orden del fragmento dentro del documento.
- `id_documento` (FK): Relación con `eco_aqua_documento`.

### `eco_aqua_fragmento_vector`
Resultados del análisis de riesgo y vectores para cada fragmento.
- `id_analisis` (PK): ID del análisis.
- `id_fragmento` (FK): Relación con `eco_aqua_fragmento`.
- `embedding`: Vector de 768 dimensiones.
- `confianza`: Probabilidad (float) de que el análisis sea correcto.
- `fatalidad_detectada`: Booleano (True si el fragmento indica un riesgo alto).
- `id_etiquetariesgo` (FK): Clasificación del riesgo.

### `eco_aqua_base_conocimiento`
Banco de ejemplos históricos o de "verdad" utilizados para comparar semánticamente.
- `id` (PK): ID.
- `texto`: Texto de ejemplo.
- `tipo_dato`: Clasificación (ej: 'Hecho', 'Rumor').
- `embedding`: Vector de 768 dimensiones.
- `id_etiquetariesgo` (FK): Etiqueta asociada al ejemplo.

---

## Relaciones (Join Path)

Para obtener información detallada de una investigación, el flujo de JOIN es:
`eco_aqua_objetivo_busqueda` -> `eco_aqua_ejecucionconsulta` -> `eco_aqua_documento` -> `eco_aqua_fragmento` -> `eco_aqua_fragmento_vector` -> `eco_aqua_etiquetariesgo`.
