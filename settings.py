# Flask settings
FLASK_SERVER_NAME = 'localhost:8888'
FLASK_DEBUG = True  # Do not use debug mode in production
UPLOAD_FOLDER = './Resources/static/resources'

# SQLAlchemy settings
# SQLALCHEMY_DATABASE_URI = 'postgresql://wivufjnadozxda:c7c7d694ad13995f27ebb739e8aa6219de15f7186a1291d4d007f478c18c7490@ec2-34-233-0-64.compute-1.amazonaws.com:5432/d9un3hae4g8ht2'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/virtualclassdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
