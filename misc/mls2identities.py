#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Daniel Izquierdo-Cortazar <dizquierdo@bitergia.com>

#
# mls2identities.py
#
# This script is based on the outcomes of unifypeople.py used in the CVSAnalY
# database. This checks information about name and email from the email accounts
# found in the people table (outcomes of the MLStats tool). If this is found,
# then the table people_upeople is populated with the upeople_id found in identities.
# If not, a new entry in identities table is generated and its correspondant link
# to the people_upeople table.


import MySQLdb
import sys
import re

def connect(database):
   user = 'xxx'
   password = 'xxx'
   host = 'xxx'
   try:
      db =  MySQLdb.connect(host,user,password,database)
      return db, db.cursor()
   except:
      print("Database connection error")


def execute_query(connector, query):
   results = int (connector.execute(query))
   cont = 0
   if results > 0:
      result1 = connector.fetchall()
      return result1
   else:
      return []

def create_tables(db, connector):
   connector.execute("DROP TABLE IF EXISTS people_upeople")
   connector.execute("""CREATE TABLE people_upeople (
                               people_id varchar(256) NOT NULL,
                               upeople_id int(11) NOT NULL,
                               PRIMARY KEY (people_id)
                  ) ENGINE=MyISAM DEFAULT CHARSET=utf8""")
   connector.execute("ALTER TABLE people_upeople DISABLE KEYS")
   db.commit()

   return



def main(db_mls, db_identities):
   # db_mls: MLStats database
   # db_identities: Identities database

   db_mlstats, connector_mls = connect(db_mls)
   db_ids, connector_ids = connect(db_identities)

   create_tables(db_mlstats, connector_mls)

   query = "select name, email_address from people"
   results = execute_query(connector_mls, query)
   for result in results:
      name = result[0]
      name = name.replace("'", "\\'") #avoiding ' errors in MySQL
      email = result[1]
      email = email.replace("'", "\\'") #avoiding ' errors in MySQL
      query = "select upeople_id from identities where identity='" + name  + "' or identity='"+ email +"';"
      results_ids = execute_query(connector_ids, query)
      if len(results_ids) > 0:
         # there exist such identity
         upeople_id = int(results_ids[0][0])
         query = "insert into people_upeople(people_id, upeople_id) " +\
                 "values('"+email+"', "+str(upeople_id)+");"
         execute_query(connector_mls, query)
      else:
         #Insert in people_upeople, identities and upeople (new identitiy)
 
         # Max (upeople_)id from upeople table
         query = "select max(id) from upeople;"
         results = execute_query(connector_ids, query)
         upeople_id = int(results[0][0]) + 1
         
         query = "insert into upeople(id) values("+ str(upeople_id) +");"
         execute_query(connector_ids, query)
         
         query = "insert into identities(upeople_id, identity, type)" +\
                 "values(" + str(upeople_id) + ", '"+name+"', 'name');"
         execute_query(connector_ids, query)
 
         query = "insert into identities(upeople_id, identity, type)" +\
                 "values(" + str(upeople_id) + ", '"+email+"', 'email');"
         execute_query(connector_ids, query)

         query = "insert into people_upeople(people_id, upeople_id) " +\
                 "values('"+email+"', "+str(upeople_id)+");"
         print query
         execute_query(connector_mls, query)

   db_ids.commit()
   return 



if __name__ == "__main__":main(sys.argv[1], sys.argv[2])


