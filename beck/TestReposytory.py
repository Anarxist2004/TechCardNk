

from repositories.postgresDataBase import PostgresDataBase
from services.tech_card_service import TechCardData

repo =PostgresDataBase("host=localhost port=5435 dbname=techCard user=postgres password=1")

def getTypeControl():
    print(repo.get_all_controlled_element_types())

def getControlElement():
    print(repo.get_all_objects_by_type_id(1))

def getParams():
    print(repo.get_available_params_for_type(1))

def  get_all_possible_values_by_param_and_element():
    print(repo.get_all_possible_values_by_param_and_element(1,4))

def get_params_for_element():
    print(repo.get_params_for_element(3))


get_params_for_element()