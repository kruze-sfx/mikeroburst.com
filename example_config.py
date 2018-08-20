import os

# The path to the python interpreter that passenger should use
interp = os.path.join(os.environ['HOME'], 'venv', 'bin', 'python')

# This is the path containing the photos and directories served by the app
photos_root = os.path.join(os.environ['HOME'], 'mikeroburst.com', 'pics', 'albums')  # noqa

# Mysql database host
db_host = 'mysql.mikeroburst.com'

# Mysql database user name
db_user = 'readonly_user'

# Mysql database password
db_password = 'my_password'

# Mysql database name
db_name = 'mikeroburst_photos'
