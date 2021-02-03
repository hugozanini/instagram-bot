# Instagram Bot

Selenium-based bot to scrape data from Instagram posts.

### Getting started


Clone the repository and download [Selenium ChromeDriver](https://chromedriver.chromium.org/downloads) (WebDriver for Chrome) .

Create a new virtualenv

> On linux terminal:

    virtualenv -p python3 venv

Activate the environment:

    source venv/bin/activate

Install the requirements:

    pip install -r requirements.txt


Start the scrapper filling the following parameters:

 - **login (-l)**  : Your instagram login password (-p): Your instagram
  - **password search (-s)**: The hashtag you want to search number of
  - **scrolls (-s)**: Number of times you want to scroll the instagram search
  - **page  output (-o)**: Filename do save the output


Example:

    python instabot.py -l exampleuser -p mypassword -c chromedriver_linux64/chromedriver -s braziliansoccer -n 2 -o braziliansoccer.csv

The application is going to open a webpage and start to scrap the data. First, the login and the search will be done, after that, the bot will scroll the screen *n times* to save the posts links and then access one by one to get the data.

![Object detection demo](./git_media/kangaroo-demo.gif)
<br>

When finished, the application is going to save a .csv file containing the following data for each post:

- **date**: Post date
- **type**: Type of the post (image or video)
- **user**: User post
- **subtitles**: Post subtitles
- **image_description**: Image description autogenerated by instagram
- **likes**: Number of likes (for images)
- **views**: Number of views (for videos)
- **rank**: Post ranking (defined by instagram)
- **link**: Post link
