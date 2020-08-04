#from backtesting import *
import numpy as np
from scipy import stats,optimize
import random


# * There are three types of hypothesis tests that we can run:
# *    - Run a simple hypothesis test assuming a known priori distrbution,
# *    - Run the algorithm over randomly generated random walks showing if the algorithm provides insight into the market,
# *    - Run a suite of algorithms that have the same characteristics (e.g. same trade frequency).

def priori_distr():
    b = Backtesting().dailyProfit()
    #Renaming in terms of math constants
    mu = np.abs(np.mean(b))
    sigma = np.std(b)
    N = len(b)

    t = mu/sigma * np.sqrt(N) #test_statistic
    df = N - 1 #degrees of freedom
    p = 1 - stats.t.cdf(t,df=df) #p value
    print("t = " + str(t))
    print("p = " + str(2*p))
    if 2*p < 0.01:
        print("The result is significant.")
    else:
        print("The result is not significant.")

#priori_distr()

#Using scipy's optimise to iteratively generate a pearson type III distribution with the required moments
def random_by_sk(mean, var, skew, kurt, size):
    def dist_error(a):
        m, v, s, k = stats.pearson3.stats(a, moments="mvsk", loc = mean, scale = np.sqrt(var))
        return (m - mean) ** 2 + (v - var) ** 2 + (s - skew) ** 2 + (k - kurt) ** 2  # penalty equally weighted for all moments
    a = optimize.minimize(dist_error, 1).x
    n = stats.pearson3.rvs(a, size=size, loc = mean, scale = np.sqrt(var))
    return n




def monte_carlo(no_tests=10000):
    """Using pearson type III we generate data with the same mean, skew, kurtosis, etc. and run our algorithm over these artificial markets and see if performance is a product of the underlying data structure. 
    """
    # ! Currently using the pearson III distribution, in Algorithmic trading by Ernie Chan he uses generalised pearson but doesn't mention the type.
    # TODO look into and justify the distribution used
    b = Backtesting()
    profit = b.runBacktest(data).totalProfit()
    b_data = b.maketData()
    #Generate a number of tests
    gen_data = [random_by_sk(np.mean(b_data), np.var(b_data), stats.skew(b_data), stats.kurtosis(b_data), len(b_data)) for i in range(no_tests)]
    success_count = 0
    for data in gen_data:
        if b.runBacktest(data).totalProfit() < profit:
            success_count += 1
    return (success_count / no_tests)