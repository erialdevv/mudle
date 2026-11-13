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
                    "msg": "Query executed successfully",
                    "result": result
                }

            return {
                "status": False,
                "msg": "The query returned no results",
                "result": []
            }

    except SQLAlchemyError as error:
        return {
            "status": False,
            "msg": f"Error querying domains: {error}",
            "result": []
        }


async def connect_test(engine):
    try:
        async with engine.connect() as conn:
            query = await conn.execute(text("SELECT 1 as flag, current_database() as dbname"))
            result=query.fetchall()  
            if result[0].flag == 1:
                return (True, "[SUCCESS]: Connection established successfully",result[0].dbname)
            else:
                return (False, "[ERROR]: Query did not return the expected result","")
            
    except exc.OperationalError as e:
        
        # contraseñas incorrectas, base de datos apagada,
        # caidas de red o timeouts del servidor.
        return (False, f"Operational error: - {e.orig}","")
    except exc.ProgrammingError as e:
        
        # la tabla no existe, una columna esta mal escrita,
        # o el usuario no tiene permisos de lectura o escritura.
        return (False, f"Programming / SQL syntax error: - {e.orig}","")
    except exc.IntegrityError as e:
        
        # errores en fk, pk, uniques, y mas
        return (False, f"Data integrity violation: - {e.orig}","")
    except exc.DataError as e:
        
        # datos truncados
        return (False, f"Data format error: - {e.orig}","")
    except exc.DBAPIError as e:
        
        # errores en el driver.
        return (False, f"General DB driver error: - Type: {type(e).__name__} - Detail: {e}","")
    except exc.ArgumentError as e:
        
        # url mal escrita
        return (False, f"Invalid SQLAlchemy URL configuration: - {e}","")
    except Exception as e:
        
        # errores fuera de la base de datos
        return (False, f"Unexpected system error: - Type: {type(e).__name__} - Detail: {e}","")
        
#Codigo si se desea ejecutar el archivo connection de forma individual
# asyncio.run(connect_test(engine))
