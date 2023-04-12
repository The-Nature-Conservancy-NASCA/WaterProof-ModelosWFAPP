#!/usr/bin/python
from configparser import SafeConfigParser
import os


def config(filename='config/database.ini', section='postgresql'):
    # create a parser
    parser = SafeConfigParser(os.environ)
    # read config file
    parser.read(filename)

    host = parser.get(section,"host")
    database = parser.get(section,"database")
    user = parser.get(section,"user")
    password = parser.get(section,"password")

    # get section, default to postgresql
    db = {}

    db["host"] = host
    db["database"] = database
    db["user"]  = user
    db["password"] = password

    # if parser.has_section(section):
    #     params = parser.items(section)
    #     print(params)
    #     for param in params:
    #         db[param[0]] = param[1]
    # else:
    #     raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    # print(db)

    return db