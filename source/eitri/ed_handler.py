# coding=utf-8

# Copyright (c) 2001-2015, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

import docker_wrapper
import glob
import logging
import psycopg2
import os
import zipfile

from contextlib import contextmanager
from navitiacommon import utils, process
from typing import Any, Generator, List

"""
This module contains all the functions to prepare a job, to call the binaries that ingest input data (all the "*2ed" binaries),
into a database and then call "ed2nav" to produce a single ".nav.lz4" file.
"""

ALEMBIC_PATH_ED = os.environ.get('ALEMBIC_PATH', '../sql')
ALEMBIC_PATH_CITIES = os.environ.get('ALEMBIC_PATH_CITIES', '../cities')


@contextmanager
def cd(new_dir):
    # type: (str) -> Generator
    """
    Change the current directory.

    :param new_dir: the new directory to move into
    """
    prev_dir = os.getcwd()  # type: str
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


def binarize(ed_db_params, output, ed_component_path, cities_db_params):
    # type: (docker_wrapper.DbParams, str, str, docker_wrapper.DbParams) -> None
    """
    Binarize the data from the database to a file.

    :param ed_db_params: the parameters of the database
    :param output: the name of the output file (usually with extension ".nav.lz4")
    :param ed_component_path: the path to the "ed2nav" binary
    :param cities_db_params: the parameters for the cities of the database
    """
    logger = logging.getLogger(__name__)  # type: logging.Logger
    logger.info('creating data.nav')
    ed2nav = 'ed2nav'
    if ed_component_path:
        ed2nav = os.path.join(ed_component_path, ed2nav)
    process.run(
        ed2nav,
        [
            "-o",
            output,
            "--connection-string",
            ed_db_params.old_school_cnx_string(),
            "--cities-connection-string",
            cities_db_params.old_school_cnx_string(),
        ],
    )
    logger.info("data.nav is created successfully: {}".format(output))


def import_data(data_dir, db_params, ed_component_path):
    # type: (str, docker_wrapper.DbParams, str) -> None
    """
    Call the right binary for its data (all the "*2ed") to create data then load it in the database.

    :param data_dir: the directory containing the data for "*2ed"
    :param db_params: the parameters of the database
    :param ed_component_path: the path of the folder containing the binary "*2ed"
    """
    log = logging.getLogger(__name__)  # type: logging.Logger
    files = glob.glob(data_dir + "/*")  # type: List[str]
    data_type, file_to_load = utils.type_of_data(files)  # type: str,str
    if not data_type:
        log.info('unknown data type for dir {}, skipping'.format(data_dir))
        return

    # we consider that we only have to load one kind of data per directory
    import_component = data_type + '2ed'  # type: str
    if ed_component_path:
        import_component = os.path.join(ed_component_path, import_component)

    if file_to_load.endswith('.zip') or file_to_load.endswith('.geopal'):
        # TODO: handle geopal as non zip ; if it's a zip, we unzip it
        zip_file = zipfile.ZipFile(file_to_load)  # type: zipfile.ZipFile
        zip_file.extractall(path=data_dir)
        file_to_load = data_dir

    if process.run(
        import_component, ["-i", file_to_load, "--connection-string", db_params.old_school_cnx_string()], log
    ):
        raise Exception('Error: problem with running {}, stoping'.format(import_component))


def load_cities(cities_file, cities_db_params, cities_exec_path):
    # type: (str, docker_wrapper.DbParams, str) -> None
    """
    Load cities in the database.

    :param cities_file: the path to the directory containing the data for the "ed2nav" binary
    :param cities_db_params: the parameters of the database
    :param cities_exec_path: the path of the folder containing the "cities" binary
    """
    logger = logging.getLogger(__name__)  # type: logging.Logger

    cities_exec = os.path.join(cities_exec_path, 'cities')  # type: str

    if process.run(
        cities_exec, ["-i", cities_file, "--connection-string", cities_db_params.old_school_cnx_string()]
    ):
        raise Exception('Error: problem with running {}, stoping'.format(cities_exec))


def load_data(data_dirs, ed_db_params, ed_component_path):
    # type: (List[str], docker_wrapper.DbParams, str) -> None
    """
    Load all data in the database.

    :param data_dirs: the directory containing all the data ("*.osm", "*.gtfs", ...)
    :param ed_db_params: the parameters of the database
    :param ed_component_path: the path of the folder containing all the binaries for data ("*2ed" and "ed2nav")
    """
    logging.getLogger(__name__).info('loading {}'.format(data_dirs))

    for d in data_dirs:
        import_data(d, ed_db_params, ed_component_path)


def update_db(db_params, alembic_path):
    # type: (docker_wrapper.DbParams, str) -> None
    """
    Update the database by enabling Postgre/PostGIS and update it's scheme.

    :param db_params: the parameters of the database
    :param alembic_path: the path to the folder containing the "alembic" binary
    """
    cnx_string = db_params.cnx_string()  # type: str

    cnx = psycopg2.connect(
        database=db_params.dbname, user=db_params.user, password=db_params.password, host=db_params.host
    )  # type: psycopg2.connection
    c = cnx.cursor()  # type: psycopg2.connection.cursor
    c.execute("create extension postgis;")
    c.close()
    cnx.commit()

    logging.getLogger(__name__).info('message = {}'.format(c.statusmessage))

    with cd(alembic_path):
        res = os.system(
            'PYTHONPATH=. alembic -x dbname="{cnx}" upgrade head'.format(cnx=cnx_string)
        )  # type: Any

        if res:
            raise Exception('problem with db update')


def generate_nav(
    data_dir, docker_ed, docker_cities, output_file, ed_component_path, cities_exec_path, import_cities
):
    # type: (str, docker_wrapper.PostgresDocker, docker_wrapper.PostgresDocker, str, str, str, str) -> None
    """
    Load all data from a directory to an single output file.
    It can load all the data directly from the directory or in each sub-directories for each data kind.

    :param data_dir: the path of the directory containing all the data ("*.osm", "*.gtfs", ...)
    :param docker_ed: the Docker for the "*2ed" binaries
    :param docker_cities: the Docker for the "cities" binary
    :param output_file: the name of the output file (usually with extension ".nav.lz4")
    :param ed_component_path: the path of the folder containing all the binaries for data ("*2ed" and "ed2nav")
    :param cities_exec_path: the path of the folder containing the "cities" binary
    :param import_cities: the path to the directory containing the data for the "ed2nav" binary
    """
    cities_db_params = docker_cities.get_db_params()
    update_db(cities_db_params, ALEMBIC_PATH_CITIES)

    ed_db_params = docker_ed.get_db_params()  # type: docker_wrapper.DbParams
    update_db(ed_db_params, ALEMBIC_PATH_ED)

    if import_cities:
        if not os.path.exists(import_cities):
            raise Exception('Error: impossible to find {}, exiting'.format(import_cities))

        load_cities(import_cities, cities_db_params, cities_exec_path)

    if not os.path.exists(data_dir):
        raise Exception('Error: impossible to find {}, exiting'.format(data_dir))

    data_dirs = [
        os.path.join(data_dir, sub_dir_name)
        for sub_dir_name in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, sub_dir_name))
    ] or [
        data_dir
    ]  # if there is no sub dir, we import only the files in the dir

    load_data(data_dirs, ed_db_params, ed_component_path)

    binarize(ed_db_params, output_file, ed_component_path, cities_db_params)
