# flask-restful-pymongo
RESTful API with flask-restful and PyMongo

The project was created as part of a Coding Challenge Assigment.
For this, the RSS feed from Stackoverflow Jobs is pulled (search filter: 'matlab' https://stackoverflow.com/jobs?q=matlab) and saved in PyMongo with the help of flask/flask-restful.

steps:
1) creating small RESTful http service (flaskful.py) <br />
1.1) creating database management system (PyMongo) <br />
1.2) storing data objects according to JSON Resume data model https://jsonresume.org/ (fill_json_resume() & PullJobs.post()) <br />
1.3) listing of previously stored jobs data objects (ShowJobs.get()) <br />
2) Stackoverflow's Jobs API (flaskful.py) <br />
2.1) fetching RSS feed from Stackoverflow (pull_rss()) <br />
2.2) transforming data model for storage (get_essentials_from_feed()) <br />
3.) do it autonomous (tryful.py)


HowToUse:
- installing requirements:
  > pip install -r req.txt
- starting mongo/flask (make sure your mongod.exe is running):
  > python flaskful.py
- pulling rss into db (here its executed with a certain filter matlab):
  > python tryful.py pull_jobs
- display saved jobs in db:
  > python tryful.py show_jobs
- showing amount of entries in db:
  > python tryful.py home
- loop the fetch function, to keep db updated (in 15 sec interval):
  > python tryful.py loop
