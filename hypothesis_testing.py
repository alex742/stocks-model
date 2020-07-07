#from backtesting import *
import numpy as np
from scipy import stats
import random

# * There are three types of hypothesis tests that we can run:
# *    - Run a simple hypothesis test assuming a known priori distrbution,
# *    - Run the algorithm over randomly generated random walks showing if the algorithm provides insight into the market,
# *    - Run a suite of algorithms that have the same characteristics (e.g. same trade frequency).

def priori_distr():
    b = [random.uniform(-0.999999, 1.0) for i in range(100000)] #Backtesting().dailyPL()
    #Renamting in terms of math csnts
    mu = np.abs(np.mean(b))
    sigma = np.std(b)
    N = len(b)

    t = mu/sigma * np.sqrt(N) #test_statistic
    df = 2*N - 1 #degrees of freedom
    p = 1 - stats.t.cdf(t,df=df) #p value
    print("t = " + str(t))
    print("p = " + str(2*p))

priori_distr()