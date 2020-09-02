'''
Eli Lifland
Tool used to run SSTL checks
'''
import sys
import argparse
import osmnx as ox
import sc_loading
import sstl
import sc_plot
import random
import performance
import pandas as pd
import numpy as np
import time
from multiprocessing import Pool
from collections import defaultdict

params = {'chicago': {'co','o3','no2','lightsense','humidity'},
          'aarhus': {'event','hum','nearby_event','spots','vehicles'}
}

workdays = ['2018-04-02','2018-04-10','2018-04-18','2018-04-26','2018-04-27','2018-05-01','2018-05-09','2018-05-17','2018-05-21','2018-05-25','2018-06-01','2018-06-04','2018-06-12','2018-06-20','2018-06-28','2018-07-12','2018-07-17','2018-07-20','2018-07-25','2018-07-30','2018-08-01','2018-08-06','2018-08-14','2018-08-23','2018-08-31','2018-09-07','2018-09-11','2018-09-19','2018-09-24','2018-09-27']

weekends = ['2018-04-07','2018-04-08','2018-04-14','2018-04-15','2018-04-21','2018-05-05','2018-05-06','2018-05-12','2018-05-13','2018-05-20','2018-06-02','2018-06-03','2018-06-09','2018-06-10','2018-06-16','2018-07-08','2018-07-14','2018-07-21','2018-07-22','2018-07-29','2018-08-04','2018-08-05','2018-08-11','2018-08-12','2018-08-18','2018-09-08','2018-09-09','2018-09-22','2018-09-23','2018-09-30']

aarhus_days = ['2014-08-01','2014-08-02','2014-08-03','2014-08-04','2014-08-05','2014-08-06','2014-08-07','2014-08-08','2014-08-09','2014-08-10','2014-08-11','2014-08-12','2014-08-13','2014-08-14','2014-08-15','2014-08-16','2014-08-17','2014-08-18','2014-08-19','2014-08-20','2014-08-21','2014-08-22','2014-08-23','2014-08-24','2014-08-25','2014-08-26','2014-08-27','2014-08-28','2014-08-29','2014-08-30','2014-09-01','2014-09-02','2014-09-03','2014-09-04','2014-09-05','2014-09-06','2014-09-07','2014-09-08','2014-09-09','2014-09-10','2014-09-11','2014-09-12','2014-09-13','2014-09-14','2014-09-15','2014-09-16','2014-09-17','2014-09-18','2014-09-19','2014-09-20','2014-09-21','2014-09-22','2014-09-23','2014-09-24','2014-09-25','2014-09-26','2014-09-27','2014-09-28','2014-09-29','2014-09-30']
#holidays = ['2018-05-28','2018-07-04','2018-09-03','2018-10-08']
holidays = weekends[4:8]

holidays = ['2018-05-28','2018-07-04','2018-09-03','2018-10-08']+workdays[:4]+weekends[4:8]
#holidays = weekends[4:8]

def test_reqs():
    to_test = holidays if args.holiday else aarhus_days
    #no args: ASSTL, -p: PASSTL, -c: SSTL
    method = 'PASSTL' if args.parallel else 'ASSTL'
    if not args.cache_locs:
        method = 'SSTL'
    df = pd.DataFrame()
    df_tf = pd.DataFrame()
    req_satisfied = defaultdict(int)
    filename = '{}_stats/{}.csv'.format(args.city,method)
    tf_filename = '{}_stats/{}_tf.csv'.format(args.city,method)
    try:
        df = pd.read_csv(filename,index_col=0)
        df_tf = pd.read_csv(tf_filename,index_col=0)
    except Exception:
        pass
    graph = get_graph(args.city)
    reqs = list()
    for day in to_test:
        checker = sstl.sstl_checker(graph,day,parallel=args.parallel,cache_locs=args.cache_locs,debug=args.debug,params=params[args.city])
        f = open(args.req_file,'r')
        reqs = list()
        for line in f:
            if line == 'END\n':
                break
            name,spec = line.split(':')
            reqs.append(name)
            if name not in df.columns:
                df[name] = np.nan
            if name not in df_tf.columns:
                df_tf[name] = np.nan if args.holiday else False
            s = time.time()
            ans = checker.check_spec(spec[:-1])
            check_time = time.time()-s
            if (ans and not args.holiday) or (ans==0 and args.holiday):
                req_satisfied[name]+=1
            df.at[day,name] = check_time
            df_tf.at[day,name] = ans
            if not args.parallel:
                print('Req {} took {} checks'.format(name,checker.checks))
                checker.checks=0
        print('Finished day {}'.format(day))
        sys.stdout.flush()
    for req in reqs:
        pct_satisfied = (req_satisfied[req]/len(to_test))*100
        print('Req {} is {} pct satisfied'.format(req,pct_satisfied))
    df.to_csv(filename)
    df_tf.to_csv(tf_filename)

def load_work():
    to_load = holidays
    pool = Pool(processes=3)
    pool.map(load_day,to_load)

tagToColor = {
    'school'  : (0,0,255),
    'hospital': (255,0,0),
    'theatre' : (0,255,0),
    'traffic' : (0,0,0),
    'parking' : (255,255,0),
    'library' : (255,0,255),
    'park'    : (0,255,255),
    'high_crime': (255,0,0),
    'weather' : (0,255,0)
}

def get_graph(city,plot=False):
    graph = sc_loading.get_graph(city)
    if plot:
        sc_plot.plot(graph,tagToColor)
    return graph

def load_day(day):
    sc_loading.load_data(args.city,day)

def summarize_comp():
    pdf = pd.read_csv('{}_stats/PASSTL.csv'.format(args.city),index_col=0)
    #sdf = pd.read_csv('{}_stats/SSTL.csv'.format(args.city),index_col=0)
    df = pd.read_csv('{}_stats/ASSTL.csv'.format(args.city),index_col=0)
    SSTL_able = {2}
    for r in range(1,6):
        pavgs = []
        avgs = []
        #savgs = []
        for c in ['A','B','C','D']:
            try:
                avgs.append(np.nanmean(df['R{}{}'.format(r,c)]))
            except Exception:
                pass
            try:
                pavgs.append(np.nanmean(pdf['R{}{}'.format(r,c)]))
            except Exception:
                pass
            #if r in SSTL_able:
                #savgs.append(np.nanmean(sdf['R{}{}'.format(r,c)]))
        print('PASSTL avg for R{} is {}'.format(r,sum(pavgs)/4))
        print('ASSTL avg for R{} is {}'.format(r,sum(avgs)/4))
        #if r in SSTL_able:
            #print('SSTL avg for R{} is {}'.format(r,sum(savgs)/4))


parser = argparse.ArgumentParser(description='Example SSTL')
parser.add_argument('-l',dest='load',action='store_true')
parser.add_argument('-p',dest='parallel',action='store_true')
parser.add_argument('-f',dest='req_file',default='reqs.txt')
parser.add_argument('-c',dest='city',default='aarhus')
parser.add_argument('-d',dest='day',default='2018-04-01')
parser.add_argument('-m',dest='month',action='store_true')
parser.add_argument('-r',dest='reqs',action='store_true')
parser.add_argument('--comp',dest='comp',action='store_true')
parser.add_argument('--hol',dest='holiday',action='store_true')
parser.add_argument('--debug',dest='debug',action='store_true')
parser.add_argument('--cache',dest='cache_locs',action='store_false')
parser.add_argument('--plot',dest='plot',action='store_true')
args = parser.parse_args()
perf = performance.performance_tester()
if args.comp:
    summarize_comp()
elif args.plot:
    get_graph(args.city,plot=True)
elif args.month:
    pool = Pool(processes=3)
    d_strs = list()
    for d in range(1,31):
        d_str = str(d)
        if len(d_str) == 1:
            d_str = '0'+d_str
        d_strs.append('2018-04-{}'.format(d_str))
    pool.map(load_day,d_strs)
elif args.reqs and args.load:
    load_work()
elif args.reqs:
    test_reqs()
elif args.load:
    load_day(args.day)    
