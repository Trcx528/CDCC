## CD&CC ##

This project is for the UWM SOIS 350 Senior Capstone course in which we design a scheduling system for fictious 'City Dome And Convention Center.' The requirements state that in addition to managing room scheduleing and preventing double bookings we allow allow rooms to be combined, storage of contact information and grouping of contacts into organization and track caterering requirements per event.  There are some reports which would be used by marketing for figureout how to target new customers as well as providing discount to repeat customers.  

This site is built entirely using flask 0.12 (python) for the backend, with peewee as the ORM for database interaction.  Peewee supports numerous database providers so any databases peewee supports should work although the app has only been tested with mysql.    The front end is built using bootstrap, jquery, and a few additional libraries, with some javascript to tie everything together.   Flask debug toolbar is included for easy profiling making it easy to sniff out performance issues before they become problems.  

### Features ###
* Simple administration of rooms, contacts, organizations, caterering vendors, and caterering food options
* Automatic suggestion of room combinations (up to 3 rooms) for large events

#### Getting Started ####

```shell
git clone http://git.jdp.tech/Trcx/CDCC.git
cd CDCC
vi config.py
# (Optional) setup virtalenv to keep the host system clean
virtualenv env
env/bin/activate
# install the dependencies
pip install flask-pw flask-debugtoolbar pymysqldb
# Create the database by running the migrations
python run.py db migrate
# start the app without debugging
python run.py runserver
# start the app with debugging, automatic reloads and multithreading
python run.py runserver -d -r --threaded
```

### Screen Shots ###
![Login Screnshot](https://git.jdp.tech/Trcx/CDCC/raw/master/screenshots/login.png "Login required to view anything")
![Form Validation Screenshot](https://git.jdp.tech/Trcx/CDCC/raw/master/screenshots/validation.png "Forms are validated and provide per input feedback")
![Homepage Screenshot](https://git.jdp.tech/Trcx/CDCC/raw/master/screenshots/home.png "Simple homepage once logged in")
![Booking Confirmation Screenshot](https://git.jdp.tech/Trcx/CDCC/raw/master/screenshots/confirmation.png "Final confirmation step in the booking process")
