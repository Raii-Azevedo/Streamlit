import snowflake.connector

def get_connection():
    return snowflake.connector.connect(
        user='SEU_USUARIO',
        password='SUA_SENHA',
        account='SEU_ACCOUNT',
        warehouse='SEU_WAREHOUSE',
        database='SEU_DATABASE',
        schema='SEU_SCHEMA'
    )
