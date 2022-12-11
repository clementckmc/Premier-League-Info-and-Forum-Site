## Premier League Info and Forum Site
### Capstone - CS50’s Web Programming with Python and JavaScript

### Overview

--------

This is a web application project built with Django on the back-end and Javascript on the front-end, as the final project for Harvard CS50’s Web Programming with Python and JavaScript course.

It is a simple website that presents Premier League data and information by retreiving data from [football-API](https://www.football-data.org/), including information for each Premier League team, fixtures and table of the current Premier League season.
It also includes a discussion forum for each Premier League team.

### Distinctiveness and Complexity

--------

This web application utilizes Django framework on the back-end with 3 models (User, Thread and Reply).
The Django framework(Python) also performs functions like retreiving data from API, handling HTTP requests, rendering pages and making queries on data.
Javascript on the front-end is also utilized to perform fetch calls and implement different event listeners, with HTML, CSS and Bootstrap also applied extensively to build the user interface of the web application.

The web application is sufficiently distinct and complex from the other projects in this course as it makes API calls from an outside source which is relatively complex. 
While other projects in the course use Javascript to handle API responses, this web application uses Python to handle the API data.
Apart from that, models in Django framework is applied in a more complex way as it includes models like SlugField and adding properties and functions for Thread and Reply models.


### Files

--------

`./football/`
- `admin.py`: Registering models into the django administration
- `urls.py`: Contains a list of url patterns
- `models.py`: Contains all models of the web application
- `views.py`: Contains functions to generate web templates (and retrieve APIs)

`./football/templates/football`
- `layout.html`: Layout template of the website
- `index.html`: Home page of the website
- `register.html`: User registration
- `login.html`: Login page
- `teamInfo.html`: Basic information of each Premier Club
- `fixtures.html`: Premier League fixtures of the current season
- `table.html`: Premier League table of the current season
- `forum.html`: Listing all team forums and general discussion forum
- `teamForum.html`: Forum for each team, listing all threads under that particular forum
- `thread.html`: Listing replies of a particular thread, also allow users to add new replies and upvote/downvote each post
- `newPost.html`: Allow users to create new thread

`./football/static/football`
- `script.js`: All javascript codes are stored here, providing features including:
    - asynchronously updating upvote and downvote for threads/replies
    - disabling upvote/downvote buttons once the user has voted
    - the cite button of forum
    - assigning class to buttons of sidebar to change the background color
- `styles.css`: Contains all styling of the website


### Usage

--------

Install the required packages and start the server.

```sh
pip install -r requirements.txt
python manage.py runserver
```

Then Navigate to http://127.0.0.1:8000/ in your browser.

A token is needed to retrieve data from [football-API](https://www.football-data.org/).
