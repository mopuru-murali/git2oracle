#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gitana imports and digests the data of Git repositories to a relational database
It also provides support to generate project activity reports.
"""

from dbschema import DbSchema
from git2db_extract_main import Git2DbMain
from git2db_update import Git2DbUpdate
#from exporters.report.report_exporter import ReportExporter
#from exporters.graph.graph_exporter import GraphExporter
from logging_util import LoggingUtil
import os
import glob
import subprocess


class Git2Oracle(object):
    """
    This is the main class you instanciate to use Git2Oracle functionalities
    """

    LOG_FOLDER_PATH = "logs"
    LOG_NAME = "git2oracle"

    def __init__(self, config, log_folder_path=None):
        """
        :type config: dict
        :param config: the DB configuration file

        :type log_folder_path: str
        :param log_folder_path: the log folder path
        """
        self._config = config

        if log_folder_path:
            self.create_log_folder(log_folder_path)
            self._log_folder_path = log_folder_path
        else:
            self.create_log_folder(self.LOG_FOLDER_PATH)
            self._log_folder_path = self.LOG_FOLDER_PATH

        self._log_path = os.path.join(self._log_folder_path,
                                      Git2Oracle.LOG_NAME + "-")
        self._logging_util = LoggingUtil()
        self._logger = self._logging_util.get_logger(self._log_path + "init-schema")
        self._fileHandler = self._logging_util.get_file_handler(self._logger, self._log_path, "info")

    def __del__(self):
        # deletes the file handler of the logger
        self._logging_util.remove_file_handler_logger(self._logger, self._fileHandler)

    def create_log_folder(self, name):
        """
        creates the log folder

        :type name: str
        :param name: the log folder path
        """
        if not os.path.exists(name):
            os.makedirs(name)

    def delete_previous_logs(self):
        """
        deletes the content of the log folder
        """
        files = glob.glob(self._log_folder_path + "/*")
        for f in files:
            try:
                os.remove(f)
            except:
                continue

    def init_schema(self, config):
        """
        initializes the Gitana DB schema

        If a DB having a name equal already exists in Gitana, the existing DB will be dropped and a new one will be created
        """
        # db = DbSchema(self._config, self._log_path)
        # db.init_database(db_name)
        script = subprocess.Popen(
            'echo exit | sqlplus {user}/{password}@{dsn} @gitana.sql'.format(**config),
            stdin=subprocess.PIPE, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT, shell=True)
        out, err = script.communicate()
        self._logger.info(out)
        self._logger.error(err)

    def create_project(self, project_name):
        """
        inserts a project in the DB

        :type db_name: str
        :param db_name: the name of an existing DB

        :type project_name: str
        :param project_name: the name of the project to create. It cannot be null
        """
        db = DbSchema(self._config, self._log_path)
        db.create_project(project_name)

    def import_git_data(self, project_name, repo_name, git_repo_path, before_date, import_type, references):
        """
        imports Git data to the DB

        :type project_name: str
        :param project_name: the name of an existing project in the DB

        :type repo_name: str
        :param repo_name: the name of the repository to import. It cannot be null

        :type git_repo_path: str
        :param git_repo_path: the local path of the repository. It cannot be null

        :type before_date: str
        :param before_date: import data before date (YYYY-mm-dd). It can be null

        :type import_type: int
        :param import_type: 1 = do not import patch content, 2 = import patch content but not at line level, 3 = import patch content at line level

        :type references: list str
        :param references: list of references (branches and tags) to import. It can be null or ["ref-name-1", .., "ref-name-n"]
        """
        git2db = Git2DbMain(project_name,
                            repo_name, git_repo_path, before_date, import_type, references,
                            self._config, self._log_path)
        git2db.extract()

    def update_git_data(self, db_name, project_name, repo_name, git_repo_path, before_date, processes):
        """
        updates the Git data stored in the DB

        :type db_name: str
        :param db_name: the name of an existing DB

        :type project_name: str
        :param project_name: the name of an existing project in the DB

        :type repo_name: str
        :param repo_name: the name of an existing repository in the DB to update

        :type git_repo_path: str
        :param git_repo_path: the path of the repository. It cannot be null

        :type before_date: str
        :param before_date: import data before date (YYYY-mm-dd). It can be null

        :type processes: int
        :param processes: number of processes to import the data. If null, the default number of processes is used (10)
        """
        git2db = Git2DbUpdate(db_name, project_name,
                              repo_name, git_repo_path, before_date, processes,
                              self._config, self._log_path)
        git2db.update()

    # def export_to_graph(self, db_name, graph_json_path, output_path):
    #     """
    #     exports the data stored in the Gitana DB to a graph (gexf format)
    #
    #     :type db_name: str
    #     :param db_name: the name of an existing DB
    #
    #     :type graph_json_path: str
    #     :param graph_json_path: the path of the JSON that drives the export process
    #
    #     :type output_path: str
    #     :param output_path: the path where to export the graph
    #     """
    #     exporter = GraphExporter(self._config, db_name, self._log_path)
    #     exporter.export(output_path, graph_json_path)
    #
    # def export_to_report(self, db_name, report_json_path, output_path):
    #     """
    #     exports the data stored in the Gitana DB to an HTML report
    #
    #     :type db_name: str
    #     :param db_name: the name of an existing DB
    #
    #     :type report_json_path: str
    #     :param report_json_path: the path of the JSON that drives the export process
    #
    #     :type output_path: str
    #     :param output_path: the path where to export the report
    #     """
    #     exporter = ReportExporter(self._config, db_name, self._log_path)
    #     exporter.export(output_path, report_json_path)


def main():
    """
    main
    """
    config = {
        'user': 'tst_git_dwh',
        'password': 'T6gitca$hC1W',
        'dsn': 'TRDAPD',
    }
    g = Git2Oracle(config)
    g.delete_previous_logs()
    g.create_project('vcf')
    g.import_git_data(
        'vcf', 'vcf_audit_repo', 'C:\\Users\\mmopuru\\Downloads\\vcf-audit',
        None, 1, None)
    #g.export_to_graph("_hwim_db", "./graph.json", "./graph.gexf")
    #g.export_to_report("_hwim_db", "./report.json", "./report.html")

if __name__ == "__main__":
    main()