-- Funciones de consulta con columnas ya nombradas como los schemas de la API.
-- Cambian el tipo de retorno, por eso se hace DROP antes de CREATE.
-- Desplegar junto con el código de la API (los servicios leen las claves nuevas).

BEGIN;

-- 1) Usuario por id (code, first_name, last_name, institutional_email, voided)
DROP FUNCTION IF EXISTS public.fn_obtener_usuario_por_id(bigint);
CREATE FUNCTION public.fn_obtener_usuario_por_id(p_id bigint)
RETURNS TABLE(
    id bigint,
    code uuid,
    first_name character varying,
    last_name character varying,
    institutional_email character varying,
    voided boolean,
    created_at timestamp with time zone,
    edited_at timestamp with time zone
)
LANGUAGE sql STABLE AS $function$
    SELECT u.id, u.codigo, u.nombre, u.apellido, u.email_est, u.anulado,
           u.fecha_creacion, u.fecha_editado
    FROM public.sis_usuarios AS u
    WHERE u.id = p_id;
$function$;

-- 2) Listado paginado de usuarios (nueva)
DROP FUNCTION IF EXISTS public.fn_obtener_usuarios(integer, integer, character varying, boolean);
CREATE FUNCTION public.fn_obtener_usuarios(
    p_limit integer DEFAULT 10,
    p_offset integer DEFAULT 0,
    p_search character varying DEFAULT NULL::character varying,
    p_only_active boolean DEFAULT true
)
RETURNS TABLE(
    code uuid,
    first_name character varying,
    last_name character varying,
    institutional_email character varying,
    voided boolean,
    total_records bigint
)
LANGUAGE sql STABLE AS $function$
    SELECT u.codigo AS code, u.nombre AS first_name, u.apellido AS last_name,
           u.email_est AS institutional_email, u.anulado AS voided,
           COUNT(*) OVER() AS total_records
    FROM public.sis_usuarios AS u
    WHERE (p_only_active IS FALSE OR u.anulado = FALSE)
      AND (p_search IS NULL OR p_search = ''
           OR u.nombre   ILIKE '%' || p_search || '%'
           OR u.apellido ILIKE '%' || p_search || '%'
           OR u.email_est ILIKE '%' || p_search || '%')
    ORDER BY u.nombre ASC, u.apellido ASC, u.id ASC
    LIMIT p_limit OFFSET p_offset;
$function$;

-- 3) Rol por id (code, name, version, permissions, voided)
DROP FUNCTION IF EXISTS public.fn_obtener_rol_por_id(bigint);
CREATE FUNCTION public.fn_obtener_rol_por_id(p_rol_id bigint)
RETURNS TABLE(
    code uuid,
    name character varying,
    version integer,
    permissions jsonb,
    voided boolean
)
LANGUAGE sql STABLE AS $function$
    SELECT r.codigo AS code, r.nombre AS name, r.version,
           r.permissions::jsonb, r.anulado AS voided
    FROM public.sis_roles AS r
    WHERE r.id = p_rol_id AND r.anulado = FALSE;
$function$;

-- 4) fn_obtener_roles ya devuelve los nombres correctos: no requiere cambios.

COMMIT;
