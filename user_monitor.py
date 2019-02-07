
# coding: utf-8

# In[6]:


import pyscreenshot
from time import strftime, sleep
import os, sys
import pandas as pd


# In[7]:


def get_screenshot():
    im = pyscreenshot.grab()
    im.save(os.getcwd()+'/files/'+strftime('%d %b%Y %H-%M.png'))


# In[8]:


def get_ps_top_processes() -> pd.DataFrame:
    # getting output from ps command
    proc = os.popen("ps -e -o pcpu,pmem,comm | sort -nrk 3,3 | head -n 30")
    out = proc.read()
    proc.close()

    processes = out.split('\n')
    nfields = len(processes[0].split()) - 1
    process = []
    for row in processes[1:]:
        process.append(row.split(None, nfields))
        
    df = pd.DataFrame(process[:-1])
    df.columns = processes[0].split()

    return df


# In[9]:


# preprocessing df of top processes paramsgetTopProcesses
def _transform_data(df) -> pd.DataFrame:
    tmp = df
    ser = pd.Series(['100.0', '100.0', 'total'],
                    index=['%CPU', '%MEM', 'COMMAND'])
    tmp = tmp.append(ser, ignore_index=True)
    tmp['%CPU'] = tmp['%CPU'].astype(float)
    tmp['%MEM'] = tmp['%MEM'].astype(float)
    tmp = tmp.groupby('COMMAND').sum()
    
    return tmp


# In[10]:


def _add_results_to_stats(df):
    result = pd.read_csv('statistics.csv')
    result = result.groupby('COMMAND').sum()
    result = result.append(df, sort=True)
    result = result.groupby('COMMAND', sort=True).sum()
    result.to_csv('statistics.csv', index=True)


# In[11]:


def monitor(time):
    try:
        while(1):
            get_screenshot()
            _add_results_to_stats(_transform_data(get_ps_top_processes()))
            sleep(time)       
    except KeyboardInterrupt:
        print('interrupted')


# In[12]:


def _init_statistics_file():
    if not os.path.exists('statistics.csv'):
        with open('statistics.csv', 'w+') as f:
            pass
        ser = pd.DataFrame({'%CPU': ['0.0'], '%MEM': ['0.0'], 
                            'COMMAND': ['total']})
        ser = ser.groupby('COMMAND').sum()
        ser.to_csv('statistics.csv', index=True)
    else:
        pass


# In[13]:


def main_function(interval=60):
    _init_statistics_file()
    monitor(interval)


# In[15]:


if __name__ == '__main__':
    main_function(int(float(sys.argv[1])))    

