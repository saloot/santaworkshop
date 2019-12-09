from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pytz

def creat_submission(assignment_matrix,file_suffix = ''):
    """
    This function creates a submission for kaggle based on the
    assignment matrix

    params:
    assignment_matrix: a N*D assignment matrix

    output params:
    submission: a N*2 matrix containing the assigned date for 
    each family
    """

    no_families = assignment_matrix.shape[0]
    no_days = assignment_matrix.shape[1]
    submission = np.zeros([no_families,2])

    for i in range(0,no_families):
        choices = family_data[i,1:-1]
        no_people = family_data[i,-1]
        family_id = family_data[i,0]
        d = np.nonzero(assignment_matrix[i,:])[0][0]
        submission[i,0] = family_id
        submission[i,1] = d+1

    submission = submission.astype(int)

    # write to file
    file_name = "./Results/submission_" + file_suffix + ".csv"
    file = open(file_name,'w')
    detail = ['family_id','assigned_day']
    writer = csv.writer(file)
    writer.writerow(detail)

    for i in range(0,no_families):
        detail = submission[i,:]
        writer.writerow(detail)

    return 1

def calculate_cost(choice_no: int,no_people: int):
    """
    This function calculates the cost of assigning a family to
    a given day, accounting for their preferred schedule as well
    as the family size.

    params:
    choice_no: indicated the desirability of the speicifed day 
                according to the families schedule, 0 being the
                most desirable
    no_people: Number of the people in the family

    output params:
    cost: the cost of assigning the family to the day specified 
          by the choice number
    """

    if choice_no == 0:
        cost = 0
    elif choice_no == 1:
        cost = 50
    elif choice_no == 2:
        cost = 50 + 9 * no_people
    elif choice_no == 3:
        cost = 100 + 9 * no_people
    elif choice_no == 4:
        cost = 200 + 9 * no_people
    elif choice_no == 5:
        cost = 200 + 18 * no_people
    elif choice_no == 6:
        cost = 300 + 18 * no_people
    elif choice_no == 7:
        cost = 300 + 36 * no_people
    elif choice_no == 8:
        cost = 400 + 36 * no_people
    elif choice_no == 9:
        cost = 500 + 36 * no_people + 199 * no_people
    else:
        cost = 500 + 36 * no_people + 398 * no_people

    return cost



# Load Family Data
file_name = './Data/family_data.csv'
f = open(file_name,'r')
reader = csv.reader(f)
data_ub = list(reader)
no_families = len(data_ub)-1
no_days = 100 #max(sample_submission[:,1])

family_data = np.zeros([no_families,12])
for itr in range(1,len(data_ub)):
    item = data_ub[itr]
    family_data[itr-1,:] = item
family_data = family_data.astype(int)

# Create cost matrix
C = np.zeros([no_families,no_days])
for i in range(0,no_families):
    choices = family_data[i,1:-1]
    no_people = family_data[i,-1]
    family_id = family_data[i,0]

    for itr in range(0,len(choices)):
        j = choices[itr]
        C[i,j-1] = calculate_cost(itr,no_people)

    for j in range(1,no_days+1):
        if j in choices:
            continue
        else:
            C[i,j-1] = calculate_cost(-1,no_people)

    
