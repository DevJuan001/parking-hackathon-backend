from fastapi import HTTPException
from app.features.countries.services.countries_service import CountriesService


class CountriesController:

    @staticmethod
    def get_all_countries():
        error, countries = CountriesService.get_all_countries()

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": countries
        }
