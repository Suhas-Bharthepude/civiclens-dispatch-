from app.db.database import database

async def get_db():

    """
    FastAPI dependency to get a connected database object. 
    Can be used with Depends(get_db) in your endpoints
    """   

    # Connect if not already connected 
    if not database.is_connected:
        await database.connect()
    
    try:
        # Yield database object for use in route 
        yield database 
    
    finally:
        # Disconnect after the route finishes 
        await database.disconnect()        