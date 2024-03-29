## File and Folder Organization
The code behind this app is organized like a standard Flask app.  The `migrations` folder contains code to upgrade the database scheme as the need arose (ie. adding additional fields) and is entirely autogenerated.  The `app` folder contains the meat of the app.  

* The static folder contains the static assets for the site such client side libraries like jquery and bootstrap along with a few jquery plugins and some small bits of custom javascript (`script.js`) and css (`style.css`).  

* The template folder contains the html templates that take some varibles and generat the html.  These are organized into folders that roughly correspond to the url for the page the template is responsible for. 

* The blueprints folder contains the logic required to make the site run. Each blueprint is responsible for a different logical portion of the site.  It should be pretty easy to identify which blueprint does what based solely on the blueprint's name.  

* `__init__.py` contains the logic to load all the blueprints and initialize the webserver.  

* `helpers.py` contains functions that can be used with in the html templates.  These lessen the amount of html that needs to be manually written and ensures a consistant style.  

* `models.py` contains the database entity definitions and relationships.  Additionally some functions are attached to these models for common functions you'd perform on them (such as `calculateTotal()` on the `Booking` model).

* `logic.py` contains business logic that has no corresponding database model.  This contains classes like `tenativeBooking` which is built during the booking process and is converted to a `Booking` model in the database when finalized.  

* `validation.py` contains logic to make it easy to validate form fields and return the page to the user upon validation errors.  Views that take form input get tagged with `@validate()` decorator and passes in a list of inputs and the expected datatypes.  Each datatype corresponds to a function in `validation.py` that ensures a value's accuracy.  

* `config.py` contains some configuration varibles such as the database server to use.

* Other files not mentioned are of little importance and only imporant for development and not used by the app in production.  

### General Notes
* This app uses the POST/Redirect/GET methodology to ensure there are no duplicate form submissions. because of this only GETs return HTML while all POSTS return redirects.  

* This app uses pylint and pep8 to adhere to traditional python coding standards.  Some varitions on these standards are used, such as allowing camelCase and a line length of 120 characters (vs 80).  `.pylintrc` contains a list of these changes.  

* This app uses Git for source control.  You can find the latest version in the online repository located at [http://git.jdp.tech/trcx/CDCC](http://git.jdp.tech/trcx/CDCC).

* Most functions and files contain doc strings to describe their purpose and role in the application as a whole.  While there are comments there are only a few opting to use the doc string for documentation purposes instead. 