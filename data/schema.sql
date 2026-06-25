-- PulpFiction 2.0 — Esquema de Base de Datos
-- Datos sintéticos para portfolio público
-- Seed reproducible: todas las generaciones usan random_seed=42

CREATE TABLE IF NOT EXISTS boletas (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo_origen          TEXT    NOT NULL,
    numero_boleta           TEXT    NOT NULL UNIQUE,
    rut                     TEXT    NOT NULL,
    empresa                 TEXT    NOT NULL,
    giro                    TEXT    NOT NULL,
    direccion               TEXT    NOT NULL,
    ciudad                  TEXT    NOT NULL,
    fecha                   DATE    NOT NULL,
    hora                    TEXT    NOT NULL,
    monto_neto              INTEGER NOT NULL CHECK(monto_neto > 0),
    iva                     INTEGER NOT NULL CHECK(iva >= 0),
    propina                 INTEGER DEFAULT 0 CHECK(propina >= 0),
    total                   INTEGER NOT NULL CHECK(total > 0),
    tipo_pago               TEXT    NOT NULL CHECK(tipo_pago IN ('Debito', 'Credito', 'Efectivo')),
    marca_tarjeta           TEXT    DEFAULT NULL,
    medio_pago              TEXT    DEFAULT NULL,
    numero_tarjeta          TEXT    DEFAULT NULL,
    terminal                TEXT    DEFAULT NULL,
    numero_operacion        TEXT    DEFAULT NULL,
    codigo_autorizacion     TEXT    DEFAULT NULL,
    moneda                  TEXT    NOT NULL DEFAULT 'CLP',
    cuotas                  INTEGER DEFAULT 1,
    tipo_cuotas             TEXT    DEFAULT NULL,
    estado_validacion       TEXT    NOT NULL DEFAULT 'Aprobado',
    comision_transbank      INTEGER DEFAULT 0 CHECK(comision_transbank >= 0),
    fecha_abono             DATE    DEFAULT NULL,
    id_transaccion_tbk      TEXT    DEFAULT NULL UNIQUE,
    fuente_datos            TEXT    NOT NULL DEFAULT 'SINTETICO',
    fuente_fecha            DATE    NOT NULL
);

-- Tabla de resumen diario
CREATE TABLE IF NOT EXISTS resumen_diario (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha           DATE    NOT NULL UNIQUE,
    total_ventas    INTEGER NOT NULL CHECK(total_ventas >= 0),
    total_iva       INTEGER NOT NULL CHECK(total_iva >= 0),
    total_propinas  INTEGER NOT NULL CHECK(total_propinas >= 0),
    cantidad_boletas INTEGER NOT NULL CHECK(cantidad_boletas >= 0),
    ticket_promedio INTEGER NOT NULL CHECK(ticket_promedio >= 0),
    pct_efectivo    REAL    CHECK(pct_efectivo BETWEEN 0 AND 100)
);

-- Tabla de indicadores mensuales
CREATE TABLE IF NOT EXISTS indicadores_mensuales (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    anio                INTEGER NOT NULL,
    mes                 INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
    total_ventas        INTEGER NOT NULL CHECK(total_ventas >= 0),
    total_iva           INTEGER NOT NULL CHECK(total_iva >= 0),
    total_propinas      INTEGER NOT NULL CHECK(total_propinas >= 0),
    cantidad_boletas    INTEGER NOT NULL CHECK(cantidad_boletas >= 0),
    ticket_promedio     INTEGER NOT NULL CHECK(ticket_promedio >= 0),
    pct_credito         REAL    CHECK(pct_credito BETWEEN 0 AND 100),
    pct_debito          REAL    CHECK(pct_debito BETWEEN 0 AND 100),
    UNIQUE(anio, mes)
);

-- Índices para consultas del dashboard
CREATE INDEX IF NOT EXISTS idx_boletas_fecha ON boletas(fecha);
CREATE INDEX IF NOT EXISTS idx_boletas_medio_pago ON boletas(medio_pago);
CREATE INDEX IF NOT EXISTS idx_boletas_tipo_pago ON boletas(tipo_pago);
CREATE INDEX IF NOT EXISTS idx_boletas_marca_tarjeta ON boletas(marca_tarjeta);
CREATE INDEX IF NOT EXISTS idx_boletas_monto ON boletas(monto_neto);
CREATE INDEX IF NOT EXISTS idx_resumen_diario_fecha ON resumen_diario(fecha);
CREATE INDEX IF NOT EXISTS idx_indicadores_mes ON indicadores_mensuales(anio, mes);
