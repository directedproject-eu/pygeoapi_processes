import os
import socket
import time
from contextlib import closing

import psycopg2
from qgis.core import QgsApplication


def verify_database_connection(db_name: str, db_host: str, db_port: int, db_user: str,
                               db_password: str, no_ping: bool = False) -> bool:
    if not no_ping:
        # ping host
        response = os.system("ping -c 1 {} > /dev/null".format(db_host))
        if response == 0:
            print("Database host '{}' reachable via ping.".format(db_host))
        else:
            print("Could not ping required database host '{}'.".format(db_host))
            return False
    # check host port
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            if sock.connect_ex((db_host, db_port)) == 0:
                print("Database port '{}' on host '{}' is OPEN.".format(db_port, db_host))
            else:
                print("Database port '{}' on host '{}' is CLOSED.".format(db_port, db_host))
                return False
        except socket.gaierror:
            print("Hostname '{}' could not be resolved.".format(db_host))
            return False

    # psql connect
    with closing(psycopg2.connect("host={} port={} dbname={} user={} password={}"
                                  .format(db_host, db_port, db_name, db_user, db_password))) as db_conn:
        if db_conn and not db_conn.closed:
            print("Database connection to '{}' established".format(db_name))
        else:
            print("Could NOT connect to database '{}'".format(db_name))
            return False
    return True


def flood_damage_create_system(db_name: str, db_host: str, db_port: int, db_user: str, db_password: str):
    qgs = QgsApplication([], False)
    qgs.initQgis()

    import processing
    from OS2DamageCostAdmin.flood_damage_data_import_provider import FloodDamageCostAdmin

    # processing.core.Processing.Processing.initialize()  # to load built-in/native algorithms
    p = FloodDamageCostAdmin()
    QgsApplication.processingRegistry().addProvider(p)

    # for alg in QgsApplication.processingRegistry().algorithms():
    #     print(alg.id())
    #
    # for prov in QgsApplication.processingRegistry().providers():
    #     print(prov.id())

    # print("Number of algorithms:", len(QgsApplication.processingRegistry().algorithms()))
    # print("Number of providers:", len(QgsApplication.processingRegistry().providers()))

    new_database = 'flood_damage'
    repository_url = 'https://storage.googleapis.com/skadesokonomi-dk-data/createscripts.json'
    processing.run(
        "fdccost:flood_damage_create_system", {
            'server_name': db_host,
            'server_port': db_port,
            'adm_user': db_user,
            'adm_password': db_password,
            'database_name': new_database,
            'fdc_connection':'{database_name} at {server_name} as {administrative_user}',
            'repository_url': repository_url,
            'adm_database_name': db_name,
            'run_scripts': [0,1,2,3],
            'fdc_admin_role': '{database_name}_admin_role',
            'fdc_model_role': '{database_name}_model_role',
            'fdc_read_role': '{database_name}_read_role'
        }
    )


if __name__ == '__main__':
    db_host = os.getenv('POSTGRES_HOST', default='localhost')
    db_port = os.getenv('POSTGRES_PORT', default=5432)
    db_admin_user = os.getenv('POSTGRES_USER', default='docker')
    db_admin_pw = os.getenv('POSTGRES_PASSWORD', default='docker')
    db_admin_db = os.getenv('POSTGRES_ADMIN_DB', default='postgres')
    no_ping = True
    max_retries = 15
    sleep = 1

    times_slept = 0
    db_conn_ok = False
    while times_slept < max_retries:
        print("[{}/{}] Check database connection".format(str(times_slept + 1), str(max_retries)))
        if verify_database_connection(db_admin_db, db_host, db_port, db_admin_user, db_admin_pw, no_ping):
            db_conn_ok = True
            break
        time.sleep(sleep)
        times_slept = times_slept + 1
    if db_conn_ok:
        try:
            flood_damage_create_system(db_admin_db, db_host, db_port, db_admin_user, db_admin_pw)
            print("Created system for DTU damage cost model")
        except Exception as err:
            print(err)