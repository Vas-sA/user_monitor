
# coding: utf-8

# In[1]:


import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime as dt


# In[2]:


def check_image_for_logo(img, *logos) -> list:
    img_rgb = cv2.imread(img)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    for logo in logos:
        template = cv2.imread(logo, 0)
        loc = np.where(cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED) > 0.9)
        
        amount = set()
        for pt in zip(*loc[::-1]):
            sensitivity = 100
            amount.add((round(pt[0]/sensitivity), round(pt[1]/sensitivity)))
        if len(amount)>0:
            return [img, logo]
    return [img, 'no_logos']


# In[3]:


def _filename_to_datetime(name) -> dt:
    return dt.strptime(name, '%d %b%Y %H-%M.png')


# In[13]:


def collect_screenshots_logos_data() -> pd.DataFrame:
    logos = ['logos/'+x for x in os.listdir('logos/')]
    files = os.listdir('screenshots/')
    screenshots = ['screenshots/'+x for x in files if '.png' in x]
    result = []
    for img in screenshots:
        tmp = check_image_for_logo(img, *logos)
        if tmp is not None:
            result.append(tmp)
            
    return pd.DataFrame([x for x in result if x is not None ])


# In[ ]:


def main_function(filename='screenshots_data'):
    data = get_screenshots_logs_data()
    data.to_csv(filename+'csv')


# In[ ]:


if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        print('Collecting data from screenshots'.format(filename))
        main_function(filename)
        print('Done')
    except IndexError:
        print('Collecting data from screenshots')
        main_function()
        print('Done')
   

