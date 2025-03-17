from airflow.providers.postgres.hooks.postgres import PostgresHook


def _check_if_new_ipca_data():
    
    """
    Checks if there is new IPCA data available from the IBGE Metadata API.

    Returns:
        bool: True if there is new data, False otherwise.
    """
    pass

def _fetch_ipca_data(month, year):
    """
    Fetchs IPCA data for the current month from the IBGE SIDRA API.

    Returns:
        bool: True if there is new data, False otherwise.
    """
    pass

def _save_ipca_data(data):
    """
    Saves the data to MinIO.
    """
    pass