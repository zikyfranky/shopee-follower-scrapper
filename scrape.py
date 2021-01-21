from bs4 import BeautifulSoup as BS
import requests
import json


class Shopee():

    """
    The base class with neccessary methods to scrape shopee followers list

    Properties:

    end (bool): Bool that determines if the crawler has reached the end of the followers list

    offset (int): An integer that determines the value the offset adds by

    current (int): An integer that determines the current offset to fetch

    base_url_for_follower_page (str): A link to the base url of a shopee user ie "https://shopee.com.my"

    usernames (array of str): An array that holds the fetched usernames

    filename (str): Name of file to save the fetched users

    Returns:

    class_obj: Returns an obj of this class
    """

    def __init__(self):
        self.end = False
        self.offset = 20
        self.current = 0
        self.base_url_for_follower_page = "https://shopee.com.my"
        self.usernames = []
        self.filename = "./followers.txt"

    def get_html(self):
        """
        The method to get the webpage HTML as string

        Returns:

        str: the webpage html as a string
        """
        print(f"Fetching {self.current} Request")
        return requests.get(
            f'https://shopee.com.my/shop/145423/followers?offset={self.current}&__classic__=1').text

    def get_followers(self, html):
        """
        An internal method to get list of followers

        Returns:

        array of HTMLElement: Array of List Items of the followers
        """
        soup = BS(html, "html.parser")
        if len(soup.find_all('ul')) <= 0:
            return soup.find_all('li')
        else:
            return soup.select('ul.follower-list')[0].find_all('li')

    def get_username_and_links(self, followers):
        """
        An internal method to get username and link as str

        Returns:

        An array(batch) of users link

        """

        print("Compiling Batch of Users\n")
        batch = []
        for follower in followers:
            anchor_tag = follower.find('a')
            try:
                username = anchor_tag.get("href")[1:]
            except TypeError as error:
                continue
            link_to_username = f'{self.base_url_for_follower_page}/{username}'
            batch.append(link_to_username)
        print("Returning Batch of Users\n")
        return batch

    def write_usernames_to_file(self, username_batch):
        """
        An internal method to write usernames and links to file

        """

        print("Writing Links to file :)")

        for i in username_batch:
            if i not in self.usernames:
                with open(self.filename, 'a+') as file:
                    file.write(i+'\n')
            else:
                continue

    def delete_duplicates(self):
        """
        An internal method to delete duplicates from the file

        """
        with open(self.filename, 'r') as file:
            links = list(set(file.readlines()))
            with open(self.filename, 'w+') as file:
                for i in links:
                    file.write(i+'\n')

    def run(self):
        """
        The main method to run the crawler

        Returns:

        bool: True if successfull, False if it isn't
        """
        while self.end == False:
            html_doc = self.get_html()
            try:
                data = json.loads(html_doc)
                if data["no_more"]:
                    print("We've reached the very end, Ending Script right now!")
                    self.end = True
            except json.decoder.JSONDecodeError as error:
                followers = self.get_followers(html_doc)
                usernames_batch = self.get_username_and_links(followers)
                # After fetching batch of users, write it to file
                self.write_usernames_to_file(usernames_batch)

            # Update the current offsets
            self.current += self.offset

        self.delete_duplicates()
