from elixir import *

metadata.bind = 'mysql://root:cs145@localhost/cs145'
metadata.bind.echo = True


class Tweet(Entity):
    # Relationships
    user = ManyToOne('User')
    hashtags = ManyToMany('Hashtags')

    # Fields
    tweet = Field(UnicodeText)
    tweetid = Field(Integer)
    time = Field(Integer)

class Hashtags(Entity):
    # Relationships
    tweets = ManyToMany('Tweet')

    # Fields
    hashtagid = Field(Integer)
    tag = Field(UnicodeText)

class User(Entity):
    # Relationships
    tweets = OneToMany('Tweet')

    # Fields
    userid = Field(Integer)
    username = Field(UnicodeText)


