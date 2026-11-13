from fastapi import APIRouter
from fastapi import FastAPI, HTTPException,status,Request
from repositories.general.startup import connect_test
from db.connection import engine

router=APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

@router.get(
    "/data_in_memory", 
    status_code=status.HTTP_200_OK,
    summary="View data loaded in memory",
    description=(
        "Allows viewing the initial data preloaded for the application to work. "
        "**Note:** Currently, the response is limited to the domains information only."
    )
)

async def loaded_data(request:Request):
    valid_domains = request.app.state.allowed_domains
    if valid_domains:
        return{
            "status": True,
            "message": "Data loaded in memory successfully",
            "database": valid_domains
        }
    return{
        "status":False,
        "message":"Memory is empty",
        "database": valid_domains
    }
    
@router.get("/isconnect", status_code=status.HTTP_200_OK)
async def db_check():
    result = await connect_test(engine)
    
    is_connected, error_detail, db_name = result[0], result[1], result[2]
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "status": "error",
                "message": "Could not establish a connection with the server.",
                "database": db_name,
                "technical_details": error_detail
            }
        )
        
    return {
        "status": "success",
        "message": "Connection established successfully.",
        "database": db_name
    }
