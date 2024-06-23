#!/usr/bin/env python

import os
import random
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sugarcube_test.html')

# returns True if tag is not a link or a header or footer
def is_basic_text(tag):
    return tag.name != 'a' and tag.name != 'div'

# automated player for sugarcube defaults using selenium
def test(driver, output_path='output.txt', dump_stats=1, script_path='transcript.txt', data_path='data.json'):
    script = []
    transcript = ''
    current_paragraphs = set()
    driver.get('file://' + file_path)
    # this returns all of the twine links on the page.
    # TODO: might want to tweak this to only find links within a div?
    # Or if links are 'button' rather than 'a'
    link_divs = driver.find_elements(By.XPATH, '//a[@class="link-internal"]')
    # this command gets the sugarcube internal variables.
    data = driver.execute_script('return JSON.stringify(window.SugarCube.State.active.variables, null, 2);');
    while len(link_divs) > 0:
        print('NEW SCENE')
        # this tries to get the main text of the passage.
        content_text = driver.find_elements(By.XPATH, '//div[@id="passages"]/div')
        content_text = content_text[0]
        html = content_text.get_attribute('outerHTML')
        # parse content text
        bs = BeautifulSoup(html, 'html.parser')
        # TODO: I don't know how to get all the headers/footers yet
        # all_texts = bs.div.findAll(is_basic_text, text=True)
        # print('len(all_texts):', len(all_texts))
        for i, paragraph in enumerate(bs.stripped_strings):
            paragraph = str(paragraph)
            if len(paragraph.strip()) == 0:
                continue
            # filter paragraphs based on whether they're seen
            if i == 0 and paragraph not in current_paragraphs:
                current_paragraphs = set()
                transcript += '\n'
            current_paragraphs.add(paragraph)
            print('\n ', paragraph)
            transcript += '\n ' + paragraph
        # now, we try to find the links on the page.
        link_divs = driver.find_elements(By.XPATH, '//a[@class="link-internal"]')
        for link in link_divs:
            print('\n -', link.get_attribute('text'))
            transcript += '\n -' + link.get_attribute('text')
        if len(link_divs) == 0:
            break
        # click on a random link
        link_choice = random.choice(link_divs)
        print('\n>>> ' + link_choice.get_attribute('text'))
        script.append(link_choice.get_attribute('text'))
        transcript += '\n>>> ' + link_choice.get_attribute('text')
        # this is necessary because twine is slow. TODO: tweak these values.
        time.sleep(0.1)
        link_choice.click()
    # after the game is over, save the variables.
    data = driver.execute_script('return JSON.stringify(window.SugarCube.State.active.variables, null, 2);');
    transcript += '\n\nFINAL DATA:\n' + data
    print(data)
    driver.quit()
    with open(output_path, 'w') as f:
        f.write(transcript)
    with open(script_path, 'w') as f:
        for line in script:
            f.write(line + '\n')
    with open(data_path, 'w') as f:
        f.write(data)
    return transcript


def random_n_tests(n, dump_stats=0, starting_index=0):
    for i in range(n):
        i = starting_index + i
        output_path = 'random_test_outputs/{:03d}_output.txt'.format(i)
        script_path = 'random_test_outputs/{:03d}_script.txt'.format(i)
        data_path = 'random_test_outputs/{:03d}_data.txt'.format(i)
        test(output_path=output_path, script_path=script_path, data_path=data_path,
                dump_stats=dump_stats)


if __name__ == '__main__':
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options)
    print(file_path)
    #try:
    test(driver)
    #except:
    #    driver.quit()
