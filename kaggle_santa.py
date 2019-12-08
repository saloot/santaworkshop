from datetime import datetime, timedelta
import numpy as np
import os
import csv
import pytz


# TODO: Complete this function with -1 being equivalent to the "others" choice
def calculate_cost(choice_no):

    return cost



# Load Family Data
file_name = './Data/family_data.csv'
f = open(file_name,'r')
reader = csv.reader(f)
data_ub = list(reader)
no_families = len(data_ub)
no_days = 100 #max(sample_submission[:,1])

family_data = np.zeros([no_families,12])
for itr in range(1,len(data_ub)):
    item = data_ub[itr]
    family_data[itr,:] = item


# Create cost matrix
C = np.zeros([no_families,no_days])
for in range(0,no_families):
    choices = family_data[i,1:-1]
    no_people = family_data[i,-1]
    family_id = family_data[i,0]

    for itr in range(0,len(choices)):
        j = choices[itr]
        C[i,j] = calculate_cost(itr)

    for j in range(0,no_days):
        if j in choices:
            continue
        else:
            C[i,j] = calculate_cost(-1)

    
