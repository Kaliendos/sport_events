from fastapi import APIRouter, Depends

from src.event.services import CitiesService

router = APIRouter(prefix="/cities")


@router.get("")
async def get_cities_list(service: CitiesService = Depends()):
    return await service.get_city_list()
