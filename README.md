Code Forgery SyncCity server
================================================================================

Backend implementation of SyncCity Smart Tourism contest entry for smartcities
hackaton.


run locally
--------------------------------------------------------------------------------

- [install flask](http://flask.pocoo.org/docs/0.10/installation/)
- run `python hello.py`
- visit web site:

API:

```
GET /api_user/route?username=john&date=YYYY-mm-dd&time={all_day, morning, afternoon}&city=Barcelona
GET /api_admin/smart_data
PUT /api_admin/smart_data?source={real, fake_rainy, fake_sunny}
GET /api_admin/verbose
PUT /api_admin/verbose?val={true, false}
```



run on bluemix
--------------------------------------------------------------------------------

- copy the file `manifest-sample.yml` to `manifest.yml`
- edit the `manifest.yml` file and edit the `hostname` property to make it unique
- run `cf push`
- visit web site



buildpacks you might want to use
--------------------------------------------------------------------------------

The `manifest.yml` file used for running on bluemix has a buildpack hard-coded
in it.  You may want to try another, but of course *your mileage may vary*.

- https://github.com/heroku/heroku-buildpack-python.git
- https://github.com/joshuamckenty/heroku-buildpack-python.git
- https://github.com/ephoning/heroku-buildpack-python.git
