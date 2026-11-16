from sqlalchemy import text
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError

async def get_domains(engine):
    try:
        async with engine.connect() as conn:
            query = await conn.execute(
                text("SELECT dominio FROM VW_SIS_PARAMETROS")
            )

            result = query.scalars().all()

            if result:
                return {
                    "status": True,
                    "msg": "Consulta ejecutada exitosamente",
                    "result": result
                }

            return {
                "status": False,
                "msg": "La consulta no devolvió resultados",
                "result": []
            }

    except SQLAlchemyError as error:
        return {
            "status": False,
            "msg": f"Error al consultar los dominios: {error}",
            "result": []
        }


async def connect_test(engine):
    try:
        async with engine.connect() as conn:
            query = await conn.execute(text("SELECT 1 as flag, current_database() as dbname"))
            result=query.fetchall()  
            if result[0].flag == 1:
                return (True, "[ÉXITO]: Conexión establecida exitosamente",result[0].dbname)
            else:
                return (False, "[ERROR]: La consulta no devolvió el resultado esperado","")
            
    except exc.OperationalError as e:
        
        # contraseñas incorrectas, base de datos apagada,
        # caidas de red o timeouts del servidor.
        return (False, f"Error operativo: - {e.orig}","")
    except exc.ProgrammingError as e:
        
        # la tabla no existe, una columna esta mal escrita,
        # o el usuario no tiene permisos de lectura o escritura.
        return (False, f"Error de programación / sintaxis SQL: - {e.orig}","")
    except exc.IntegrityError as e:
        
        # errores en fk, pk, uniques, y mas
        return (False, f"Violación de integridad de datos: - {e.orig}","")
    except exc.DataError as e:
        
        # datos truncados
        return (False, f"Error de formato de datos: - {e.orig}","")
    except exc.DBAPIError as e:
        
        # errores en el driver.
        return (False, f"Error general del driver de BD: - Tipo: {type(e).__name__} - Detalle: {e}","")
    except exc.ArgumentError as e:
        
        # url mal escrita
        return (False, f"Configuración de URL de SQLAlchemy inválida: - {e}","")
    except Exception as e:
        
        # errores fuera de la base de datos
        return (False, f"Error inesperado del sistema: - Tipo: {type(e).__name__} - Detalle: {e}","")
        
# Código para ejecutar este archivo de forma individual
# asyncio.run(connect_test(engine))
