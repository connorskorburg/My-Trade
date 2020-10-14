from django.db import models
import pymysql.cursors
import os
import re
from better_profanity import profanity
# Create your models here.

class MySQLConnection:
  def __init__(self, db):
    connection = pymysql.connect(host = 'localhost',
                                user = 'root',
                                password = os.environ.get('DB_PASS'),
                                db = db,
                                charset = 'utf8mb4',
                                cursorclass = pymysql.cursors.DictCursor,
                                autocommit = True)
    self.connection = connection
  
  def query_db(self, query, data=None):
    with self.connection.cursor() as cursor:
      try:
        query = cursor.mogrify(query, data)
        print("Running Query:", query)

        executable = cursor.execute(query, data)
        if query.lower().find('insert') >= 0:
          self.connection.commit()
          return cursor.lastrowid
        elif query.lower().find('select') >= 0:
          result = cursor.fetchall()
          return result
        else:
          self.connection.commit()
      except Exception as e:
        print("SOMETHING WENT WRONG:", e)
        return False
      finally:
        self.connection.close()

def connectToMySQL(db):
  return MySQLConnection(db)




# VALIDATIONS

# validate registration 
def validate_registration(post_data):

  errors = {}

  if len(post_data['first_name']) < 1 or post_data['first_name'] == '':
    errors['first_name'] = "First Name must contain 2 letters or more" 

  if profanity.contains_profanity(post_data['first_name']) == True:
    errors['bad_first_name'] = "Please Enter an appropriate First Name"

  if len(post_data['last_name']) < 1 or post_data['last_name'] == '':
    errors['last_name'] = "Last Name must contain 2 letters or more"

  if profanity.contains_profanity(post_data['last_name']) == True:
    errors['last_name'] = "Please Enter an appropriate Last Name"

  if len(post_data['username']) < 4 or post_data['username'] == '':
    errors['username'] = "Username must contain 5 letters or more"

  if profanity.contains_profanity(post_data['username']) == True:
    errors['bad_username'] = "Please Enter an appropriate username"

  if len(post_data['password']) < 7 or post_data['password'] == '':
    errors['password'] = "Password must contain 8 characters or more"

  if post_data['password'] != post_data['conf_password']:
    errors['conf_password'] = "Passwords do not match"

  return errors
  
# validate login 
def validate_login(post_data):
  
  errors = {}

  if len(post_data['username']) < 4 or post_data['username'] == '':
    errors['username'] = "Please Enter valid username"

  if len(post_data['password']) < 7 or post_data['password'] == '':
    errors['password'] = "Please Enter valid password"

  return errors

