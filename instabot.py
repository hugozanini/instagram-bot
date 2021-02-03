from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup
import time
import logging
from tqdm import tqdm
import pandas as pd
import argparse


logger = logging.getLogger('InstaBOT')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = \
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class InstaBot():
    def __init__(self, chromedriver_path, username, password):
        self.__driver = webdriver.Chrome(chromedriver_path)
        self.__driver.get("http://www.instagram.com")
        self.__login(username, password)

    def __login(self, username_ig, password_ig):
        #Wait until the element be clickable => load it in the webpage
        username = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "input[name='username']")))

        password = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "input[name='password']")))

        #Cleaning the fields
        username.clear()
        username.send_keys(username_ig)
        password.clear()
        password.send_keys(password_ig)

        #Login
        login_button = WebDriverWait(self.__driver, 10)\
            .until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "button[type='submit']"))).click()

        #Skipping not now
        not_now = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        not_now2 = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()

    def search(self, keyword):
        searchbox = WebDriverWait(self.__driver, 10)\
            .until(EC.element_to_be_clickable\
                ((By.XPATH, "//input[@placeholder='Search']")))
        searchbox.clear()
        searchbox.send_keys('#' + keyword)
        logger.info('Searching by ' + '#' + keyword)


        # Wait for 5 seconds
        time.sleep(5)
        searchbox.send_keys(Keys.ENTER)
        time.sleep(5)
        searchbox.send_keys(Keys.ENTER)
        time.sleep(5)

    def __lcondition(self, link):
        '''
        Selecting only image links
        '''
        return '.com/p/' in link.get_attribute('href')

    def __get_user(self):
        '''
        Getting user
        '''
        user = self.__driver.find_element_by_xpath('//*[@id="react-root"]\
          /section/main/div/div[1]/article/header/div[2]/div[1]/div[1]/span/a')
        user = user.get_attribute('href').split('/')[-2]
        return user


    def filter_links(self, links):
        '''
        Filter post links
        '''
        post_links = []
        for link in links:
            try:
                if '.com/p/' in link.get_attribute('href'):
                    post_links.append(link)
            except:
                logger.warning("A https://www.instagram.com/p/ link was not found")
                continue
        return post_links


    def __get_links(self, nscrolls, scroll_pause_time):
        '''
        Getting posts links
        '''
        saved_links = {}
        rank = 0
        # Get scroll height
        last_height = \
            self.__driver.execute_script("return document.body.scrollHeight")

        for j in tqdm(range(nscrolls)):
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            links = self.__driver.find_elements_by_tag_name('a')

            valid_links =  self.filter_links(links)

            for i in range(len(valid_links)):
                link = valid_links[i].get_attribute('href')
                if link not in saved_links.keys():
                    saved_links[link] = rank
                    rank += 1

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = \
                self.__driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # If heights are the same it will exit the function
                break
            last_height = new_height

        return saved_links

    def __get_subtitles(self,):
        '''
        Getting subtitles
        '''
        subtitles_xpath = '/html/body/div[1]/section/main/div/div[1]\
            /article/div[3]/div[1]/ul/div/li/div/div/div[2]/span'
        subtitles = self.__driver.find_element_by_xpath(subtitles_xpath)
        subtitles = subtitles.get_attribute('innerHTML')
        subtitles = BeautifulSoup(subtitles).get_text()
        return subtitles

    def __get_image_description(self) -> str:
        '''
        Getting post description
        '''
        images = self.__driver.find_elements_by_tag_name('img')
        post_infos = images[1].get_attribute('alt')

        if len(post_infos) > 0:
            post_infos = post_infos.split("Image may contain: ")
            if len(post_infos) >=2:
                #image
                return post_infos[1]
            else:
                #video
                logger.warning("Description is not available")
                return ''
        else:
            return ''

    def __get_likes(self):
        '''
        Getting likes
        '''
        likes_xpath = '//*[@id="react-root"]/section/main/div/div[1]\
            /article/div[3]/section[2]/div/div/button/span'
        likes = self.__driver.find_element_by_xpath(likes_xpath)
        likes = likes.get_attribute('innerHTML')
        return likes

    def __get_views(self):
        '''
        Getting views
        '''
        views_xpath = '/html/body/div[1]/section/main/div/div[1]\
            /article/div[3]/section[2]/div/span/span'
        views = self.__driver.find_element_by_xpath(views_xpath)
        views = views.get_attribute('innerHTML')
        return views

    def __get_date(self):
        '''
        Getting date
        '''
        date_xpath = '//*[@id="react-root"]/section/main/div/div[1]\
            /article/div[3]/div[2]/a/time'
        date = self.__driver.find_element_by_xpath(date_xpath)
        date = date.get_attribute('datetime')
        return date

    def __get_image_data(self, link, rank):
        '''
        Get image data
        '''
        infos = {}
        infos['date'] = self.__get_date()
        infos['type'] = 'image'
        if len(infos['date']) == 0:
            return None
        infos['user'] = self.__get_user()
        infos['subtitles'] = self.__get_subtitles()
        infos['image_description'] = self.__get_image_description()
        infos['likes'] = self.__get_likes()
        infos['views'] = None
        infos['rank'] = rank
        infos['link'] = link

        return infos


    def __get_video_data(self, link, rank):
        '''
        Get video data
        '''
        infos = {}
        infos['date'] = self.__get_date()
        infos['type'] = 'video'
        if len(infos['date']) == 0:
            return None
        infos['user'] = self.__get_user()
        infos['subtitles'] = self.__get_subtitles()
        infos['views'] = self.__get_views()
        infos['likes'] = None
        infos['rank'] = rank
        infos['link'] = link

        return infos



    def get_data(self, nscrolls, scroll_pause_time) -> dict:
        '''
        Get all hashtag data
        '''
        links = self.__get_links(nscrolls, scroll_pause_time)
        logger.info(str(len(links)) + " links were found.")

        processed_data = []
        for link, rank in tqdm(links.items()):
            infos = {}

            #Accessing the post
            self.__driver.get(link)
            time.sleep(1)
            post_details = \
                    self.__driver.find_element_by_xpath('/html/body/script[1]')
            post_details = post_details.get_attribute('innerHTML')

            try:
                if post_details.split('is_video":')[1][:1] == 't':
                    infos = self.__get_video_data(link, rank)
                elif post_details.split('is_video":')[1][:1] == 'f':
                    infos = self.__get_image_data(link, rank)

            except:
                logger.warning("Failed to retrieve " + link + ' data. Skipping.')
                time.sleep(3)
                continue

            if infos not in processed_data and infos is not None:
                processed_data.append(infos)
            time.sleep(1)

        return processed_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', required=True,
                                    help="Instagram login")

    parser.add_argument('-p', '--password', required=True,
                                    help="Instagram password")

    parser.add_argument('-c', '--chromedriver', required=True,
                                    help="Chromedriver path")

    parser.add_argument('-s', '--search', default='test', required=True,
                                    help="Hashtag to be searched")

    parser.add_argument('-n', '--n_scrolls', default=100, required=True,
                                    help="Number of scrolls")

    parser.add_argument('-o', '--output', default='test.csv', required=True,
                                    help="Output filename")

    args = parser.parse_args()


    my_bot = InstaBot(chromedriver_path = args.chromedriver,
                 username = args.login,
                 password = args.password)
    my_bot.search(args.search)
    data = my_bot.get_data(nscrolls = int(args.n_scrolls),
                                    scroll_pause_time = 5)

    logger.info(str(len(data)) + " links were found.")

    df = pd.DataFrame(data)
    df.to_csv(args.output, index = False)
    logger.info("Results saved at " + args.output)


if __name__ == "__main__":
    main()
