from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pytz
from numpy.random import RandomState
import time
import pdb
import math

BIG_COST = 1000000
min_occupancy = 190
max_occupancy = 220

# Sort families based on number of family members
family_members = np.zeros([no_families])
for i in range(0,no_families):
    no_people = family_data[i,-1]
    family_members[i] = no_people

family_inds = np.argsort(family_members)

ForwardMatrix = np.zeros([no_families,no_days]).astype(int)
day_count = np.zeros(no_days).astype(int)
prng = RandomState(int(time.time()))
#for i in range(no_families-1,-1,-1):
for i in range(0,no_families):
    ind = family_inds[i]
    choices = family_data[ind,1:-1]
    no_people = family_data[ind,-1]

    assigned = False
    for day in choices:
        assigned_ind = None
        if day_count[day-1] + no_people <= min_occupancy:
            assigned_ind = day -1 
            break

    if not assigned_ind:
        for day in choices:
            if day_count[day-1] + no_people <= max_occupancy:
                assigned_ind = day -1 
                break


    while not assigned_ind:
        #q = prng.randint(0,no_days)
        possible_choices = np.argsort(day_count)
        q = possible_choices[0]
        if day_count[q] + no_people <= max_occupancy:
            assigned_ind = q
            break

    ForwardMatrix[i,assigned_ind] = no_people
    day_count[assigned_ind] += no_people

print(calculate_total_cost(ForwardMatrix))




# Row mathcing
ForwardMatrix = np.zeros([no_families,no_days]).astype(int)
day_count = np.zeros(no_days).astype(int)
prng = RandomState(int(time.time()))
#for i in range(no_families-1,-1,-1):
for i in range(0,no_families):
    ind = family_inds[i]
    choices = family_data[ind,1:-1]
    no_people = family_data[ind,-1]

    assigned = False
    for day in choices:
        assigned_ind = None
        if day_count[day-1] + no_people <= min_occupancy:
            assigned_ind = day -1 
            break

    if not assigned_ind:
        for day in choices:
            if day_count[day-1] + no_people <= max_occupancy:
                assigned_ind = day -1 
                break


    while not assigned_ind:
        #q = prng.randint(0,no_days)
        possible_choices = np.argsort(day_count)
        q = possible_choices[0]
        if day_count[q] + no_people <= max_occupancy:
            assigned_ind = q
            break

    ForwardMatrix[i,assigned_ind] = no_people
    day_count[assigned_ind] += no_people

print(calculate_total_cost(ForwardMatrix))

