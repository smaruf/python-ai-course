# Monte Carlo Simulation - Random Numbers and Craps

Welcome to the **Monte Carlo Simulation** module, implementing concepts from "Programming for Lovers in Python: Monte Carlo Simulation and Craps" by Phillip Compeau.

## 📚 Module Overview

This module provides a comprehensive introduction to Monte Carlo simulation methods through hands-on Python implementations. Each module includes:

- **Clear explanations** of randomness and probability concepts
- **Progressive implementations** from basic random numbers to complex simulations
- **Real-world applications** using the game of Craps
- **Visual demonstrations** of the Law of Large Numbers
- **Statistical analysis** of house edge and probability

## 🎯 Learning Objectives

By working through this module, you will master:

### Programming Skills
- **Random number generation**: Using Python's random module effectively
- **Seeding**: Understanding and controlling randomness for reproducibility
- **Simulation**: Building models to estimate probabilities
- **Statistical analysis**: Computing averages, frequencies, and convergence
- **Data visualization**: Plotting convergence and probability distributions

### Probability Concepts
- **Law of Large Numbers**: How simulations converge to theoretical values
- **Expected value**: Computing long-term averages
- **House edge**: Understanding casino mathematics
- **Simulation accuracy**: Balancing computation time vs. precision
- **Random sampling**: Generating random events programmatically

### Monte Carlo Methods
- Using randomness to solve deterministic problems
- Estimating probabilities through repeated trials
- Understanding simulation convergence
- Validating simulations against known probabilities
- Scaling simulations for better accuracy

## 📁 Directory Structure

```
monte-carlo/
├── README.md                      # This file - module overview
├── 01_random_numbers.py          # Random number generation and seeding
├── 02_dice_simulation.py         # Dice rolling and law of large numbers
├── 03_craps_simulation.py        # Craps game simulation and house edge
└── test_all.py                   # Test suite for all modules
```

## 🚀 Quick Start

### Running Examples

Each module can be run standalone to see demonstrations:

```bash
cd monte-carlo

# Generate random numbers and explore seeding
python 01_random_numbers.py

# Simulate dice rolls and observe the law of large numbers
python 02_dice_simulation.py

# Simulate craps games and calculate house edge
python 03_craps_simulation.py
```

### Using in Your Code

```python
import importlib.util
import os

def load_monte_carlo_module(filename):
    """Helper to load modules with numeric prefixes."""
    path = os.path.join('philomath-ai/monte-carlo', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and use
random_module = load_monte_carlo_module('01_random_numbers.py')
dice_module = load_monte_carlo_module('02_dice_simulation.py')
craps_module = load_monte_carlo_module('03_craps_simulation.py')

# Roll a die
result = dice_module.roll_die()

# Play a game of craps
outcome = craps_module.play_craps_once()
```

## 📖 Course Reference

This module implements concepts from **"Programming for Lovers in Python: Monte Carlo Simulation and Craps"** by Phillip Compeau, covering:

- **Random Numbers**: Generating random integers and understanding seeding
- **Dice Simulation**: Rolling dice and observing statistical properties
- **Law of Large Numbers**: How averages converge with more trials
- **Craps Rules**: Understanding the classic casino dice game
- **House Edge**: Computing the casino's advantage through simulation
- **Simulation Design**: Generalizing simulations for different scenarios

## 🎲 Craps Rules

Craps is a dice game with the following rules:

1. **Come-out roll**: Roll two dice to start
   - Rolling 7 or 11 is an instant **win**
   - Rolling 2, 3, or 12 is an instant **loss** (craps)
   - Any other number (4, 5, 6, 8, 9, 10) becomes the **point**

2. **Point phase** (if a point was established):
   - Keep rolling until you roll the point again or roll a 7
   - Rolling the point is a **win**
   - Rolling a 7 is a **loss** (seven-out)

The house edge in craps is approximately 1.4%, making it one of the better bets in a casino.

## 🔬 Real-World Applications

Monte Carlo methods are used in:

- **Finance**: Option pricing, risk analysis, portfolio optimization
- **Physics**: Particle simulations, quantum mechanics, thermodynamics
- **Engineering**: Reliability analysis, stress testing, design optimization
- **Medicine**: Drug discovery, epidemiology modeling, clinical trial design
- **Computer Graphics**: Ray tracing, global illumination, image synthesis
- **Operations Research**: Queue simulation, supply chain optimization
- **Climate Science**: Weather prediction, climate modeling
- **Machine Learning**: Bayesian inference, reinforcement learning

## 📚 Additional Resources

### Probability & Statistics
- [Khan Academy - Probability](https://www.khanacademy.org/math/statistics-probability)
- [Seeing Theory - Visual Statistics](https://seeing-theory.brown.edu/)
- [Introduction to Probability (Blitzstein & Hwang)](https://projects.iq.harvard.edu/stat110)

### Monte Carlo Methods
- [Monte Carlo Theory, Methods and Examples (Owen)](https://artowen.su.domains/mc/)
- [Handbook of Monte Carlo Methods (Kroese et al.)](https://people.smp.uq.edu.au/DirkKroese/montecarlohandbook/)

### Python & Simulation
- [Python random module documentation](https://docs.python.org/3/library/random.html)
- [NumPy random generation](https://numpy.org/doc/stable/reference/random/index.html)
- [Matplotlib plotting tutorials](https://matplotlib.org/stable/tutorials/)

### Online Courses
- Coursera: Monte Carlo Methods in Finance (Columbia)
- EdX: Computational Probability and Inference (MIT)

## 💡 Learning Path

**Recommended progression**:

1. **Start with randomness**: 01_random_numbers.py - Understand RNG and seeding
2. **Simulate dice**: 02_dice_simulation.py - Roll dice and see the law of large numbers
3. **Play craps**: 03_craps_simulation.py - Simulate the full game and compute house edge

Each module builds on previous concepts, so following this order is recommended for maximum learning benefit.

## 🤝 Contributing

This is an educational project. Contributions welcome:

- Add new simulations (roulette, blackjack, lottery, etc.)
- Improve visualizations
- Add more probability distributions
- Enhance documentation
- Create Jupyter notebooks
- Add theoretical probability calculations

## 📄 License

See the main repository [LICENSE](../../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** - Course creator and computer science educator at Carnegie Mellon University
- **Programming for Lovers** - Open online course for learning programming through scientific applications
- **The statistics community** - For developing Monte Carlo methods

## 🎓 Course Materials

This module accompanies **Chapter 2** of Programming for Lovers on "Forecasting a Presidential Election from Polling Data":

- [Random Numbers Code-Along](https://programmingforlovers.com/random-numbers)
- [Simulating Craps Code-Along](https://programmingforlovers.com/simulating-craps)
- [Course Mailing List](http://eepurl.com/iC9DSg)
- [Free Course Materials](https://programmingforlovers.com)
- [Practice Problems](https://cogniterra.org/course/63/promo)

---

**Ready to explore the fascinating world of randomness and simulation? Let's roll the dice! 🎲**
