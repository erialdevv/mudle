-- Mitigación de IDOR: la API ya no recibe el ID interno, recibe el código (UUID).
-- La función devuelve también `id` solo para uso interno del servicio (la API no lo expone:
-- el response_model lo filtra) y así llamar a sp_actualizar_usuario / sp_anular_usuario,
-- que siguen recibiendo p_id sin cambios.

BEGIN;

DROP FUNCTION IF EXISTS public.fn_obtener_usuario_por_codigo(uuid);
CREATE FUNCTION public.fn_obtener_usuario_por_codigo(p_codigo uuid)
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
    WHERE u.codigo = p_codigo;
$function$;

-- Ya no se usa desde la API (ejecutar solo tras desplegar el código nuevo):
DROP FUNCTION IF EXISTS public.fn_obtener_usuario_por_id(bigint);

COMMIT;
