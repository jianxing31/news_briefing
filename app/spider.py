#!/usr/bin/env python
import os
import sys

path = os.path.join(os.path.dirname(__file__), "../utils")
sys.path.insert(0, path)

import traceback
import time
import random
import re

import pandas as pd
from datetime import datetime
from base import Base
from summarize import summarize
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from util import dir_path_check, load_json_file, remove_space, save_json_file
from readability import Document
from dateutil.parser import parse


class Spider(Base):
    def __init__(self, path_task):
        super().__init__()
        self.path_task = path_task
        self.Sumapp = summarize()

        args = Options()
        args.add_argument("--no-sandbox")
        args.add_argument("--headless")
        args.add_argument("--disable-dev-shm-usage")
        self.Driver = webdriver.Chrome(
            executable_path="/usr/bin/chromedriver", options=args
        )
        self.Driver.set_page_load_timeout(60)
        self.Driver.implicitly_wait(10)

    def workflow(self, overide=False, skip=0):
        self.logger.info("\n  task starts")
        self.load_task()
        self.load_db()
        self.create_db_table(table_name=self.task_name, overide=overide)

        self.start_task(skip=skip)

        self.save_excel(self.Excel_list, self.FilenaAll, columns=self.Db_column)
        self.conn.commit()

        save_json_file(self.Crawl_history_path, self.Crawl_history)

        self.close()

    def load_task(self, test=False):

        conf_task = load_json_file(self.path_task)
        self.task_name = conf_task["Task_name"]

        self.Start_link = conf_task["Start_link"]
        self.Website_regex = conf_task["Reg_definition"]
        self.Crawl_history = conf_task["Crawl_history"]
        self.Website_regex = os.path.join(os.path.dirname(__file__), self.Website_regex)
        self.Website_regex = load_json_file(self.Website_regex)
        self.Crawl_history_path = os.path.join(
            os.path.dirname(__file__), self.Crawl_history
        )
        self.Crawl_history = load_json_file(self.Crawl_history_path)
        if "start_id" in self.Crawl_history:
            self.Current_id = self.Crawl_history["start_id"]
        else:
            self.Current_id = self.Crawl_history["start_id"] = 0
        self.Excel_save_dir = os.path.join(self.save_dir, self.task_name)

    def start_task(self, skip=0):

        base_links = self.Start_link[skip:]
        ng_links = []
        filename = "D" + datetime.now().strftime("%y%m%d")
        self.FilenaAll = os.path.join(self.Excel_save_dir, filename + ".xlsx")
        self.Excel_list = []
        self.c.execute(f"SELECT * from {self.task_name}")
        for link in base_links:
            self.logger.info(f"\n start working on site: {link}")
            next_links = []
            domain = link
            dir_path_check(self.Excel_save_dir)
            if domain in self.Crawl_history:
                domain_modified_time = self.Crawl_history[domain]
                self.Stop_url = (
                    list(domain_modified_time)[-1] if domain_modified_time else None
                )
            else:
                domain_modified_time = {}
                self.Stop_url = None
                self.logger.info(f"\n the following url is not crawled before: {link}")
            for link_info in self.Website_regex[domain]:
                link = link_info["Links"][0]
                if len(link_info["Links"]) != 1:
                    next_links += self.Website_regex[domain][0]["Links"][1:]

                link_extract_res = link_info["Link_extract_re"]
                next_page_res = link_info["Next_page_re"]
                crawl_content_res_ = link_info["Content_extract_re"]

                i = 0
                while True:
                    i += 1
                    try:
                        html, link = self.get_html_source(link)
                        ng_links.append(link)
                        extr_url_headlines, next_page_links = self.parse_html(
                            link,
                            html,
                            download_res=link_extract_res,
                            next_res=next_page_res,
                        )

                        if not self.is_overlap(
                            extr_url_headlines, domain_modified_time
                        ):
                            for url_ in next_page_links:
                                if url_ not in ng_links:
                                    next_links.append(url_)
                                    ng_links.append(url_)
                        self.logger.info(
                            f"\n  {len(extr_url_headlines)} articles found from {link}"
                        )

                        link_headline_contents = self.get_web_contents(
                            extr_url_headlines, domain_modified_time
                        )
                        if link_headline_contents:
                            self.process_content(
                                link_headline_contents, domain_modified_time
                            )
                        if next_links and extr_url_headlines and i <= 3:
                            link = next_links.pop(0)
                            self.logger.info(f"\n going to next link: {link}")
                        else:
                            break
                    except Exception as e:
                        self.logger.info(
                            f"\n  An Error showed up when deal with link: {link} \n Error Message: {str(e)}"
                        )
                        self.logger.info("".join(traceback.format_tb(e.__traceback__)))
                        break
            self.Crawl_history[domain] = domain_modified_time

    def parse_html(self, link, html, download_res=[], next_res=[]):
        # parse html page
        extr_url_headlines = []
        target_next_link = []
        extr_url_headlines = self.get_target_url(html, link, download_res)
        print("Url got: ", len(extr_url_headlines))
        for next_re in next_res:
            if "update_page" in next_re:
                path = next_re["path"]
                extr_url_headlines += self.driver_update_link(link, path, download_res)
            else:
                # to be updated
                pass

        print("Url got: ", len(extr_url_headlines))
        return extr_url_headlines[:2], target_next_link[:2]

    def driver_update_link(self, link, path, download_res):
        # update website to get more information
        self.Driver.get(link)
        texts = []
        target_file_urls = []
        try:
            self.Driver.find_element("xpath", path).click()
            time.sleep(random.uniform(6, 9))
            html = self.Driver.page_source
            target_file_urls += self.get_target_url(html, link, download_res)
        except:
            pass

        return target_file_urls

    def get_target_url(self, html, link, download_res=[{"name": [], "attrs": {}}]):

        soup = BeautifulSoup(html, "html.parser")
        extr_url_headlines = []
        for download_re in download_res:
            name = download_re["name"]
            attrs = download_re["attrs"]

            target_elements = soup.findAll(name=name, attrs=attrs)

            for element in target_elements:
                headline_ = ""
                if name != ["a"]:
                    for a in element.findAll("a"):
                        if a.has_attr("href"):
                            extr_url = urljoin(link, a["href"])
                            headline = remove_space(a.text)
                            if headline_:
                                headline = headline_
                            extr_url_headlines.append((extr_url, headline))
                else:
                    if element.has_attr("href"):
                        extr_url = urljoin(link, element["href"])
                    headline = remove_space(element.text)
                    extr_url_headlines.append((extr_url, headline))

        return extr_url_headlines

    def get_web_contents(self, link_headlines, domain_modified_time):
        link_headline_contents = []
        for link, _ in link_headlines:
            if self.skip_link_or_not(link):
                continue
            if not self.modified_or_not(link, domain_modified_time):
                if link == self.Stop_url:
                    self.logger.info(
                        f"\n link {link} is the last url extracted yesterday, stopping"
                    )
                    break

            try:
                html, _ = self.get_html_source(link)
                title, content = self.get_title_content(html)
                if self.skip_cont_or_not(content):
                    self.logger.info(
                        f"\n skipping {link} because can't get good content"
                    )
                    continue

                link_headline_contents.append((link, title, content))
                self.logger.info(f"\n  title, content extracted from link: {link}")
            except Exception as e:
                self.logger.info(
                    f"\n  failed in link: {link}, going to next link. \n  "
                    f"Error Message: {str(e)}"
                )
                self.logger.info("".join(traceback.format_tb(e.__traceback__)))

        return link_headline_contents

    def get_html_source(self, url):
        # get html page with selenium
        self.Driver.get(url)
        time.sleep(random.uniform(6, 9))
        html = self.Driver.page_source
        url = self.Driver.current_url

        return html, url

    def process_content(self, link_headline_contents, domain_modified_time):
        # summarize text
        Datetime = datetime.now().strftime("%y%m%d")
        for link_headline_content in link_headline_contents:
            try:
                link, headline, content = link_headline_content
                content = self.clean_cont(headline, content)
                content = remove_space(content)
                # if contents already crawled, pass
                crawled_headlines = [data[3] for data in self.Excel_list]
                crawled_contents = [data[4] for data in self.Excel_list]
                if content in crawled_contents or headline in crawled_headlines:
                    continue
                sum_ = " "#self.Sumapp.summarize(content)
                columns = re.sub(r"\w+", "?", self.Db_column)
                self.c.execute(
                    f"INSERT INTO {self.table_name}({self.Db_column})"
                    f" VALUES ({columns})",
                    (self.Current_id, link, Datetime, headline, sum_),
                )
                self.Excel_list.append(
                    [self.Current_id, link, Datetime, headline, sum_]
                )

                self.Current_id += 1
                self.logger.info(f"\n  Content of {link} saved")
            except Exception as e:
                self.logger.info(f"\n  Failed when process: {link}")
                self.logger.info("".join(traceback.format_tb(e.__traceback__)))
                domain_modified_time.pop(link, None)

            self.Crawl_history["start_id"] = self.Current_id

    def modified_or_not(self, url, domain_modified_time):

        if url not in domain_modified_time:
            domain_modified_time[url] = None
        else:
            return False
        return True

    @staticmethod
    def get_title_content(html):
        # get title and content
        doc = Document(html)
        title = doc.title()
        soup = BeautifulSoup(doc.summary(), "html.parser")
        cont = soup.get_text()

        return title, cont

    def is_overlap(self, extr_url_headlines, domain_modified_time):
        # only get new news
        for extr_url, _ in extr_url_headlines:
            if extr_url in domain_modified_time:
                self.logger.info(
                    f"link {extr_url} already extracted, " "won't go to next page"
                )
                return True
        return False

    def close(self):
        # commit and close
        self.Driver.close()
        self.conn.close()
        self.logger.info("\n  all task finished")
        self.close_log()

    @staticmethod
    def clean_headline(headline):
        # remove marks from headline
        remove_texts = [" &quot;"]
        for text in remove_texts:
            headline = headline.replace(text, "")
        return headline

    @staticmethod
    def clean_cont(title, text):
        # remove datatime and marks from text

        if text.find(title) < len(title):
            text = text.replace(title, "", 1)
        text = remove_space(text)

        for mark in ["&#39;", "&quot;", "■", "▲", "◆", "◇"]:
            text = text.replace(mark, " ")
        idx = 18
        try:
            text_s = text[:idx]
            text_m = text[idx:-idx]
            text_e = text[-idx:]
            try:
                clean_text_s = "".join(parse(text_s, fuzzy_with_tokens=True)[1])
            except:
                clean_text_s = text_s
            try:
                clean_text_e = "".join(parse(text_e, fuzzy_with_tokens=True)[1])
            except:
                clean_text_e = text_e
            text = clean_text_s + text_m + clean_text_e
        except:
            pass

        return text

    @staticmethod
    def skip_link_or_not(url):
        # skip the url if it's not good
        ng_list = ["javascript", "www.youtube.com"]
        for ng_ele in ng_list:
            if ng_ele in url:
                return True

        return False

    @staticmethod
    def skip_cont_or_not(text):
        # skip url if can't get good content
        if not text:
            return True
        else:
            return False

    @staticmethod
    def save_excel(list_conts, filena, columns=""):
        columns = columns.split(",")
        print(columns)
        print(list_conts)

        to_xls_data = pd.DataFrame(list_conts, columns=columns)
        to_xls_data.to_excel(filena)
