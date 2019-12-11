from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pytz
from numpy.random import RandomState
import time
import pdb

BIG_COST = 1000000
min_occupancy = 125
max_occupancy = 300

import math

def inv_sigmoid(x,alpha,beta):
  return 1 / (alpha + math.exp(x-beta))

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

        #if Nd < min_occupancy or Nd > max_occupancy:
        #    cost += BIG_COST

    return cost

def cost_node(Nd,Nd1):
    if Nd < min_occupancy:
        return -BIG_COST
    elif Nd > max_occupancy:
        return BIG_COST
    else:
        return pow(Nd,0.5 + abs(Nd-Nd1)/50.) * max(Nd-125,0)/400.

days_popularity = np.zeros([no_days,10])
for i in range(0,no_families):
    choices = family_data[i,1:-1]
    no_people = family_data[i,-1]
    for itr in range(0,len(choices)):
        days_popularity[choices[itr]-1,itr] += no_people

days_popularity_tot = sum(days_popularity.T)


cutoff_orig = 10
max_no_optimization_itrs = 1000
choices_inds = np.zeros([no_families,1]).astype(int)
BackwardMatrix = np.zeros([no_families,no_days]).astype(int)
max_cost = 100000000
prng = RandomState(int(time.time()))
for itr in range(0,max_no_optimization_itrs):
    ForwardMatrix = np.zeros([no_families,no_days]).astype(int)
    previous_choices_inds = choices_inds
    choices_inds = np.zeros([no_families,1]).astype(int)

    cutoff = cutoff_orig/(1.+itr)
    # Forward step: people send their schedule to the constraints
    family_inds = np.random.permutation(no_families)
    day_count = np.zeros([no_days,1]).astype(int)
    zero_vec = np.zeros([no_days,1])
    for i in family_inds:
        choices = family_data[i,1:-1]
        no_people = family_data[i,-1]
        
        # Check the messages comming from neighbors
        feedback = np.reshape(BackwardMatrix[i,:],[no_days,1])

        # Adjust the choice based on the feedback coming from constraints
        #if itr > 0:
        #    pdb.set_trace()
        overall_feedback = sum(feedback) #sum(feedback > 0) - sum(feedback < 0) 

        # randomly select the node with least cost
        feedback = np.multiply(day_count/300.-1,feedback)
        #feedback = np.multiply(day_count/135.-1,feedback)
        possible_choices = np.argsort(feedback.ravel())#[0:10]

        #if overall_feedback > cutoff:
        #    new_ind = previous_choices_inds[i] #min(previous_choices_inds[i]+1,9)
        #elif overall_feedback < -cutoff:
        #    new_ind = min(previous_choices_inds[i]+1,9) #max(previous_choices_inds[i]-1,0)
        #else:
        #    new_ind = previous_choices_inds[i]
        
        #choice = choices[new_ind]
        
        # Keep new index by random
        p = prng.randint(0,1000)
        if p >= 800:
            choice = possible_choices[0]
        #elif p >=85:
        #    choice = possible_choices[1]
        #elif p >=80:
        #    choice = possible_choices[2]
        elif p >= 700:
            q = prng.randint(1,10)
            choice = choices[q]-1
        else:
            q = prng.randint(1,no_days)
            choice = possible_choices[q]#-1
            #new_ind = previous_choices_inds[i]
        
        try:
            new_ind = list(choices).index(choice+1)
        except:
            new_ind = -1    

        choices_inds[i] = new_ind
        ForwardMatrix[i,choice] = no_people
        day_count[choice] += no_people
        #if day_count[choice]>301:
        #    pdb.set_trace()

    print(day_count.std())
    hard_criteria = sum(sum(ForwardMatrix)>300) + sum(sum(ForwardMatrix)<125)
    cost = calculate_total_cost(ForwardMatrix)
    print(hard_criteria,cost)
    if hard_criteria == 0:
        
        if cost < max_cost:
            max_cost = cost
            creat_submission(ForwardMatrix,str(int(cost)))
        #print(sum(ForwardMatrix))
        print(cost)
#    if itr > 0:
#        pdb.set_trace()

    # Backward step
    BackwardMatrix = np.zeros([no_families,no_days]).astype(int)
    occupancy_count = sum(ForwardMatrix)
    occupancy_count_mean = occupancy_count.mean()
    for j in range(0,no_days):
        
        # Check the messages comming from neighbors
        feedback = ForwardMatrix[:,j]

        # Adjust the choice based on the feedback coming from constraints
        m_base = 0
        if sum(feedback) > max_occupancy:
            m_base = .5 *(max_occupancy - sum(feedback))
        elif sum(feedback) < min_occupancy:
            m_base = .2 * (min_occupancy - sum(feedback))
        
        #for i in np.nonzero(feedback)[0]:
        Nd = 0.0001 + occupancy_count[j]
        Nd1 = occupancy_count[min(j+1,no_days-1)] 
        m_base = 0
        for i in range(0,no_families):
            no_people = family_data[i,-1]
            choices = family_data[i,1:-1]
            #try:
            #    choice_ind = list(choices).index(j+1)
            #except:
            #    choice_ind = -1
            # TODO: use Cij instead of calculate_cost()
            #Cij = calculate_cost(choice_ind,no_people)
            Cij = C[i,j]
            #if feedback[i] != 0:
            #    cost_diff = cost_node(Nd,Nd1) - cost_node(Nd-no_people,Nd1)
            #else:
            #    cost_diff = cost_node(Nd+no_people,Nd1) - cost_node(Nd,Nd1)
            #cost_diff = min(max(cost_diff,-BIG_COST),BIG_COST)

            #m = m_base - Cij - abs(Nd - Nd+1)/2.5 + 1000*no_people /(Nd + 0.0001)
            BackwardMatrix[i,j] =  Cij + no_people * (Nd - occupancy_count_mean)/.5 + 20 * math.log(1+Nd)# *(2-days_popularity_tot[j]/max(days_popularity_tot))
