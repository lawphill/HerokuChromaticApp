#!/usr/bin/python

from math import factorial,exp,log
from itertools import permutations,combinations_with_replacement,combinations
from numpy import matrix,append,zeros,ones,mean,divide,sum,dot
from cmath import sqrt,pi
from flask import request

def default_page(request):
    # These will be the default values
    c = { 'red': 0,
            'green': 0,
            'blue': 0,
            'str': 0,
            'dex': 0,
            'int': 0,
            'X' : 12,
    }
    return c

def process_data(request):
    # Let's process all the input
    [red,green,blue] = check_input(['red','green','blue'],1,6,[1,1,1],request)
    [STR] = check_input(['str'],0,'inf',[0],request)
    [DEX] = check_input(['dex'],0,'inf',[0],request)
    [INT] = check_input(['int'],0,'inf',[0],request)
    [X] = check_input(['X'],1,'inf',[12],request)

    # Formatting
    colors = [red,green,blue]
    req = [STR,DEX,INT]

    # Create modified desired list, so its in format [1,1,2,2,3,3]
    desired = []
    for i in range(0,3):
        for j in range(0,colors[i]):
            desired.append(i+1)

    # Color weights
    p = [r+X for r in req]
    sump = float(sum(p))
    Pr = p[0] / sump
    Pg = p[1] / sump
    Pb = p[2] / sump

    N = sum(colors)
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
    for i in combs:
        T[count,:] = Pcomb[:]
        # Self transition prob is lowered, can't return same permutation
        T[count,count] = (Pcomb[count]-Pperm[count])/(1-Pperm[count])
        total = sum(T[count,:])
        T[count,:] = divide(T[count,:],total)

        # If we reach the desired state we're done
        if list(i) == desired:
            T[count,:] = 0
            T[count,count] = 1
            ind = count
        
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
    mean_chromes = str(int(mean(t)))

    # Calculate the median
    # The solution for n for .5 = 1 - (1-p)**n is
    # (-.69315 + 6.2832i * n_inf)/log(1-p)
    # or (-log(2) + 2i * pi * n_inf)/log(1-p)
    n_inf = 1 # This can be any real number

    T[ind,ind] = 0
    prob_per_chrome = float(dot(matrix(Pcomb),T[:,ind]))
    complex_num = (-log(2) + 2*sqrt(-1)*pi*n_inf)/log(1-prob_per_chrome)
    median_chromes = str(int(complex_num.real))

    # Calculate probability after some number of chromes (inexact for some cases)
    n_to_try = 100
    prob_so_far = 1 - (1 - prob_per_chrome)**n_to_try

    c = { 'red': red,
        'green': green,
        'blue': blue,
        'str': STR,
        'dex': DEX,
        'int': INT,
        'X': X,
        'color_str': str(colors),
        'req_str': str(req),
        'X_str': str(X),
        'median_chromes': median_chromes,
        'mean_chromes': mean_chromes,
        'n_to_try': str(n_to_try),
        'prob_so_far': str(prob_so_far)}

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
