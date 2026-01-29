CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 2. TABLA: USUARIO (Contexto Organizacional)
-- =============================================================================
-- Captura la información del objeto "user" del payload.
CREATE TABLE eco_mcp_memoria_usuario (
    -- ID interno autoincremental (para relaciones eficientes dentro de la BD)
    id_usuario SERIAL PRIMARY KEY,

    -- [user.id_busuario] Identificador único del usuario en tu sistema
    -- Ejemplo: "4dc8b835-a22a-4b1d-94eb-f2194498355a"
    id_externo_busuario UUID NOT NULL UNIQUE,

    -- [user.username] El login de red
    -- Ejemplo: "nombre.apellido"
    username VARCHAR(100) NOT NULL,

    -- [user.nombres] Nombre completo
    -- Ejemplo: "Pedro Farith Lopez Ortiz"
    nombres VARCHAR(200),

    -- [user.dependencia] Área organizacional
    -- Ejemplo: "Subdirección de Evaluación del Riesgo"
    dependencia TEXT,

    -- [user.grupo] Grupo de trabajo detallado
    -- Ejemplo: "Grupo Cuerpo Técnico de Análisis..."
    grupo_trabajo TEXT,

    -- [user.servicios -> concatenar "rol"]
    -- Guardas los NOMBRES de roles separados por coma (Texto plano).
    -- Ejemplo: "Digitador (SER), Radicador, Gestor"
    roles_nombres TEXT,

    -- [user.servicios -> concatenar "id_rol"]
    -- Guardas los IDs numéricos de roles separados por coma (Texto plano).
    -- Ejemplo: "2220, 5731, 8401"
    roles_ids TEXT,

    -- Auditoría interna
    fecha_registro TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- 3. TABLA: SESIÓN (Contexto de Conexión)
-- =============================================================================
-- Vincula el chat actual con el "session_id" y "expiresAt" de tu app.
CREATE TABLE eco_mcp_memoria_sesion (
    -- ID único de la sesión en esta base de datos
    id_sesion UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relación con el usuario (Si se borra el usuario, se borra su historial)
    id_usuario INT REFERENCES eco_mcp_memoria_usuario(id_usuario) ON DELETE CASCADE,

    -- [session_id] El ID de sesión que viene en la raíz del payload
    -- Ejemplo: "c76bc34d-a3ce-417a-bfb5-b0b0a0f6a3fe"
    session_id_app UUID NOT NULL,

    -- [Opcional] Nombre del agente (ej: 'Aqua', 'Ignis')
    agente_nombre VARCHAR(100),

    -- Control de tiempo
    fecha_inicio TIMESTAMP DEFAULT NOW(),
    ultima_actividad TIMESTAMP DEFAULT NOW(),
    
    -- Estado lógico (TRUE = Sesión válida)
    activo BOOLEAN DEFAULT TRUE
);

-- Índice de velocidad para buscar por el session_id de tu app
CREATE INDEX idx_eco_sesion_app ON eco_mcp_memoria_sesion(session_id_app);

-- =============================================================================
-- 4. TABLA: MENSAJES (Historial de Chat)
-- =============================================================================
-- Aquí se guarda la conversación pura.
CREATE TABLE eco_mcp_memoria_mensaje (
    -- ID único del mensaje
    id_mensaje UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relación con la sesión anterior
    id_sesion UUID REFERENCES eco_mcp_memoria_sesion(id_sesion) ON DELETE CASCADE,

    -- Quién habla: 'user', 'assistant', 'system'
    rol VARCHAR(50) NOT NULL,

    -- El texto de la conversación
    contenido TEXT NOT NULL,

    -- Cuándo se dijo
    fecha_creacion TIMESTAMP DEFAULT NOW()
);