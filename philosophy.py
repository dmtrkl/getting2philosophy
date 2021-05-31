#!/usr/bin/env python
# coding: utf-8

import time
import urllib
from bs4 import BeautifulSoup
import requests      
import re 

def remove_parentheses(string):
    """
    Remove parentheses from a string
    Leave parentheses inside tags as is (e.g links)

    """
    out = ''
    par_mode = 0 # starting symbol is not inside parentheses
    tag_mode = 0 # starting symbol is not surrounded with tags
   
    for char in string:
        # only count tags that outside paragraph parentheses 
        if not par_mode:
            if char == "<":
                tag_mode += 1 
            if char == '>':
                tag_mode -= 1
        # skip symbols within parentheses that are not inside tags 
        if not tag_mode:
            if char == '(':
                par_mode += 1
            if par_mode:
                out += ' '
            else:
                out += char 
            if char == ')':
                par_mode -= 1
        # otherwise leave symbol unchanged
        else:
            out += char
    return out

    
def find_first_link(url):
    """
    Extract main article paragraphs
    Search for the first legit link

    """
    link = None
    response = requests.get(url)
    html = response.text
    tree = BeautifulSoup(html, "html.parser")

    main_paragraphs = tree.find(
        "div", {"id" : "mw-content-text"},recursive=True
    ).div.find_all("p", {"class":None}, recursive=False)

    for paragraph in main_paragraphs:
        p = BeautifulSoup(remove_parentheses(str(paragraph)), "html.parser").p

        if not p.is_empty_element:
            a_tags = p.find_all("a", class_=lambda x: x not in ['new'], recursive=True)

            for a in a_tags:
                if not (
                    a.parent.name == 'i' or
                    a.parent.name == 'sup' or
                    a.parent.name == 'span'
                ):
                    link = a.get('href')
                    break
        if link:
            break

    if not link:
        return 
    
    full_link = urllib.parse.urljoin('https://en.wikipedia.org/', link)
    
    return full_link


def continue_search(history, target_url):
    """
    Check for continuation condition

    """
    if history[-1] == target_url:
        print("Philosophy page is reached, aborting search!")
        return False

    elif history[-1] in history[:-1]:
        print("Stuck in a loop, aborting search!")
        return False

    else:
        return True
    
if __name__ == '__main__':

    start = "https://en.wikipedia.org/wiki/Special:Random"
    target = "https://en.wikipedia.org/wiki/Philosophy"
    visited = [start]

    while continue_search(visited, target):
        print(visited[-1])
        first_link = find_first_link(visited[-1])

        if not first_link:
            print("Arrived to the article without any links, aborting search!")
            break

        visited.append(first_link)
        time.sleep(0.5)
