from sqlalchemy import text
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError

async def obtener_dominios(engine):
    try:
        async with engine.connect() as conn:
            lcsql = await conn.execute(
                text("SELECT dominio FROM VW_SIS_PARAMETROS")
            )

            result = lcsql.scalars().all()

            if result:
                return {
                    "estado": True,
                    "msg": "Consulta realizada con éxito",
                    "resultado": result
                }

            return {
                "estado": False,
                "msg": "La consulta no devolvió ningún resultado",
                "resultado": []
            }

    except SQLAlchemyError as error:
        return {
            "estado": False,
            "msg": f"Error al consultar los dominios: {error}",
            "resultado": []
        }


async def connect_test(engine):
    try:
        async with engine.connect() as conn:
            lcsql = await conn.execute(text("SELECT 1 as bandera, current_database() as dbname"))
            result=lcsql.fetchall()  
            if result[0].bandera == 1:
                return (True, "[EXITO]:Conexion establecida exitosamente",result[0].dbname)
            else:
                return (False, "[ERROR]: Consulta no devolvio lo esperado","")
            
    except exc.OperationalError as e:
        
        # contraseñas incorrectas, base de datos apagada,
        # caidas de red o timeouts del servidor.
        return (False, f"Error Operacional: - {e.orig}","")
    except exc.ProgrammingError as e:
        
        # la tabla no existe, una columna esta mal escrita,
        # o el usuario no tiene permisos de lectura o escritura.
        return (False, f"Error de Programación / Sintaxis SQL: - {e.orig}","")
    except exc.IntegrityError as e:
        
        # errores en fk, pk, uniques, y mas
        return (False, f"Violación de Integridad de Datos: - {e.orig}","")
    except exc.DataError as e:
        
        # datos truncados
        return (False, f"Error en el formato de los datos: - {e.orig}","")
    except exc.DBAPIError as e:
        
        # errores en el driver.
        return (False, f"Error general del driver de BD: - Tipo: {type(e).__name__} - Detalle: {e}","")
    except exc.ArgumentError as e:
        
        # url mal escrita
        return (False, f"Configuración de URL inválida en SQLAlchemy: - {e}","")
    except Exception as e:
        
        # errores fuera de la base de datos
        return (False, f"Error inesperado del sistema: - Tipo: {type(e).__name__} - Detalle: {e}","")
        
#Codigo si se desea ejecutar el archivo connection de forma individual
# asyncio.run(connect_test(engine))
