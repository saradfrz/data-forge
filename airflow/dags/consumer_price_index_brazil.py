from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.sensors.base import PokeReturnValue
from airflow.operators.python import PythonOperator

from include.consumer_price_index_brazil.tasks import _fetch_ipca_data, _get_last_datapoint

import logging
import requests
from datetime import datetime


@dag(
    start_date=datetime(2022, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['ibge', 'ipca']
)

def consumer_price_index_brazil():
    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def is_api_available() -> PokeReturnValue:
        """
        This sensor function checks the availability of the IBGE API by sending a GET request
        to the specified endpoint. If the API is available and responds with a status code of
        200, it returns a PokeReturnValue with is_done set to True and the JSON response as 
        the xcom_value.

        :return: A PokeReturnValue indicating the availability of the API and the JSON response if available.
        :rtype: PokeReturnValue
        """
        api = BaseHook.get_connection('ibge_api')

        url = f"{api.host}{api.extra_dejson['pesquisas']}"
        logging.info(f"IBGE API URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return PokeReturnValue(is_done=True, xcom_value=response.json())
        
    get_last_datapoint = PythonOperator(
        task_id='is_api_available',
        python_callable=_get_last_datapoint,
        provide_context=True
    )
        
    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def is_new_data_available() -> PokeReturnValue:
        """
        """
        api = BaseHook.get_connection('ibge_api')

        url = f"{api.host}{api.extra_dejson['ipca']}"
        logging.info(f"IBGE API URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return PokeReturnValue(is_done=True, xcom_value=response.json())
        
    fetch_ipca_data = PythonOperator(
        task_id='fetch_ipca_data',
        python_callable=_fetch_ipca_data,
    )
        
    is_api_available()

consumer_price_index_brazil()
