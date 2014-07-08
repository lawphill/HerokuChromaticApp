#!/usr/bin/python

from math import factorial,exp,log
from itertools import combinations_with_replacement
from numpy import matrix,append,zeros,ones,mean,divide,dot
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
            'X' : 12,
            'n_to_try': 100,
            'intro_message': 1
    }
    return c

def process_data(request):
    # Let's process all the input
    [des_r,des_g,des_b] = check_input(['des_r','des_g','des_b'],1,6,[1,1,1],request)
    [curr_r,curr_g,curr_b] = check_input(['curr_r','curr_g','curr_b'],0,6,[0,0,0],request)

    [STR] = check_input(['str'],0,'inf',[0],request)
    [DEX] = check_input(['dex'],0,'inf',[0],request)
    [INT] = check_input(['int'],0,'inf',[0],request)
    [X] = check_input(['X'],1,'inf',[12],request)
    [n_to_try] = check_input(['n_to_try'],1,'inf',[100],request)

    # Formatting
    des_colors = [des_r,des_g,des_b]
    curr_colors = [curr_r,curr_g,curr_b]

    if numpy_sum(curr_colors) > 0:
        curr_entered = 1

	# CHECK FOR ERRORS
        if des_colors == curr_colors or numpy_sum(des_colors) != numpy_sum(curr_colors):
            # End process if curr == des or if items have diff. Nsockets
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
            if des_colors == curr_colors:
                c['error_message'] = "You apparently already have the item you want"
            elif numpy_sum(des_colors) != numpy_sum(curr_colors):
                c['error_message'] = "Your current item has a different number of sockets than your desired item"
            return c  

    else:
        curr_entered = 0

    req = [STR,DEX,INT]

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
    ind = 100 # Set high so that if we find currrent first, it'll be lower than ind
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
        'prob_so_far': round(prob_so_far,3),
        'n_prob': str(n_to_try) + '_' + str(prob_per_chrome),
        'graph_url': 'graphs/' + str(n_to_try) + '_' + str(prob_per_chrome),
	'intro_message': 0}
    return c

def check_input(input_list,min_val,max_val,default,request):
    output_list=[]
    cum_val = 0
    for i in range(len(input_list)):
        input_str = input_list[i]
        if input_str in request.form:
            try:
                input_var = int(request.form[input_str])
            except ValueError:
                input_var = 0
        else:
            input_var = 0

        cum_val += input_var
        output_list.append(input_var)

    # If out of bounds, set to default value
    if cum_val < min_val:
        output_list = default
    # If greater than max_val, don't check if max_val = 'inf'
    elif max_val != 'inf':
        if cum_val > max_val:
            output_list = default
    
    return output_list
