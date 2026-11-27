-- Rol asignado a un usuario, buscando por el código (UUID) del usuario.
-- Devuelve las mismas columnas que fn_obtener_rol_por_id.
-- No filtra por anulado: la columna `voided` indica el estado del rol y la decisión
-- (404, aviso, etc.) la toma el servicio. Si no existe el usuario, devuelve 0 filas.

BEGIN;

DROP FUNCTION IF EXISTS public.fn_obtener_rol_por_codigo_usuario(uuid);
CREATE FUNCTION public.fn_obtener_rol_por_codigo_usuario(p_codigo_usuario uuid)
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
    FROM public.sis_usuarios AS u
    INNER JOIN public.sis_roles AS r ON r.id = u.rol_id
    WHERE u.codigo = p_codigo_usuario;
$function$;

COMMIT;
