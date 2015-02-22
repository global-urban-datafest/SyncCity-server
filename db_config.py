location = 'raspi'

if location == 'bluemix':
    DB_HOST = '198.11.234.66:3307'
    DB_NAME = 'd0ea748e53f2d4f8382beb4016a952f1a'
    DB_USER = 'ucYK0kila3Bi7'
    DB_PASSWD = 'ploJlABfENzAI'
elif location == 'raspi':
    DB_HOST = '147.83.178.154:3306'
    DB_NAME = 'SyncCity'
    DB_USER = 'root'
    DB_PASSWD = 'toor'

# import db_config
# import torndb
# db = torndb.Connection(db_config.DB_HOST, db_config.DB_NAME, db_config.DB_USER, db_config.DB_PASSWD)
