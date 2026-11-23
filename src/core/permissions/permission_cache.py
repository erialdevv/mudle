import json

async def get_role_permissions(self,rol_id:int,conn)->dict|None:
    
    try:
        key=f"role:permissions:{rol_id}"
        result=await self.redis.get(key)
        
        if not result:
            #logica para devolver 
            
        
        
        
    except Exception as error:
        pass