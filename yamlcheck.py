#!/usr/bin/env python
from utils import ConfigFile
cf = ConfigFile('config.yaml')
cfg = cf.config
username = cfg['username']
password = cfg['password']
server = cfg['server']
project_info = cfg['project_info']
print("Board is {} Team id is {}".format(cf.get_board_id('SCCS'), cf.get_team_id('SCCS')))
