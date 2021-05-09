from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from bson import ObjectId
import feedparser
import json


FLASK_APP = Flask(__name__)
FLASK_APP.config["MONGO_URI"] = "mongodb://localhost:27017/stackoverflow_jobs"
REST_API = Api(FLASK_APP)
MONGO = PyMongo(FLASK_APP)


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        '''bson/ObjectID converter, preventing TypeError'''

        if isinstance(o, ObjectId):

            return str(o)

        return json.JSONEncoder.default(self, o)


class Home(Resource):

    def get(self):
        '''REST GET, here: will display amount of existing entries in DB'''

        jobs = MONGO.db.jobs
        job_collection = jobs.find()

        return {'Current existising entries in DB': job_collection.count()}, 201


class PullJobs(Resource):

    def post(self):
        '''REST POST, here: fetching RSS from stackoverflow and storing into db'''

        jobs = MONGO.db.jobs
        feed = pull_rss()  # getting rss feed
        essentials = get_essentials_from_feed(feed)  # cleaning feed data

        for essence in essentials:
            if not is_in_jobs(essence):
                json_resume_job = fill_json_resume(essence)  # create json
                new_insert_id = jobs.insert(json_resume_job)  # store into db
            else:
                print('Entry already exists in DB! LabelID: ', essence[0])

        return {}, 201


class ShowJobs(Resource):

    def get(self):
        '''REST GET, here: showing all existing entries in DB'''

        jobs = MONGO.db.jobs
        res = []

        for ele in jobs.find():
            res.append(JSONEncoder().encode(ele))

        return {'all_jobs': res}, 201


# Home.get() function called by 'http://127.0.0.1:5000/'
REST_API.add_resource(Home, '/')

# PullJobs.post() function called by 'http://127.0.0.1:5000/pull_jobs'
REST_API.add_resource(PullJobs, '/pull_jobs')

# ShowJobs.get() function called by 'http://127.0.0.1:5000/show_jobs'
REST_API.add_resource(ShowJobs, '/show_jobs')


def pull_rss():
    '''feedparser for fetching rss feed from stackoverflow, filter = matlab'''

    rss_url = 'https://stackoverflow.com/jobs/feed?q=matlab'
    parsed_feed = feedparser.parse(rss_url)

    return parsed_feed


def get_essentials_from_feed(feed):
    '''extract needed info, get rid of unneeded like headers, namespaces..'''

    essentials = []

    for i in range(0, len(feed['entries'])):
        essence_ele = []
        essence_ele.append(feed['entries'][i]['id'])
        essence_ele.append(feed['entries'][i]['link'])
        essence_ele.append(feed['entries'][i]['author'])

        category_tags = []

        for j in range(len(feed['entries'][i]['tags'])):
            category_tags.append(feed['entries'][i]['tags'][j]['term'])

        essence_ele.append(category_tags)
        essence_ele.append(feed['entries'][i]['title'])
        essence_ele.append(feed['entries'][i]['summary'])
        essence_ele.append(feed['entries'][i]['published'])
        essence_ele.append(feed['entries'][i]['updated'])
        essence_ele.append(feed['entries'][i]['location'])

        essentials.append(essence_ele)

    return essentials


def is_in_jobs(keys):
    '''checking if DB already contains a certain entry in collection/jobs'''

    jobs_collection = MONGO.db.jobs
    db_entries = jobs_collection.find()

    for entry in db_entries:
        if (
            entry['basics']['label']==keys[0] and
            entry['work'][0]['startDate']==keys[6] and
            entry['work'][0]['endDate']==keys[7]
        ):

            return True

    return False


def fill_json_resume(keys):
    '''create json resume data model and store essential feed info into it'''

    feed_id = keys[0]
    feed_link = keys[1]
    feed_author = keys[2]
    feed_category = ', '.join(keys[3])
    feed_titel = keys[4]
    # feed_description = clear_tags(keys[5])
    feed_description = keys[5]
    feed_published = keys[6]
    feed_updated = keys[7]
    feed_location = keys[8]
	
    # data model according to jsonresume.org/schema/
    json_resume_schema = {

        "basics": {
            "name": "default",
            "label": feed_id,
            "picture": "default",
            "email": "default",
            "phone": "default",
            "website": "default",
            "summary": "default",
            "location": {
                "address": "default",
                "postalCode": "default",
                "city": feed_location,
                "countryCode": 'default',
                "region": "default"
            },
            "profiles": [{
                "network": "default",
                "username": "default",
                "url": "default"
            }]
        },
        "work": [{
            "company": feed_author,
            "position": feed_titel,
            "website": feed_link,
            "startDate": feed_published,
            "endDate": feed_updated,
            "summary": feed_description,
            "highlights": [
                feed_category
            ]
        }],
        "volunteer": [{
            "organization": "default",
            "position": "default",
            "website": "default",
            "startDate": "default",
            "endDate": "default",
            "summary": "default",
            "highlights": [
                "default"
            ]
        }],
        "education": [{
            "institution": "default",
            "area": "default",
            "studyType": "default",
            "startDate": "default",
            "endDate": "default",
            "gpa": "default",
            "courses": [
                "default"
            ]
        }],
        "awards": [{
            "title": "default",
            "date": "default",
            "awarder": "default",
            "summary": "default"
        }],
        "publications": [{
            "name": "default",
            "publisher": "default",
            "releaseDate": "default",
            "website": "default",
            "summary": "default"
        }],
        "skills": [{
            "name": "default",
            "level": "default",
            "keywords": [
                "default",
                "default",
                "default"
            ]
        }],
        "languages": [{
            "language": "default",
            "fluency": "default"
        }],
        "interests": [{
            "name": "default",
            "keywords": [
                "default",
                "default"
            ]
        }],
        "references": [{
            "name": "default",
            "reference": "default"
        }]

    }

    return json_resume_schema


def clear_tags(html_based_text):
    '''removing html tags from feed description'''

    html_tags = [
                '<li>', '</li>',
                '<br>', '</br>', '<br />',
                '<ul>', '</ul>',
                '<p>', '</p>',
                '</strong>', '<strong>',
                '<sup>', '</sup>'
                ]

    for tag in html_tags:
        html_based_text = html_based_text.replace(tag, '')

    return html_based_text


if __name__ == '__main__':
    FLASK_APP.run(debug=True)
