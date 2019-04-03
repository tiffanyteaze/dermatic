import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('dermatic.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_reviews(self):
        return Review.select().where(Review.user == self)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    @classmethod
    def edit_user(cls, username, email, password, avatar="../static/images/brock.png", admin=False):
        try:
            cls.update(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin,
                avatar=avatar
            )
        except IntegrityError:
            raise ValueError("User already exists")

class Review(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        model=User,
        backref='reviews'
    )
    content = TextField()
    product_id = IntegerField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)  
        indexes = ((("user_id", "product_id"), True),)
            
def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Review], safe=True)
    DATABASE.close()