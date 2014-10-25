#!/usr/bin/python

from math import factorial,exp,log
from itertools import combinations_with_replacement
from numpy import matrix,append,zeros,ones,mean,divide,dot,subtract
from numpy import sum as numpy_sum
from flask import request
from cmath import sqrt,pi

def default_page(request):
    # These will be the default values
    c = { 'curr_r': 0,
            'curr_g': 0,
            'curr_b': 0,
            'des_r': 0,
            'des_g': 0,
            'des_b': 0,
            'str': 0,
            'dex': 0,
            'int': 0,
            'X' : 16,
            'n_to_try': 100,
            'intro_message': 1
    }
    return c

def process_data(request):
    # Let's process all the input
    error_list = []
    [des_r,des_g,des_b], error_list = check_input(['des_r','des_g','des_b'],1,6,request,error_list)
    [curr_r,curr_g,curr_b], error_list = check_input(['curr_r','curr_g','curr_b'],0,6,request,error_list)

    [STR], error_list = check_input(['str'],0,'inf',request,error_list)
    [DEX], error_list = check_input(['dex'],0,'inf',request,error_list)
    [INT], error_list = check_input(['int'],0,'inf',request,error_list)
    [X], error_list = check_input(['X'],1,'inf',request,error_list)
    [n_to_try], error_list = check_input(['n_to_try'],1,'inf',request,error_list)

    # Formatting
    des_colors = [des_r,des_g,des_b]
    curr_colors = [curr_r,curr_g,curr_b]

    try:
        if numpy_sum(curr_colors) > 0: # Did they enter the current colors?
            curr_entered = 1
        else:
            curr_entered = 0
        type_error = 0
    except TypeError:
        curr_entered = 0
        type_error = 1
    try:
        numpy_sum(des_colors) > 0
    except TypeError:
        type_error = 1
        

    # Default to this for error messages
    c = { 'des_r': des_r,
        'des_g': des_g,
        'des_b': des_b,
        'curr_r': curr_r,
        'curr_g': curr_g,
        'curr_b': curr_b,
        'str': STR,
        'dex': DEX,
        'int': INT,
        'X': X,
        'median_chromes': 0,
        'mean_chromes': 0,
        'n_to_try': n_to_try,
        'prob_so_far': str(1.0)}


	# Check for Errors
    if type_error == 0:
        if numpy_sum(des_colors) == 0: # No desired colors entered
            error_list.append("Please enter a valid desired item configuration")
        elif des_colors == curr_colors: # Equivalent items entered
            error_list.append("You apparently already have the item you want")
        elif numpy_sum(des_colors) != numpy_sum(curr_colors) and curr_entered==1: # Diff num sockets
            error_list.append("Your current item has a different number of sockets than your desired item")

    # Quit on error
    if len(error_list) > 0:
        c['error_message'] = error_list
        return c

    req = [STR,DEX,INT]

    # Perform statistics calculations
    median_chromes, mean_chromes, n_to_try, prob_so_far, prob_per_chrome = calc_stats(des_colors,curr_colors,curr_entered,req,X,n_to_try)

    # Calculate Vorici Results
    vorici_1 = 4
    vorici_2_same = 25
    vorici_3_same = 285
    vorici_2_diff = 15
    vorici_3_diff = 100

    # Determine possibly relevant Vorici mods
    poss_vorici = []
    if des_r >= 1:
        poss_vorici.append([1,0,0])
        if des_r >= 2:
            poss_vorici.append([2,0,0])
        if des_g >= 2:
            poss_vorici.append([1,2,0])
        if des_b >= 2:
            poss_vorici.append([1,0,2])

    if des_g >= 1:
        poss_vorici.append([0,1,0])
        if des_r >= 2:
            poss_vorici.append([2,1,0])
        if des_g >= 2:
            poss_vorici.append([0,2,0])
        if des_b >= 2:
            poss_vorici.append([0,1,2])

    if des_b >= 1:
        poss_vorici.append([0,0,1])
        if des_r >= 2:
            poss_vorici.append([2,0,1])
        if des_g >= 2:
            poss_vorici.append([0,2,1])
        if des_b >= 2:
            poss_vorici.append([0,0,2])
        
    # Calculate chances for each Vorici mod
    # NOTE: Ignores curr_colors, also only capturing mean values
    vorici_means = []
    vorici_dict = {}
    best_vorici = -1
    best_vorici_mean = -1
    for vorici_colors in poss_vorici:
        altered_colors = subtract(des_colors,vorici_colors)
        vor_median_chromes, vor_mean_chromes, vor_n_to_try, vor_prob_so_far, vor_prob_per_chrome = calc_stats(altered_colors,[0,0,0],0,req,X,n_to_try)

        vorici_means.append(vor_mean_chromes)

        if vor_mean_chromes < best_vorici_mean or best_vorici_mean == -1:
            best_vorici_mean = vor_mean_chromes
            best_vorici = vorici_colors

    # Determine proper multiplier
    if numpy_sum(best_vorici) == 1:
        vorici_mult = vorici_1
    elif numpy_sum(best_vorici) == 2:
        if 1 in best_vorici:
            vorici_mult = vorici_2_diff
        else:
            vorici_mult = vorici_2_same
    elif numpy_sum(best_vorici) == 3:
        if 3 in best_vorici:
            vorici_mult = vorici_3_same
        else:
            vorici_mult = vorici_3_diff

    best_vorici_cost = best_vorici_mean * vorici_mult

    

    # Return Information
    c = { 'des_r': des_r,
        'des_g': des_g,
        'des_b': des_b,
        'curr_r': curr_r,
        'curr_g': curr_g,
        'curr_b': curr_b,
        'str': STR,
        'dex': DEX,
        'int': INT,
        'X': X,
        'median_chromes': round(median_chromes,1),
        'mean_chromes': round(mean_chromes,1),
        'n_to_try': n_to_try,
        'prob_so_far': str(round(prob_so_far*100,1)) + '%',
        'n_prob': str(n_to_try) + '_' + str(prob_per_chrome),
        'graph_url': 'graphs/' + str(n_to_try) + '_' + str(prob_per_chrome),
	'intro_message': 0,
        'vorici_colors': best_vorici,
        'vorici_mean': best_vorici_mean,
        'vorici_cost': best_vorici_cost}
    return c

def check_input(input_list,min_val,max_val,request,error_list):
    output_list=[]
    cum_val = 0
    error_message = 0
    for i in range(len(input_list)):
        input_str = input_list[i]
        if input_str in request.form:
            if request.form[input_str] != '':
                try:
                    input_var = int(request.form[input_str])
                except ValueError:
                    input_var = request.form[input_str]
                    error_message = "Value not an integer"
            else:
                input_var = 0
        else:
            input_var = 0

        if error_message == 0:
            cum_val += input_var

        output_list.append(input_var)

    # If out of bounds, set to default value
    if cum_val < min_val and error_message==0:
        error_message = "Value too small, minimum = " + str(min_val)
    # If greater than max_val, don't check if max_val = 'inf'
    elif max_val != 'inf' and error_message==0:
        if cum_val > max_val:
            error_message = "Value too large, maximum = " + str(max_val)

    if error_message != 0:
        # Unique Error messages for each input
        if input_list == ['des_r','des_g','des_b']:
            error_message = "Desired Colors: " + error_message
        elif input_list == ['curr_r','curr_g','curr_b']:
            error_message = "Current Colors: " + error_message
        elif input_list == ['n_to_try']:
            error_message = "NChr: " + error_message
        elif len(input_list)==1:
            error_message = input_list[0] + ": " + error_message
        error_list.append(error_message)    

    return output_list, error_list

def calc_stats(des_colors,curr_colors,curr_entered,req,X,n_to_try):

    # Create modified desired/current list, so its in format [1,1,2,2,3,3]
    desired = []
    for i in range(0,3):
        for j in range(0,des_colors[i]):
            desired.append(i+1)

    current = []
    for i in range(0,3):
        for j in range(0,curr_colors[i]):
            current.append(i+1)        

    # Color weights
    p = [r+X for r in req]
    sump = float(numpy_sum(p))
    Pr = p[0] / sump
    Pg = p[1] / sump
    Pb = p[2] / sump

    N = sum(des_colors)
    Nfact = factorial(N)

    combs_iter = combinations_with_replacement([r+1 for r in range(3)],N)

    # Bring this into a usable form
    combs = []
    for i in combs_iter:
        combs.append(i)

    Ncombs = len(combs)
    Pcomb = []
    Pperm = []

    # Calculate probability of each combination
    for i in combs:
        Nr = i.count(1)
        Ng = i.count(2)
        Nb = i.count(3)
        Pperm.append(Pr**Nr * Pg**Ng * Pb**Nb)
        Pcomb.append(Nfact/(factorial(Nr)*factorial(Ng)*factorial(Nb)) * Pr**Nr * Pg**Ng * Pb**Nb)
    
    # Create Transition Matrix
    T = zeros((Ncombs,Ncombs))
    count = 0
    ind = 100 # Set high so that if we find current first, it'll be lower than ind
    for i in combs:
        T[count,:] = Pcomb[:]
        # Self transition prob is lowered, can't return same permutation
        T[count,count] = (Pcomb[count]-Pperm[count])/(1-Pperm[count])
        total = numpy_sum(T[count,:])
        T[count,:] = divide(T[count,:],total)

        # If we reach the desired state we're done
        if list(i) == desired:
            T[count,:] = 0
            T[count,count] = 1
            ind = count
        if list(i) == current:
            curr_ind = count
            if curr_ind > ind:
                curr_ind-=1 # This adjusts the index to fit smaller matrix t
        
        count += 1

    # Create Fundamental Matrix & Identity Matrix
    # Notation from  http://en.wikipedia.org/wiki/Absorbing_Markov_chain
    Q = zeros((Ncombs-1,Ncombs-1))
    I = zeros((Ncombs-1,Ncombs-1))

    for i in range(len(T)):
        if i < ind:
            xind = i
        elif i > ind:
            xind = i-1

        else:
            xind = -1
        
        for j in range(len(T)):
            if j < ind:
                yind = j
            elif j > ind:
                yind = j-1
            else:
                yind = -1
            if xind > -1 and yind > -1:
                Q[xind,yind] = T[i,j]
                if xind == yind:
                    I[xind,yind] = 1
                          
    Nmat = matrix(I-Q)
    Nmat = Nmat.I
    t = Nmat * ones((len(Nmat),1))
    if curr_entered == 0:
        mean_chromes = float(mean(t))
    else:
        mean_chromes = float(t[curr_ind])
    

    # Modify T so that T[:,ind] represents the matrix R, probability of going from any transient state to the absorbing state, multiply by the probability of being in any transient state
    T[ind,ind] = 0
    R = zeros((Ncombs-1,1))
    count = 0
    for val in T[:,ind]:
        if val != 0:
            R[count,0] = val
            count += 1

    prob_trans = zeros((1,Ncombs-1))
    count=0
    for i in range(len(Pcomb)):
        if i != ind:
            prob_trans[0,count] = Pcomb[i]
            count += 1
    prob_trans = divide(prob_trans,numpy_sum(prob_trans))

    prob_per_chrome = float(dot(prob_trans,R))

    # Calculate Median & cdf after n_to_try chromes
    stopping_point = 5000 # This is where we stop calculating exactly and start approximating
    cum_prob_failure = 1
    found_median = 0

    # Calculate probability after some number of chromes (inexact)
    curr_state = zeros((1,Ncombs-1))
    if curr_entered == 0:
        count = 0
        for i in range(len(Pcomb)):
            if i != ind:
                curr_state[0,count] = Pcomb[i]
                count += 1
        
    else:
        # We know where we're starting, so let's calculate more exactly
        curr_state[0,curr_ind] = 1 # We know 100% what state we start in
        
    # Force sum(curr_state) = 1
    curr_state = divide(curr_state,numpy_sum(curr_state))

    for i in range(stopping_point):
        prob_failure = 1 - float(dot(curr_state,R))
        cum_prob_failure = cum_prob_failure * prob_failure
            
        curr_state = dot(curr_state,Q) # Update current state
        curr_state = divide(curr_state,numpy_sum(curr_state)) # Normalize to create pdf

        if i+1 == n_to_try:
            prob_so_far = 1 - cum_prob_failure

        prob_success = 1 - cum_prob_failure
        if prob_success >= .5 and found_median==0:
            median_chromes = i+1
            found_median = 1

    prob_per_chrome = float(dot(curr_state,R))

    if n_to_try > stopping_point: # Approximate the remaining chromes using prob_per_chrome
        n_leftover = n_to_try - stopping_point
        cum_prob_failure = cum_prob_failure * (1-prob_per_chrome)**n_leftover
        prob_so_far = 1 - cum_prob_failure
    # We may need to still calculate the median
    if found_median == 0:
        # Calculate the median
        # The solution for n_left for .5 = 1 - cum_prob_failure*(1-p)**n_left is
        # (log(1/(2*cum_prob_failure)) + 2i * pi * n_inf)/log(1-p), where log is the natural log
        # Taking the real portion of this complex number gives the median
        n_inf = 1 # This can be any real integer
        complex_num = (log(1/(2*(1-prob_so_far))) + 2*sqrt(-1)*pi*n_inf)/log(1-prob_per_chrome)
        chromes_left = float(complex_num.real)
        median_chromes = n_to_try + chromes_left

    return median_chromes, mean_chromes, n_to_try, prob_so_far, prob_per_chrome


