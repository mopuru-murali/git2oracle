#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cx_Oracle


class DbUtil(object):
    """
    This class provides database utilities
    """

    def get_connection(self, config):
        """
        gets DB connection

        :type config: dict
        :param config: the DB configuration file
        """
        return cx_Oracle.connect(**config)

    def close_connection(self, cnx):
        """
        closes DB connection

        :type cnx: Object
        :param cnx: DB connection to close
        """
        cnx.close()

    def lowercase(self, str):
        """
        conver str to lowercase

        :type str: str
        :param str: str to convert
        """
        if str:
            str = str.lower()

        return str

    def select_project_id(self, cnx, project_name, logger):
        """
        gets project id

        :type cnx: Object
        :param cnx: DB connection

        :type project_name: str
        :param project_name: name of the project

        :type logger: Object
        :param logger: logger
        """
        found = None
        cursor = cnx.cursor()
        query = "SELECT p.id " \
                "FROM project p " \
                "WHERE p.name = :project_name"
        cursor.execute(query, [project_name])
        row = cursor.fetchone()

        if row:
            found = row[0]
        else:
            logger.error("the project " + str(project_name) + " does not exist")

        cursor.close()
        return found

    def insert_repo(self, cnx, project_id, repo_name, logger):
        """
        inserts repository

        :type cnx: Object
        :param cnx: DB connection

        :type project_id: int
        :param project_id: id of the project

        :type repo_name: str
        :param repo_name: name of the repository

        :type logger: Object
        :param logger: logger
        """
        cursor = cnx.cursor()
        query = "INSERT INTO repository(project_id, name) " \
                "VALUES (:project_id, :repo_name)"
        cursor.execute(query, [project_id, repo_name])
        cnx.commit()
        cursor.close()

    def select_repo_id(self, cnx, repo_name, logger):
        """
        selects repository id

        :type cnx: Object
        :param cnx: DB connection

        :type repo_name: str
        :param repo_name: name of the repository

        :type logger: Object
        :param logger: logger
        """
        found = None
        cursor = cnx.cursor()
        query = "SELECT id " \
                "FROM repository " \
                "WHERE name = :repo_name"
        cursor.execute(query, [repo_name])

        row = cursor.fetchone()

        if row:
            found = row[0]
        else:
            logger.error("the repository " + repo_name + " does not exist")

        cursor.close()
        return found

    def insert_user(self, cnx, name, email, logger):
        """
        inserts user

        :type cnx: Object
        :param cnx: DB connection

        :type name: str
        :param name: name of the user

        :type email: str
        :param email: email of the user

        :type logger: Object
        :param logger: logger
        """
        cursor = cnx.cursor()
        query = "INSERT INTO users(name, email) " \
                "VALUES (:name, :email)"
        cursor.execute(query, [name, email])
        cnx.commit()
        cursor.close()

    def select_user_id_by_email(self, cnx, email, logger):
        """
        selects user id by email

        :type cnx: Object
        :param cnx: DB connection

        :type email: str
        :param email: email of the user

        :type logger: Object
        :param logger: logger
        """
        found = None
        if email:
            cursor = cnx.cursor()
            query = "SELECT id " \
                    "FROM users " \
                    "WHERE email = :email"
            cursor.execute(query, [email])

            row = cursor.fetchone()
            if row:
                found = row[0]
            else:
                logger.warning("there is not user with this email " + email)

            cursor.close()
        return found

    def select_user_id_by_name(self, cnx, name, logger):
        """
        selects user id by name

        :type cnx: Object
        :param cnx: DB connection

        :type name: str
        :param name: name of the user

        :type logger: Object
        :param logger: logger
        """
        found = None
        if name:
            found = None
            cursor = cnx.cursor()
            query = "SELECT id " \
                    "FROM users " \
                    "WHERE name = %s"
            arguments = [name]
            cursor.execute(query, arguments)

            row = cursor.fetchone()

            if row:
                found = row[0]
            else:
                logger.warning("there is not user with this name " + name)

            cursor.close()
        return found

    # def set_database(self, cnx, db_name):
    #     """
    #     set database
    #
    #     :type cnx: Object
    #     :param cnx: DB connection
    #
    #     :type db_name: str
    #     :param db_name: name of the database
    #     """
    #     cursor = cnx.cursor()
    #     use_database = "USE " + db_name
    #     cursor.execute(use_database)
    #     cursor.close()

    # def set_settings(self, cnx):
    #     """
    #     set database settings
    #
    #     :type cnx: Object
    #     :param cnx: DB connection
    #     """
    #     cursor = cnx.cursor()
    #     cursor.execute("set global innodb_file_format = BARRACUDA")
    #     cursor.execute("set global innodb_file_format_max = BARRACUDA")
    #     cursor.execute("set global innodb_large_prefix = ON")
    #     cursor.execute("set global character_set_server = utf8")
    #     cursor.execute("set global max_connections = 500")
    #     cursor.close()

    # def restart_connection(self, config, logger):
    #     """
    #     restart DB connection
    #
    #     :type config: dict
    #     :param config: the DB configuration file
    #
    #     :type logger: Object
    #     :param logger: logger
    #     """
    #     logger.info("restarting connection...")
    #     return mysql.connector.connect(**config)
