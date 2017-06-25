#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from git2db_extract_reference import Git2DbReference
from git_dao import GitDao
from logging_util import LoggingUtil
from querier_git import GitQuerier
import multiprocessing
import multiprocessing_util


class Git2DbMain(object):
    """
    This class handles the import of Git data
    """

    NUM_PROCESSES = 10

    def __init__(self, project_name, repo_name, git_repo_path,
                 before_date, import_type, references, config, log_root_path):
        """
        :type project_name: str
        :param project_name: the name of an existing project in the DB

        :type repo_name: str
        :param repo_name: the name of the Git repository to import

        :type git_repo_path: str
        :param git_repo_path: the local path of the Git repository

        :type before_date: str
        :param before_date: import data before date (YYYY-mm-dd)

        :type import_type: int
        :param import_type: 1 does not import patches, 2 imports patches but not at line level, 3 imports patches with line detail

        :type references: list str
        :param references: list of references to import

        :type config: dict
        :param config: the DB configuration file

        :type log_root_path: str
        :param log_root_path: the log path
        """
        self._log_path = log_root_path + "import-git-" + project_name + "-" + repo_name
        self._git_repo_path = git_repo_path
        self._project_name = project_name
        self._repo_name = repo_name
        self._before_date = before_date
        self._import_type = import_type
        self._references = references
        self._config = config

        self._logging_util = LoggingUtil()

        self._logger = None
        self._fileHandler = None
        self._querier = None
        self._dao = None

    def _get_existing_references(self, repo_id):
        # retrieves already imported references
        existing_refs = []

        cursor = self._dao.get_cursor()
        query = "SELECT ref.name " \
                "FROM reference ref JOIN repository r ON ref.repo_id = r.id " \
                "WHERE r.id = :repo_id"
        cursor.execute(query, {'repo_id': repo_id})

        row = cursor.fetchone()
        while row:
            existing_refs.append(row[0])
            row = cursor.fetchone()
        cursor.close()

        return existing_refs

    def _get_info_contribution(self, repo_id):
        #processes Git data
        existing_refs = self._get_existing_references(repo_id)

        queue_references = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        # Start consumers
        multiprocessing_util.start_consumers(Git2DbMain.NUM_PROCESSES, queue_references, results)

        for reference in self._querier.get_references():
            if self._references:
                if reference[0] in self._references:
                    git_ref_extractor = Git2DbReference(self._db_name, repo_id, self._git_repo_path,
                                                        self._before_date, self._import_type, reference[0], "",
                                                        self._config, self._log_path)

                    queue_references.put(git_ref_extractor)
            else:
                if reference[0] not in existing_refs:
                    git_ref_extractor = Git2DbReference(repo_id, self._git_repo_path,
                                                        self._before_date, self._import_type, reference[0], "",
                                                        self._config, self._log_path)

                    queue_references.put(git_ref_extractor)

        # Add end-of-queue markers
        multiprocessing_util.add_poison_pills(Git2DbMain.NUM_PROCESSES, queue_references)

        # Wait for all of the tasks to finish
        queue_references.join()

    def extract(self):
        """
        extracts Git data and stores it in the DB
        """
        try:
            self._logger = self._logging_util.get_logger(self._log_path)
            self._fileHandler = self._logging_util.get_file_handler(self._logger, self._log_path, "info")

            self._logger.info("Git2DbMain started")
            start_time = datetime.now()

            self._querier = GitQuerier(self._git_repo_path, self._logger)
            self._dao = GitDao(self._config, self._logger)

            project_id = self._dao.select_project_id(self._project_name)
            self._dao.insert_repo(project_id, self._repo_name)
            repo_id = self._dao.select_repo_id(self._repo_name)
            #info contribution does not need a connection to the db
            self._get_info_contribution(repo_id)
            #self._dao.restart_connection()
            self._dao.fix_commit_parent_table(repo_id)
            end_time = datetime.now()
            minutes_and_seconds = self._logging_util.calculate_execution_time(end_time, start_time)
            self._logger.info("Git2DbMain finished after " + str(minutes_and_seconds[0])
                         + " minutes and " + str(round(minutes_and_seconds[1], 1)) + " secs")
            self._logging_util.remove_file_handler_logger(self._logger, self._fileHandler)
        except Exception, e:
            self._logger.error("Git2DbMain failed", exc_info=True)
        finally:
            if self._dao:
                self._dao.close_connection()
