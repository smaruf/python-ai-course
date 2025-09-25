import pymc3 as pm
import numpy as np

# Simulated returns data
data = np.random.normal(0, 1, size=100)

with pm.Model() as model:
    mu = pm.Normal('mu', mu=0, sigma=1)
    sigma = pm.HalfNormal('sigma', sigma=1)
    returns = pm.Normal('returns', mu=mu, sigma=sigma, observed=data)
    trace = pm.sample(1000)

# Posterior estimate
print('Mean return estimate:', np.mean(trace['mu']))
