import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = PostgresqlDatabase('dermatic', user='tiffanyteaze', password='secret', host='127.0.0.1', port=5432)
class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()
    skin_type = CharField()
    avatar = CharField()
    image_url = CharField()
    age = IntegerField()
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)  

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        only_save_dirty = True

    def get_reviews(self):
        return Review.select().where(Review.user == self)

    def get_list(self):
        return List.select().where(List.user_id == self)

    @classmethod
    def create_user(cls, username, email, password, image_url="", first_name="", last_name="", skin_type="", age=18, avatar="../static/images/mask.png", admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                skin_type=skin_type,
                age=age,
                avatar=avatar,
                image_url=image_url,
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    @classmethod
    def edit_user(cls, username, email, password, first_name, avatar="../static/images/brock.png", admin=False):
        try:
            cls.update(
                username=username,
                email=email,
                password=generate_password_hash(password),
                first_name=first_name,
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
    buy_again = BooleanField(default=False)
    helpful_votes = IntegerField()
    not_helpful_votes = IntegerField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)  
        indexes = ((("user_id", "product_id"), True),)

class Vote(Model):
    user = ForeignKeyField(
        model=User,
        backref='votes'
    )
    review = ForeignKeyField(
        model=Review,
        backref='votes'
    )
    helpful = BooleanField()

    class Meta:
        database = DATABASE
        indexes = ((("user_id", "review_id"), True),)

class List(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        model=User,
        backref='list'
    )
    product_id = IntegerField()
    
    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)  
        indexes = ((("user_id", "product_id"), True),)

    @classmethod
    def create_list_item(cls, user_id, productid):
        try:
            cls.create(
                user=user_id,
                product_id=productid
            )
        except IntegrityError:
            return success
            
def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Review, Vote, List], safe=True)
    DATABASE.close()