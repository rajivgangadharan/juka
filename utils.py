#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Copyright 2017 Rajiv Gangadharan <rajiv.gangadharan@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
# Module Jira Utilities for Maintaining Data. Rajiv Gangadharan (Sep.2017)

from jira import JIRA, JIRAError
import argparse
import os.path
from pathlib import Path
import yaml

class ConfigFile:
    config = {}
    file_string = ""

    def __init__(self, file_string):
        self.config = {}
        self.file_string = file_string
        if (self.is_exists()):
            self.read()

    def read(self):
        with open(self.file_string, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, yaml.SafeLoader)
        self.config['username'] = cfg['jira']['username']
        self.config['password'] = cfg['jira']['password']
        self.config['server'] = cfg['jira']['server']
        self.config['project_info'] = cfg['project']

    def get_board_id(self, project_key):
        for p in self.config['project_info']:
            if (p['key'] == project_key):
                return(p['board'])
        return None

    def get_team_id(self, project_key):
        for p in self.config['project_info']:
            if (p['key'] == project_key):
                return(p['team'])
        return None

    def is_exists(self):
        f = Path(self.file_string)
        if f.is_file():
            return True
        else:
            return False

class JiraConn:
    jira = None
    username = None
    password = None
    server = None
    options = None

    def __init__(self, username, password, server):
        self.options = {'server': server}
        self.username = username
        self.password = password
        self.server = server
        self.jira_connect()
        
    def jira_connect(self):
        assert(self.server != None)
        try:
            self.jira = JIRA(self.options,
                    basic_auth=(self.username,
                    self.password),
                    validate=True)
        except JIRAError as e:
            print("Failed Jira connect - {:d} - {:s}"\
                .format(e.status_code, e.text))
            exit(1)

class RunParams:
    mode = None # Query --query or Fix --fix
    project = None #
    sprint = None #
    username = None
    password = None
    server = None

    def __init__(self):
        self.parse_params()

    def parse_params(self):
        parser = argparse.ArgumentParser(description='Query and update issues')
        parser.add_argument('-u',
                help="Provide User Name")
        parser.add_argument('-p',
                help="Provide Password")
        parser.add_argument('-s',
                help="Provide Server URL")
        parser.add_argument('project_sprint',
                help="Specify the project and sprint in the form project:sprint")
        args = parser.parse_args()
        self.username = args.u
        self.password = args.p
        self.server = args.s
        (self.project, self.sprint) = args.project_sprint.split(":")

class SprintBoard:
    board_id  = None
    sprints = None
    def __init__(self, jira, board_id):
        assert(board_id != None)
        self.board_id = board_id
        self.sprints = jira.sprints(self.board_id)

    def list_sprints(self):
        print('Printing {:d} Sprints'.format(len(self.sprints)))
        for s in self.sprints:
            print("{:s} (id: {:d}) [{:s}]".format(s.name, s.id, s.state))

    def get_sprints(self):
        return(self.sprints)

class Metrics:
    boards = None
    epics_for_planned_iteration = None

    def __init__(self, jira):
        try:
            self.boards = jira.boards()
        except JIRAError as e:
            print('Failed updating fields {0} {1}'.\
                format(e.status_code, e.text))
            exit(1)

    def list_boards(self):
        for b in self.boards:
            print(b.name,"[","id:",b.id,"]")

    def get_board_name_by_id(self, id):
        for b in self.boards:
            if b.id == id:
                return(b.name)

    def get_board_id_by_name(self, name):
        for b in self.boards:
            if b.name == name:
                return(b.id)

    def percentage(self, part, whole):
        assert(whole != 0)
        try:
            if (part is None):
                raise TypeError("part is of type None")
            if (whole is None):
                raise TypeError("whole is of type None")
            return (100 * (float(part)/float(whole)))
        except AssertionError as err:
            print("whole is {} and part is {}".format(whole, part))
            raise
        except ZeroDivisionError as err:
            print("Divide by Zero, aborting.")
            raise
        except TypeError as err:
            print("Exception raised ", err)
            raise

    def get_fixable_issues(self):
        jql_str = "project= "    + self.project + \
                " AND (\'Team/s\' is Empty OR \"Planned Iteration\" is Empty) "+ \
                " AND type = Story"
        issues = jira.search_issues(jql_str)
        return(issues)

    def fix_release_data(self, issues, release):
        for issue in issues:
            i = jira.issue(issue)
            print("Updating issue :", i.key)
            if (i.fields.issuetype.name in ("Epic", "Story")):
                try:
                    i.update(fields={"customfield_14401":release})
                except JIRAError as e:
                    print('Failed updating fields {0} {1}'.format(e.status_code,
                        e.text))
                    exit(1)

                print("Updated.")

class Issue:
    key = None
    i = None
    jira = None
    summary = None

    def __init__(self, jira, issue_key):
        assert(issue_key != None)
        self.jira = jira
        self.i = jira.issue(issue_key)
        self.key = issue_key
        self.summary = self.i.fields.summary

    def available_transitions(self):
        try:
            transitions = self.jira.transitions(self.i)
            [print(t['id'], t['name']) for t in transitions]
        except JIRAError as e:
            print("Updating new estimate failed with {} and {}"\
                    .format(e.status_code, e.text))
            raise

    def get_estimate_in_story_points(self):
        pass
        # Yet to be implemented in a implementation independant way

    def set_epic(self, epic):
        try:
            self.i.update(fields={'customfield_13300':epic})
        except JIRAError as e:
            print("Updating epic field failed with {} and {}"\
                            .format(e.status_code, e.text))
            raise

    def descope(self):
        try:
            self.i.update(fields={'customfield_14401':''})
        except JIRAError as e:
            print("Descoping failed with error {} and {}"\
                    .format(e.status_code, e.text))
            raise

    def scope(self, release_string):
        try:
            self.i.update(fields={'customfield_14401':release_string})
        except JIRAError as e:
            print("Scoping failed with error {} and {}"\
                    .format(e.status_code, e.text))

    def get_planned_iteration(self):
        try:
            if (self.i.fields.customfield_14401 is None):
                return("backlog")
            else:
                return(self.i.fields.customfield_14401)
        except JIRAError as e:
            print("Scoping failed with error {:s} and {:s}"\
                    .format(e.status_code, e.text))
            return(None)

    def set_release(self, release_string, action="add"):
        release_list = []
        if (action is None or action == "add"):
            release_list.append(release_string)
        elif (action == "remove"):
            release_list.remove(release_string)
        else:
            release_list = []
            release_list.append(release_string)
        try:
            if (self.i.fields.customfield_14401 is None):
                return("Untagged for a release")
            else:
                print("Updating fixVersions to ", release)
                self.i.update(fields={'fixVersions':release_list})
        except JIRAError as e:
            print("Scoping failed with error {} and {:s}".format(e.status_code, e.text))
            return(None)

    def assign_team(self, team_code):
        try:
            for t in self.i.fields.customfield_14400:
                teams.append(t)
            teams = teams.append(team_code)
            self.i.update(fields={'customfield_14400':teams})
            return(self.i.fields.customfield_14400) # Returning the new team list
        except JIRAError as e:
            print("Team assignment failed with error {} and {:s}".format(e.status_code, e.text))

    def unassign_team(self, team_code):
                try:
                    for t in self.i.fields.customfield_14400:
                        if (t != team_code):
                            teams.append(t)
                    self.i.update(fields={'customfield_14400':teams})
                    return(self.i.fields.customfield_14400) # Returning the new team list
                except JIRAError as e:
                    print("Team assignment failed with error {} and {:s}".format(e.status_code, e.text))

    def unassign_all_teams(self):
        try:
            self.i.update(fields={'customfield_14400':""})
        except JIRAError as e:
            print("Team assignment failed with error {} and {:s}"\
                    .format(e.status_code, e.text))

    def show_teams(self):
        try:
            for t in self.i.fields.customfield_14400:
                print(t)
        except JIRAError as e:
            print("Team assignment failed with error {} and {:s}"\
                    .format(e.status_code, e.text))

    def tag(self, tag_list):
        try:
            self.i.update(fields={'labels':tag_list})
        except JIRAError as e:
            print("Scoping failed with error {} and {:s}"\
                    .format(e.status_code, e.text))

    def detag_all(self):
        try:
            self.i.update(fields={'labels':""})
        except JIRAError as e:
            print("Scoping failed with error {} and {:s}"\
                    .format(e.status_code, e.text))

    def detag(self, detag_list):
        try:
            tags = self.i.fields.labels
            tag_list = [x for x in tags if x not in detag_list]
            self.tag(tag_list)
        except JIRAError as e:
            print("Scoping failed with error {} and {:s}"\
                    .format(e.status_code, e.text))

    def show_tags(self):
        try:
            tags = self.i.fields.labels
        except JIRAError as e:
            print("Scoping failed with error {} and {:s}"\
                    .format(e.status_code, e.text))
        for t in tags:
            print(t)

class DeferredEpics:
    deferred_epics = None
    deferred_epic_keys = None
    jira = None

    def __init__(self, jira, project_key):
        self.jira= jira
        deferred_epic_jql = " project = "+ project_key + \
                    " AND Type = Epic AND status = Deferred "
        self.deferred_epics = self.jira.search_issues(deferred_epic_jql)
        self.deferred_epic_keys = [d.key for d in self.deferred_epics]


    def list_deferred_epics(self):
        for d in self.deferred_epics:
            print('Epic {:s} {:10s} Planned Iter: {}'\
                .format(d.key, d.fields.summary, d.fields.customfield_14401 ))

    def list_deffered_epics_keys(self):
        for k in selfdeferred_epic_keys:
            print(k)

    def descope_all_deffered_epics(self, issue_id):
        for d in self.deferred_epics:
            d.update(fields={'customfield_14401':''})

    def descope_specified_deferred_epics(self, issue_keys):
        for i in issue_keys:
            if i in self.deferred_epic_keys:
                try:
                    epic = Issue(self.jira, i)
                    epic.descope()
                    print("Issue {:s} descoped successfully.".format(i))
                except JIRAError as e:
                    print("Descoping issue {:s} unsuccessful.".format(i))
                    print("with Error {:s} and {:s}".format(e.status_code, e.text))

            else:
                print("Deferred issue lookup failed, skipping ", i)


class Epic(Issue):
    issues = None
    stories = None
    closed_stories = None
    story_point_aggregate = 0
    closed_story_point_aggregate = 0
    percentage_complete = 0

    def __init__(self, jira, key):
        Issue.__init__(self, jira, key)
        self.get_issues()
        self.get_stories()
        self.get_closed_stories()
        self.story_point_aggregate = self.aggregate_estimate_for_all_stories()
        self.closed_story_point_aggregate = self.aggregate_estimate_for_closed_stories()
        try:
            story_point_aggregate = None
            # So that there is no DivideByZero exception
            if (self.story_point_aggregate == 0):
                story_point_aggregate = 1
            else:
                story_point_aggregate = self.story_point_aggregate
            self.percentage_complete = \
                Metrics.percentage(self.closed_story_point_aggregate, story_point_aggregate)
        except ZeroDivisionError as err:
            print("Divide by Zero while calculating % Completion ", err)
            raise


    def aggregate_estimates(self, issues):
        agg = 0
        for i in issues:
            if (i.fields.customfield_11213 == None):
                agg += 0
            else:
                agg += i.fields.customfield_11213
        return(agg)

    def aggregate_estimate_for_all_stories(self):
        return(self.aggregate_estimates(self.stories))

    def aggregate_estimate_for_closed_stories(self):
        return(self.aggregate_estimates(self.closed_stories))

    def get_issues(self):
        jql_get_issues = "cf[13300] = " + self.i.key
        self.issues = self.jira.search_issues(jql_get_issues)

    def get_stories(self):
        jql_get_stories = "cf[13300] = " + self.i.key + " AND Type = Story"
        self.stories = self.jira.search_issues(jql_get_stories)

    def get_closed_stories(self):
        jql_get_closed_stories = "cf[13300] = " + self.i.key + \
        " AND Type = Story" + \
        " AND Status in (Resolved, Closed, Accepted, Verified, Closed, Done) "
        self.closed_stories = self.jira.search_issues(jql_get_closed_stories)

    def print_stories(self):
        print("{:10s} | {:40s} | {:10s} | {:5s} | {:10s}".format("Key","Summary","Status", "Est.","Release"))
        for s in self.stories:
            if (s.fields.customfield_11213 is None):
                estimate = 0
            else:
                estimate = s.fields.customfield_11213
                print("{:10s} | {:40s} | {:10s} | {:5.2f} | {}".\
                    format(s.key, s.fields.summary[0:40],
                        s.fields.status.name, estimate,
                        "Backlog" if s.fields.customfield_14401 is None else s.fields.customfield_14401))

    def print_issues(self):
        print("{:10s} | {:8s} | {:40s} | {:10s} | {:5s} | {:10s}".\
                format("Key","Type", "Summary","Status","Est.","Release"))
        for s in self.issues:
            if (s.fields.customfield_11213 is None):
                estimate = 0
            else:
                estimate = s.fields.customfield_11213
                print("{:10s} | {:8s} | {:40s} | {:10s} | {:5.2f} | {:10s}".\
                format(s.key, s.fields.issuetype.name, \
                    s.fields.summary[0:40], s.fields.status.name, \
                            estimate, \
                            "Backlog" if s.fields.customfield_14401 is None else s.fields.customfield_14401))

    def print_closed_stories(self):
        for s in self.closed_stories:
            if (s.fields.customfield_11213 is None):
                estimate = 0
            else:
                estimate = s.fields.customfield_11213
            print("{:s} | {:s} | {:10s} Est {:f}"\
                    .format(s.key, s.fields.issuetype.name,\
                    s.fields.summary, estimate))

    def get_bottom_up_estimate(self):
        return self.story_point_aggregate

    def get_bottom_up_estimate_for_sprint(self, sprint_string):
        jql_get_stories_in_sprint = "project = SCCS and cf[11701] ="+ sprint_string \
                      + " and cf[13300] = " + self.i.key
        try:
            issues = jira.search_issues(jql_get_stories_in_sprint)
            estimates = \
                [0 if e.fields.customfield_11213 is None else i.fields.customfield_11213 \
                for i in issues \
                if i.fields.issuetype.name == "Story"]
            return (sum(estimates))
        except JIRAError as e:
            print("Caught error {} {}".format(e.status_code, e.text))
            raise

    def get_bottom_up_estimate_for_planned_iteration(self, planned_iteration_string):
        try:
            estimates_of_epics_for_planned_iteration = \
                [0 if e.fields.customfield_11213 is None else e.fields.customfield_11213 \
                for e in self.stories \
                if e.fields.customfield_14401 == planned_iteration_string]
            return(sum(estimates_of_epics_for_planned_iteration))
        except JIRAError as e:
            print("Caught error {} {}".format(e.status_code, e.text))
            raise

    def fix_estimate(self, planned_iteration_string):
        try:
             pi_estimate_for_epic = self.get_bottom_up_estimate_for_planned_iteration(planned_iteration_string)
             self.set_estimate_in_story_points(pi_estimate_for_epic)
        except JIRAError as e:
             print("Caught error {} {}".format(e.status_code, e.text))
             raise
