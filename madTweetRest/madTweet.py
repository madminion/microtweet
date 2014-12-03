#! /usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'madminion'

import json
from pymongo import MongoClient

client = MongoClient()
from operator import itemgetter
from flask import Flask, request, make_response

app = Flask(__name__)

# The mongo db is madTweet
db = client.madTweet


# mongo collection for users
userCollection = db.user


# mongo collection for tweets
tweetCollection = db.tweet


# TEST CONNECTION
@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


# # GET METHODS

# GET /:handle/tweets # :handle tweets
@app.route('/madTweet/<handle>/tweets/', methods=['GET'])
def mongo_get_tweets_from_user(handle):
    tweets = []
    for tweet in tweetCollection.find({'handle': handle}):
        tweet['_id'] = str(tweet['_id'])
        tweets.append(tweet)
    return get_response(tweets, 200)


# GET /:handle/followers # :handle followers
@app.route('/madTweet/<handle>/followers/', methods=['GET'])
def mongo_get_followers_from_user(handle):
    followers = []
    user = find_user(handle)
    for follower in user['followers']:
        follower = remove_follow_attributes(find_user(follower['handle']))
        followers.append(follower)
    return get_response(followers, 200)


# GET /:handle/followings # :handle followings
@app.route('/madTweet/<handle>/followings/', methods=['GET'])
def mongo_get_followings_from_user(handle):
    followings = []
    user = find_user(handle)
    for following in user['followings']:
        following = remove_follow_attributes(find_user(following['handle']))
        followings.append(following)
    return get_response(followings, 200)


# GET /:handle/reading_list # local followings tweets sorted by creation date**
@app.route('/madTweet/<handle>/reading_list/', methods=['GET'])
def mongo_get_reading_list(handle):
    user = find_user(handle)
    tweets = []
    for follower in user['followers']:
        for tweet in tweetCollection.find({'handle': follower['handle']}):
            tweet['_id'] = str(tweet['_id'])
            tweets.append(tweet)
    tweets = sorted(tweets, key=itemgetter('date'), reverse=True)
    return get_response(tweets, 200)


# # Nice to have:

# GET /users # list users
@app.route('/madTweet/users/', methods=['GET'])
def mongo_get_users():
    users = []
    for user in userCollection.find():
        remove_follow_attributes(user)
        user['_id'] = str(user['_id'])
        users.append(user)
    return get_response(users, 200)


# GET /user # user information
@app.route('/madTweet/<handle>/', methods=['GET'])
def mongo_get_user(handle):
    return get_response(find_user(handle), 200)


# GET /tweets # list tweets
@app.route('/madTweet/tweets/', methods=['GET'])
def mongo_get_tweets():
    tweets = []
    for tweet in tweetCollection.find():
        tweet['_id'] = str(tweet['_id'])
        tweets.append(tweet)
    return get_response(tweets, 200)


# OPTIONS /.* # CORS handling

# DELETE METHODS

# DELETE /:handle/followers # Remove follower (inter SRV)
@app.route('/madTweet/<handle>/follower/<follower>/', methods=['DELETE'])
def mongo_delete_follower_from_user(handle, follower):
    ref = {'handle': handle}
    users = []
    for user in userCollection.find({'handle': handle}):
        users.append(user)
    user = users[0]
    status = {}
    user['followers'].remove({'handle': follower})

    userCollection.update(ref, user)
    status['result'] = True
    return get_response(status, 201)


# DELETE /:handle/followings # Stop following someone **
@app.route('/madTweet/<handle>/following/<following>/', methods=['DELETE'])
def mongo_get_stop_following(handle, following):
    ref = {'handle': handle}
    users = []
    for user in userCollection.find({'handle': handle}):
        users.append(user)
    user = users[0]
    status = {}
    user['followings'].remove({'handle': following})
    userCollection.update(ref, user)
    status['result'] = True
    return get_response(status, 201)


# # POST METHODS

# POST /:handle/tweets # Add tweet **
@app.route('/madTweet/<handle>/tweet/', methods=['POST'])
def mongo_add_tweet_from_user(handle):
    status = {}
    tweet = {'handle': handle}
    for key in request.args:
        tweet[key] = request.args[key]
#   TEST PURPOSE return get_response(request.args, 201)
    tweetCollection.insert(tweet)
    status['result'] = True
    return get_response(status, 201)


# POST /users # Create user
@app.route('/madTweet/', methods=['POST'])
def mongo_create_user():
    user = {}
    status = {}
    for key in request.args:
        user[key] = request.args[key]
    userCollection.insert(user)
    status['result'] = True
    return get_response(status, 201)


# POST /:handle/followings # Follow someone **
@app.route('/madTweet/<handle>/follower/<following>', methods=['POST'])
def mongo_follow(handle, following):
    ref = {'handle': handle}
    users = []
    for user in userCollection.find({'handle': handle}):
        users.append(user)
    user = users[0]
    status = {}
    user['followings'].append({'handle': following})
    userCollection.update(ref, user)
    status['result'] = True
    return get_response(status, 201)


# POST /:handle/followers # Add follower (inter SRV)
@app.route('/madTweet/<handle>/follower/<follower>', methods=['POST'])
def add_follower(handle, follower):
    ref = {'handle': handle}
    users = []
    for user in userCollection.find({'handle': handle}):
        users.append(user)
    user = users[0]
    status = {}
    user['followers'].append({'handle': follower})
    userCollection.update(ref, user)
    status['result'] = True
    return get_response(status, 201)


# POST /sessions # Signin user **
@app.route('/madTweet/sessions/<handle>/', methods=['POST'])
def mongo_signin_session(handle):
    return True


# UTILS METHODS

# find user
def find_user(handle):
    users = []
    for user in userCollection.find({'handle': handle}):
        user['_id'] = str(user['_id'])
        users.append(user)
    return users[0]


# remove all followers and followings
def remove_follow_attributes(user):
    user.pop("followers", None)
    user.pop("followings", None)
    return user


# response as a JSON
def get_response(obj, status_code):
    response = make_response(json.dumps(obj))
    response.mimetype = "application/json"
    response.status_code = status_code
    return response

# MAIN
if __name__ == '__main__':
    app.run(debug=True)

