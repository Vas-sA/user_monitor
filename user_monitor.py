# coding: utf-8

import pyscreenshot
from time import strftime, sleep
import os, sys
import pandas as pd



def get_screenshot():
    im = pyscreenshot.grab()
    im.save(os.getcwd()+'/screenshots/'+strftime('%d %b%Y %H-%M.png'))



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



def _add_results_to_stats(df):
    result = pd.read_csv('statistics.csv')
    result = result.groupby('COMMAND').sum()
    result = result.append(df, sort=True)
    result = result.groupby('COMMAND', sort=True).sum()
    result.to_csv('statistics.csv', index=True)



def monitor(time):
    try:
        while(1):
            get_screenshot()
            _add_results_to_stats(_transform_data(get_ps_top_processes()))
            sleep(time)       
    except KeyboardInterrupt:
        print('Interrupted by user.')



def _init_files_dir():
    if not os.path.exists(os.getcwd()+'/files'):
        try:
            original_umask = os.umask(0)
            os.makedirs(os.getcwd()+'/files', 0o777)
        finally:
            os.umask(original_umask)
    


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


def main_function(interval=60):
    _init_files_dir()
    _init_statistics_file()
    monitor(interval)



if __name__ == '__main__':
    try:
        interval = int(float(sys.argv[1]))
        print('Starting user_monitor with {} sec interval'.format(interval))
        main_function(interval)
    except IndexError:
        print('Starting user_monitor with 60 sec interval')
        main_function()
