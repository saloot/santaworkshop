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
import copy

BIG_COST = 100000000
min_occupancy = 140
max_occupancy = 260

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
min_occupancy = 190
max_occupancy = 230

prng = RandomState(int(time.time()))
cost_matrix = copy.deepcopy(C)
#for i in range(no_families-1,-1,-1):

#for i in range(0,no_families):
#    no_people = family_data[i,-1]
#    cost_matrix[i,:] += cost_node(no_people,0)
family_inds = np.argsort(family_members)

current_day = -1
assigned_days = np.zeros(no_families).astype(int)
day_count = np.zeros(no_days).astype(int)
cost_nodes = np.zeros(no_days)
max_cost_tot = 1000000000
for itr in range(0,max_no_optimization_itrs):
    family_inds = np.random.permutation(no_families)
    #
    #ForwardMatrix = np.zeros([no_families,no_days]).astype(int)
    #cost_matrix = C
    
    for i in range(0,no_families):
        max_cost = 100000000
        ind = family_inds[i]
        choices = family_data[ind,1:-1]
        no_people = family_data[ind,-1]

        costs = cost_matrix[ind,:]
        costs_new =costs
        if itr > 0:
            #current_day = np.nonzero(ForwardMatrix[ind,:])[0][0]
            current_day = assigned_days[ind]
            #pdb.set_trace()
            Nd = day_count[current_day] - no_people
            Nd1 = day_count[min(current_day+1,no_days-1)] 
            if Nd < min_occupancy:
                cost_after_leaving = BIG_COST 
            else:
                cost_after_leaving = cost_node(Nd,Nd1)
                

            assigned_ind = current_day
            
            if 1:
                cost_max = C[ind,current_day] + cost_nodes[current_day]
                for j in range(0,no_days):
                    if j == current_day:
                        continue

                    if day_count[j] + no_people > max_occupancy:
                        costs_new[j] = BIG_COST
                    else:
                        Nd = day_count[j] + no_people
                        Nd1 = day_count[min(j+1,no_days-1)] 
                        costs_new[j] = C[ind,j] + cost_node(Nd,Nd1)

                    if cost_after_leaving + costs_new[j] - cost_nodes[j]< cost_max:
                        assigned_ind = j
                        cost_max = cost_after_leaving + costs_new[j] - cost_nodes[j]
                        p = prng.randint(0,1000)
                        if p > 800:
                            break
        else:
            for j in range(0,no_days):
                if day_count[j] + no_people > max_occupancy:
                    costs_new[j] = BIG_COST
                else:
                    Nd = day_count[j] + no_people
                    Nd1 = day_count[min(j+1,no_days-1)] 
                    costs_new[j] = C[ind,j] + cost_node(Nd,Nd1)

                if costs_new[j] < max_cost:
                    assigned_ind = j
                    max_cost = costs_new[j]

            #pdb.set_trace()

                
            #for day in possible_choices:
            #    if day_count[day] + no_people <= min_occupancy:
            #        assigned_ind = day
            #        break

            #if not assigned_ind:
            #    for day in possible_choices:
            #        if day_count[day] + no_people <= max_occupancy:
            #            assigned_ind = day 
            #            break

        
        ForwardMatrix[ind,assigned_ind] = no_people
        
        day_count[assigned_ind] += no_people
        assigned_days[ind] = assigned_ind
        if itr > 0:
            day_count[current_day] -= no_people
            if  current_day != assigned_ind:
                ForwardMatrix[ind,current_day] = 0

    for j in range(0,no_days):
        Nd = day_count[j]
        Nd1 = day_count[min(j+1,no_days-1)] 

        cost_nodes[j] = cost_node(Nd,Nd1)

                
    hard_criteria = sum(sum(ForwardMatrix)>300) + sum(sum(ForwardMatrix)<125)
    cost = calculate_total_cost(ForwardMatrix)
    print(hard_criteria,cost)
    #if itr > 0:
    #    pdb.set_trace()
    if hard_criteria == 0:
        if cost < max_cost_tot:
            max_cost_tot = cost
            creat_submission(ForwardMatrix,str(int(cost)))
        #print(sum(ForwardMatrix))
        print(cost)

    

day_count_opt = np.zeros([no_days])
#for d in range(no_days-1,-1,-1):
#   day_count_opt[d] = min(125 + 2*(no_days-d),247)
for d in range(0,no_days):
    budget = 21030 - sum(day_count_opt)
    d_bar = no_days - d + 1
    if budget < 140 * d_bar:
        day_count_opt[d] = 145
    else:
        day_count_opt[d] = min(260,145 + 2 * d)

i = 0
while sum(day_count_opt) > 21030:
    if day_count_opt[i] > 130:
        day_count_opt[i] -= 1
    i += 1



co = 0
for d in range(0,100):
    Nd = day_count_opt[d]
    Nd1 = day_count_opt[min(d,no_days-1)]

    co += pow(Nd,0.5 + abs(Nd-Nd1)/50.) * (Nd-125)/400.