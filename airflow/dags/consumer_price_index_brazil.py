from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.sensors.base import PokeReturnValue
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from include.consumer_price_index_brazil.tasks import _check_if_new_ipca_data, _fetch_ipca_data, _save_ipca_data

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
    def is_metadata_api_available() -> PokeReturnValue:
        """
        Sensor checking IBGE API availability.
        """
        api = BaseHook.get_connection('ibge_metadata_api')
        url = f"{api.host}{api.extra_dejson['pesquisas']}"
        logging.info(f"Checking IBGE API availability: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return PokeReturnValue(is_done=True, xcom_value=response.json())
        
    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def is_sidra_api_available() -> PokeReturnValue:
        """
        Sensor checking IBGE SIDRA API availability.
        """
        api = BaseHook.get_connection('ibge_sidra_api')
        url = f"{api.host}{api.extra_dejson['ipca_test_endpoint']}"
        logging.info(f"Checking IBGE API availability: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return PokeReturnValue(is_done=True, xcom_value=response.json())

    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def get_last_datapoint() -> PokeReturnValue:
        """
        Sensor checking the last saved IPCA data in MinIO.
        """
        # last_date = _get_last_datapoint()
        # if last_date:
        #     return PokeReturnValue(is_done=True, xcom_value=last_date)
        return PokeReturnValue(is_done=True, xcom_value=datetime.now().strftime('%Y-%m'))

    # Logical AND merge point
    wait_for_sensors = DummyOperator(task_id="wait_for_sensors")
    
    check_if_new_ipca_data = PythonOperator(
        task_id='check_if_new_ipca_data',
        python_callable=_check_if_new_ipca_data,
        provide_context=True
    )

    # Fetch and save data
    fetch_data = PythonOperator(
        task_id='fetch_ipca_data',
        python_callable=_fetch_ipca_data,
        provide_context=True
    )

    save_data = PythonOperator(
        task_id='save_ipca_data',
        python_callable=_save_ipca_data,
        provide_context=True
    )

    # DAG Dependencies
    [is_metadata_api_available, is_sidra_api_available, get_last_datapoint] >>  wait_for_sensors

    # wait_for_sensors >> check_if_new_ipca_data >> fetch_data >> save_data


consumer_price_index_brazil()
