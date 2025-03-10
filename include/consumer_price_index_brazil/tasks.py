from airflow.providers.postgres.hooks.postgres import PostgresHook

def _get_last_record_date(**kwargs):
    postgres_hook = PostgresHook(postgres_conn_id="my_postgres_conn")
    sql = "SELECT MAX(date_column) FROM my_table;"
    result = postgres_hook.get_first(sql)

    if result and result[0]:
        last_date = result[0]
        year = last_date.year
        month = last_date.month
        # Push values to XComs for the next task
        kwargs['ti'].xcom_push(key='last_year', value=year)
        kwargs['ti'].xcom_push(key='last_month', value=month)
    else:
        raise ValueError("No records found in the database.")
    
def _fetch_ipca_data():
    url = f"{url}"