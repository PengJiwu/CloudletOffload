'''
Created on Sep 3, 2014

@author: yzhang28
'''

import pickle
from multiprocessing import Pool, Array

import timeit


import sys
sys.path.append("..")

from Core.MDPfunc import *
from Core.header import *

############################################
# PARAMETERS
############################################
G = 1 + 4
Q = 1 + 6
# N Calculated from LAM and R_COVERAGE at last
A = 2 # two actions: 0 and 1

R_COVERAGE = 10.0

LAM_Q = 0.25
LAM_C = 0.0005
LAM_U = 0.0001

TAU = 0.5
C_TOP = 2
BETAH = 0.5
VELOCITY = 5.0

PENALTY = 20.0

ALPHA_LOCAL = 1.0
ALPHA_REMOTE = 1.0

GAM = 0.80
DELTA = 0.01
############################################


ETA_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
expnum = len(ETA_list)

ParamsSet = [None for _ in range(expnum)]
TransProbSet = [None for _ in range(expnum)]

RESset_bell = [None for _ in range(expnum)]
RESset_myo = [None for _ in range(expnum)]
RESset_rnd = [None for _ in range(expnum)]
RESset_zero = [None for _ in range(expnum)]
RESset_one = [None for _ in range(expnum)]

V_opt_set_bell = [None for _ in range(expnum)]
A_opt_set_bell = [None for _ in range(expnum)]

tic = timeit.default_timer()

for ind, eta_cur in enumerate(ETA_list):
    print "---- ROUND:", ind+1,
    print "out of", expnum
    N = GetUpperboundN(LAM_C, R_COVERAGE)[0]
    ParamsSet[ind] = {'ETA_DIRECT': eta_cur, \
                      'G': G, 'Q': Q, 'N': N, \
                      'A': A, \
                      'R_COVERAGE': R_COVERAGE, \
                      'LAM_Q': LAM_Q, 'LAM_C': LAM_C, 'LAM_U': LAM_U, \
                      'TAU': TAU, 'C_TOP': C_TOP, 'BETAH':BETAH, 'VELOCITY':VELOCITY, \
                      'PENALTY': PENALTY, \
                      'ALPHA_LOCAL': ALPHA_LOCAL, 'ALPHA_REMOTE': ALPHA_REMOTE, \
                      'GAM': GAM, 'DELTA': DELTA
                      }
    # BUILD TRANS MAT _ PARALELL #
    TransProbSet[ind] = BuildTransMatrix_Para(ParamsSet[ind])
    # BUILD TRANS MAT _ LINEAR #
#     TransProbSet[ind] = BuildTransMatrix(ParamsSet[ind])
    
    # Bellman
    V_bell, A_bell = BellmanSolver(TransProbSet[ind], ParamsSet[ind])
    V_opt_set_bell[ind] = V_bell
    A_opt_set_bell[ind] = A_bell 
    RESset_bell[ind] = GetOptResultList(V_bell,A_bell, TransProbSet[ind], ParamsSet[ind])
      
    # Myopic
    V_myo, A_myo = NaiveSolver_Myopic(TransProbSet[ind], ParamsSet[ind])
    RESset_myo[ind] = GetOptResultList(V_myo,A_myo, TransProbSet[ind], ParamsSet[ind])
      
    # Zero
    V_zero, A_zero = NaiveSolver_Always(TransProbSet[ind], 0, ParamsSet[ind])
    RESset_zero[ind] = GetOptResultList(V_zero,A_zero, TransProbSet[ind], ParamsSet[ind])
    
    # One
    V_one, A_one = NaiveSolver_Always(TransProbSet[ind], 1, ParamsSet[ind])
    RESset_one[ind] = GetOptResultList(V_one,A_one, TransProbSet[ind], ParamsSet[ind])
     
#     # rndmzd
#     RANDOM_COUNT = 10
#     RE = []
#     for rcount in range(RANDOM_COUNT):
#         print "RANDOM: %d/%d running..." % (rcount+1,RANDOM_COUNT)
#         V_rnd, A_rnd = NaiveSolver_Rnd(TransProbSet[ind], ParamsSet[ind])
#         RE_rnd = GetOptResultList(V_rnd,A_rnd, TransProbSet[ind], ParamsSet[ind])
#         if rcount == 0:
#             RE = [0.0 for _ in range(len(RE_rnd))]
#         for i in range(len(RE_rnd)):
#             RE[i] = RE[i] + RE_rnd[i]
#     for i in range(len(RE)):
#         RE[i] = RE[i]*1.0/(1.0*RANDOM_COUNT)
#     RESset_rnd[ind] = RE

#
# EXTRA PENALTY TEST
PEN_list = [0.0, 50.0] # LOW AND HIGH

RESset_bell_PEN_LOW = [None for _ in range(expnum)]
RESset_bell_PEN_HIGH = [None for _ in range(expnum)]

for ind, eta_cur in enumerate(ETA_list):
    print "---- EXTRA ROUND:", ind+1,
    print "out of", expnum
    N = GetUpperboundN(LAM_C, R_COVERAGE)[0]
    
    # low pen
    Params_PEN_LOW = {'ETA_DIRECT': eta_cur, \
                      'G': G, 'Q': Q, 'N': N, \
                      'A': A, \
                      'R_COVERAGE': R_COVERAGE, \
                      'LAM_Q': LAM_Q, 'LAM_C': LAM_C, 'LAM_U': LAM_U, \
                      'TAU': TAU, 'C_TOP': C_TOP, 'BETAH':BETAH, 'VELOCITY':VELOCITY, \
                      'PENALTY': PEN_list[0], \
                      'ALPHA_LOCAL': ALPHA_LOCAL, 'ALPHA_REMOTE': ALPHA_REMOTE, \
                      'GAM': GAM, 'DELTA': DELTA
                      }

    TransProb_PEN_LOW = BuildTransMatrix_Para(Params_PEN_LOW)
    
    # Bellman
    V_bell, A_bell = BellmanSolver(TransProb_PEN_LOW, Params_PEN_LOW)
    RESset_bell_PEN_LOW[ind] = GetOptResultList(V_bell,A_bell, TransProb_PEN_LOW, Params_PEN_LOW)
    
    # high pen
    Params_PEN_HIGH = {'ETA_DIRECT': eta_cur, \
                      'G': G, 'Q': Q, 'N': N, \
                      'A': A, \
                      'R_COVERAGE': R_COVERAGE, \
                      'LAM_Q': LAM_Q, 'LAM_C': LAM_C, 'LAM_U': LAM_U, \
                      'TAU': TAU, 'C_TOP': C_TOP, 'BETAH':BETAH, 'VELOCITY':VELOCITY, \
                      'PENALTY': PEN_list[1], \
                      'ALPHA_LOCAL': ALPHA_LOCAL, 'ALPHA_REMOTE': ALPHA_REMOTE, \
                      'GAM': GAM, 'DELTA': DELTA
                      }

    TransProb_PEN_HIGH = BuildTransMatrix_Para(Params_PEN_HIGH)
    
    # Bellman
    V_bell, A_bell = BellmanSolver(TransProb_PEN_HIGH, Params_PEN_HIGH)
    RESset_bell_PEN_HIGH[ind] = GetOptResultList(V_bell,A_bell, TransProb_PEN_HIGH, Params_PEN_HIGH)

#

    
toc = timeit.default_timer()
print
print "Total time spent: ",
print toc - tic
    
print "Dumping...",
pickle.dump(expnum, open("../results/ETA_changing/expnum","w"))
pickle.dump(ParamsSet, open("../results/ETA_changing/Paramsset","w"))
pickle.dump(ETA_list, open("../results/ETA_changing/xaxis","w"))
pickle.dump(RESset_bell, open("../results/ETA_changing/bell","w"))
pickle.dump(RESset_bell_PEN_LOW, open("../results/ETA_changing/bell_pen_low","w"))
pickle.dump(RESset_bell_PEN_HIGH, open("../results/ETA_changing/bell_pen_high","w"))
pickle.dump(RESset_myo, open("../results/ETA_changing/myo","w"))
pickle.dump(RESset_rnd, open("../results/ETA_changing/rnd","w"))
pickle.dump(RESset_zero, open("../results/ETA_changing/zero","w"))
pickle.dump(RESset_one, open("../results/ETA_changing/one","w"))
pickle.dump(V_opt_set_bell, open("../results/ETA_changing/V_opt_bell","w"))
pickle.dump(A_opt_set_bell, open("../results/ETA_changing/A_opt_bell","w"))
print "Finished"