from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pytz

BIG_COST = 1000000
min_occupancy = 125
max_occupancy = 300

def calculate_total_cost(assignment_matrix):
    """
    This function calculates the total cost of assigning families
    a given day, accounting for their preferred schedule as well
    as the family size.

    params:
    assignment_matrix: a N*D assignment matrix

    output params:
    cost: the cost of assigning the families to the days
    """

    cost = 0
    no_families = assignment_matrix.shape[0]
    no_days = assignment_matrix.shape[1]
    

    for i in range(0,no_families):
        choices = family_data[i,1:-1]
        no_people = family_data[i,-1]
        d = np.nonzero(assignment_matrix[i,:])[0][0]
        try:
            choice = list(choices).index(d+1)
        except:
            choice = -1

        cost += calculate_cost(choice,no_people)

    occupancy_count = sum(assignment_matrix)
    for j in range(0,len(occupancy_count)):
        Nd = occupancy_count[j] 
        
        Nd1 = occupancy_count[min(j+1,no_days-1)] 
        cost += pow(Nd,0.5 + abs(Nd-Nd1)/50.) * max(Nd-125,0)/400.

        if Nd < min_occupancy or Nd > max_occupancy:
            cost += BIG_COST

    return cost


cutoff_orig = 10
max_no_optimization_itrs = 100
choices_inds = np.zeros([no_families,1]).astype(int)
for itr in range(0,max_no_optimization_itrs):
    ForwardMatrix = np.zeros([no_families,no_days]).astype(int)
    previous_choices_inds = choices_inds
    choices_inds = np.zeros([no_families,1]).astype(int)

    cutoff = cutoff_orig/(1.+itr)
    # Forward step: people send their schedule to the constraints
    for i in range(0,no_families):
        choices = family_data[i,1:-1]
        no_people = family_data[i,-1]
        
        # Check the messages comming from neighbors
        feedback = BackwardMatrix[i,:]

        # Adjust the choice based on the feedback coming from constraints
        #if itr > 0:
        #    pdb.set_trace()
        overall_feedback = sum(feedback) #sum(feedback > 0) - sum(feedback < 0) 

        # randomly select the node with least cost
        choice = np.argmax(feedback)

        #if overall_feedback > cutoff:
        #    new_ind = previous_choices_inds[i] #min(previous_choices_inds[i]+1,9)
        #elif overall_feedback < -cutoff:
        #    new_ind = min(previous_choices_inds[i]+1,9) #max(previous_choices_inds[i]-1,0)
        #else:
        #    new_ind = previous_choices_inds[i]
        
        #choice = choices[new_ind]
        try:
            new_ind = list(choices).index(choice+1)
        except:
            new_ind = -1    
        choices_inds[i] = new_ind
        ForwardMatrix[i,choice] = no_people
    print(sum(sum(ForwardMatrix))/100.)

    print(calculate_total_cost(ForwardMatrix))
    # Backward step
    BackwardMatrix = np.zeros([no_families,no_days]).astype(int)
    for j in range(0,no_days):
        
        # Check the messages comming from neighbors
        feedback = ForwardMatrix[:,j]

        # Adjust the choice based on the feedback coming from constraints
        m_base = 0
        if sum(feedback) > max_occupancy:
            m_base = 2000 *(max_occupancy - sum(feedback))
        elif sum(feedback) < min_occupancy:
            m_base = 20 * (min_occupancy - sum(feedback))
        
        #for i in np.nonzero(feedback)[0]:
        for i in range(0,no_families):
            if 1:#m == 0:
                no_people = family_data[i,-1]
                choices = family_data[i,1:-1]
                try:
                    choice = list(choices).index(j+1)
                except:
                    choice = -1

                m = m_base -calculate_cost(choice,no_people)
            BackwardMatrix[i,j] = m

