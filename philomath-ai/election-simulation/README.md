# Election Simulation - Forecasting Presidential Elections from Polling Data

Welcome to the **Election Simulation** module, implementing concepts from "Programming for Lovers in Python: Simulating an Election" by Phillip Compeau.

## 📚 Module Overview

This module provides a comprehensive introduction to election forecasting through Monte Carlo simulation. Learn how to:

- Parse polling data from files
- Simulate individual state elections
- Model uncertainty in polling
- Aggregate state results through the Electoral College
- Run thousands of simulations to predict outcomes
- Understand why polling simulators have limitations

Each module includes:

- **Clear explanations** of election forecasting concepts
- **Progressive implementations** from basic parsing to full simulations
- **Real-world polling data** examples
- **Statistical analysis** of prediction uncertainty
- **Discussion of limitations** and alternative approaches

## 🎯 Learning Objectives

By working through this module, you will master:

### Programming Skills
- **File parsing**: Reading and processing CSV/text data
- **Data structures**: Using dictionaries and lists for state data
- **Random sampling**: Modeling uncertainty in polls
- **Simulation**: Running Monte Carlo methods for prediction
- **Statistical analysis**: Computing win probabilities and confidence

### Election Forecasting Concepts
- **Electoral College**: Understanding winner-take-all systems
- **Polling uncertainty**: Why polls have margins of error
- **Monte Carlo simulation**: Using randomness to model outcomes
- **Aggregation**: Combining state-level results
- **Prediction markets**: Alternative to polling-based forecasts
- **Model limitations**: Why all polling simulators struggle

### Statistical Methods
- Normal distribution and random sampling
- Law of large numbers applied to elections
- Confidence intervals and margins of error
- Probability vs. certainty in predictions

## 📁 Directory Structure

```
election-simulation/
├── README.md                      # This file - module overview
├── 01_parsing_data.py             # Parse polling data from files
├── 02_single_election.py          # Simulate a single election
├── 03_multiple_elections.py       # Run multiple elections with randomness
├── 04_electoral_college.py        # Complete Electoral College simulation
├── demo_bd_2026.py                # Bangladesh 2026 election demonstration
├── test_all.py                    # Test suite for all modules
└── data/                          # Sample polling data
    ├── sample_polls.csv           # US swing state example
    ├── bd_2026_polls.csv          # Bangladesh 2026 key constituencies
    ├── bd_2026_swing_constituencies.csv  # BD close races
    ├── bd_2026_comprehensive.csv  # BD comprehensive (75 constituencies)
    └── README.md                  # Data format documentation
```

## 🚀 Quick Start

### Running Examples

Each module can be run standalone to see demonstrations:

```bash
cd election-simulation

# Parse polling data from a file
python 01_parsing_data.py

# Simulate a single election based on polls
python 02_single_election.py

# Run multiple simulations to see probability distribution
python 03_multiple_elections.py

# Complete Electoral College simulation
python 04_electoral_college.py

# Bangladesh 2026 election simulation (real-world example)
python demo_bd_2026.py
```

### Running with Bangladesh Data

Simulate Bangladesh's landmark 2026 election:

```bash
cd election-simulation

# Run comprehensive Bangladesh election simulation
python demo_bd_2026.py

# Or use individual modules with BD data
python 04_electoral_college.py  # Then modify to load BD data files
```

### Using in Your Code

```python
import importlib.util
import os

def load_election_module(filename):
    """Helper to load modules with numeric prefixes."""
    path = os.path.join('philomath-ai/election-simulation', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and use
parsing_module = load_election_module('01_parsing_data.py')
single_module = load_election_module('02_single_election.py')
multiple_module = load_election_module('03_multiple_elections.py')
ec_module = load_election_module('04_electoral_college.py')

# Parse data
state_polls = parsing_module.parse_polling_file('data/sample_polls.csv')

# Run simulation
result = ec_module.simulate_electoral_college(state_polls, num_simulations=10000)
print(f"Candidate A wins {result['candidate_a_wins']/100:.1f}% of simulations")
```

## 📖 Module Details

### 01_parsing_data.py - Reading Polling Data

Learn to parse polling data from CSV files:

- Read state-by-state polling data
- Extract candidate percentages and margins
- Handle data validation and errors
- Structure data for simulation

**Key Functions:**
- `parse_polling_file(filename)`: Read CSV polling data
- `validate_state_data(state_dict)`: Ensure data integrity
- `get_state_poll(state_polls, state_name)`: Access specific state data

### 02_single_election.py - Simulating One Election

Simulate a single election based on polling:

- Determine winners in each state
- Award electoral votes
- Calculate total electoral votes
- Determine overall winner

**Key Functions:**
- `simulate_state(poll_data)`: Determine state winner
- `simulate_election(state_polls)`: Run complete election
- `calculate_electoral_votes(state_results)`: Count electoral votes

### 03_multiple_elections.py - Monte Carlo Simulation

Run thousands of elections with polling uncertainty:

- Add random variation to polls (margin of error)
- Sample from normal distributions
- Track win frequencies
- Analyze probability of victory

**Key Functions:**
- `add_polling_noise(poll_value, margin_of_error)`: Model uncertainty
- `simulate_multiple_elections(state_polls, num_sims)`: Run many elections
- `analyze_results(simulation_results)`: Compute win probabilities

### 04_electoral_college.py - Complete Simulation

Full Electoral College simulation with all features:

- Parse polling data
- Add realistic polling uncertainty
- Simulate thousands of elections
- Report comprehensive statistics
- Visualize probability distributions

**Key Functions:**
- `simulate_electoral_college(state_polls, num_simulations)`: Main simulation
- `generate_report(results)`: Create detailed output
- `visualize_results(results)`: Plot distributions (if matplotlib available)

## 🎓 Course Reference

This module implements concepts from **"Programming for Lovers in Python: Simulating an Election"** streamed live on Feb 10, 2026 by Phillip Compeau.

### Video Timestamps (1:54:55 total)
- **00:00** - Intro screen
- **05:25** - Stream starts, course updates, Electoral College
- **15:13** - Overview of election directory
- **20:32** - Writing parsing code
- **35:43** - Highest level function
- **40:45** - Simulating multiple elections
- **53:32** - Simulating a single election
- **1:01:44** - Adding randomness to polling data
- **1:10:09** - Ensuring parsing code works
- **1:15:44** - (Incorrectly) simulating an election
- **1:22:22** - Fixing a bug
- **1:25:50** - (Correctly) simulating an election
- **1:30:05** - Why is our simulation so confident?
- **1:38:58** - Why all polling simulators stink
- **1:44:25** - Better idea: make this into a prediction market
- **1:50:19** - Kalshi is not gambling
- **1:54:55** - Course conclusion

### Related Course Materials
- Course: [Programming for Lovers in Python](https://programmingforlovers.com)
- Chapter 2: "Forecasting a Presidential Election from Polling Data"
- Code along: [Simulating Elections](https://programmingforlovers.com/chapter-2/simulating-elections/)
- Practice problems: [Cogniterra exercises](https://cogniterra.org/course/63/promo)

## 🌍 Real-World Applications

Election forecasting and Monte Carlo simulation are used in:

### Politics and Elections
- **FiveThirtyEight**: Election forecasting models
- **The Economist**: Presidential prediction models
- **Decision Desk HQ**: Real-time election projections
- **Campaign strategy**: Resource allocation and targeting
- **Bangladesh 2026 Example**: BNP's landslide victory in parliamentary elections

### Bangladesh 2026 Election Case Study

This module includes real data from Bangladesh's landmark 2026 general election:

**Historical Context:**
- First election after 2024 political upheaval that ousted PM Sheikh Hasina
- BNP (Bangladesh Nationalist Party) won 209-213 seats out of 299
- Jamaat-e-Islami secured 68-77 seats as main opposition
- 127 million registered voters, high turnout
- Held alongside constitutional reform referendum

**Why This Example Matters:**
- Demonstrates parliamentary vs. electoral college systems
- Shows single-member constituency dynamics
- Real-world validation of forecasting methods
- Illustrates impact of systematic shifts in voter behavior

**Key Differences from US System:**
- 300 constituencies with equal representation (1 seat each)
- Need 151 seats for majority (vs. 270 electoral votes in US)
- All constituencies use winner-take-all
- Prime Minister from majority party (vs. direct president election)

### Beyond Elections
- **Financial modeling**: Stock price predictions, risk analysis
- **Weather forecasting**: Ensemble prediction models
- **Sports analytics**: Game outcome probabilities
- **Medical research**: Clinical trial simulations
- **Engineering**: Reliability and failure analysis

## 🤔 Key Insights

### Why Polling Simulators Have Limitations

As discussed in the course (timestamp 1:38:58):

1. **Correlated errors**: Polls often all wrong in same direction
2. **Systematic bias**: Polls may consistently miss certain voters
3. **Turnout modeling**: Uncertainty about who will actually vote
4. **Late deciders**: Voters changing minds near election day
5. **House effects**: Different polling firms produce different results

### Alternative: Prediction Markets

Prediction markets like Kalshi (discussed at 1:44:25) offer advantages:

- **Real money stakes**: People bet actual money on outcomes
- **Information aggregation**: Markets combine many signals
- **Self-correcting**: Arbitrage eliminates obvious mistakes
- **No modeling assumptions**: Market sets probabilities
- **Legal in US**: Not gambling, but derivatives trading

## 📚 Additional Resources

### Election Forecasting
- [FiveThirtyEight Methodology](https://fivethirtyeight.com/methodology/)
- [The Economist Model](https://projects.economist.com/us-2020-forecast/president/how-this-works)
- [Nate Silver's The Signal and the Noise](https://www.penguinrandomhouse.com/books/305826/)

### Prediction Markets
- [Kalshi](https://kalshi.com/) - CFTC-regulated prediction market
- [PredictIt](https://www.predictit.org/) - Research-focused market
- [The Wisdom of Crowds](https://en.wikipedia.org/wiki/The_Wisdom_of_Crowds) - Book by James Surowiecki

### Monte Carlo Methods
- [Monte Carlo Method (Wikipedia)](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Seeing Theory - Probability](https://seeing-theory.brown.edu/basic-probability/)
- [Probabilistic Programming & Bayesian Methods](http://camdavidsonpilon.github.io/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/)

### Electoral College
- [National Archives - Electoral College](https://www.archives.gov/electoral-college)
- [FairVote - Electoral College Reform](https://www.fairvote.org/electoral_college)
- [270toWin - Interactive Electoral Maps](https://www.270towin.com/)

## 🧪 Testing

Run the test suite to verify all functions work correctly:

```bash
python test_all.py
```

The tests cover:
- File parsing and validation
- Single election simulation
- Multiple election simulation
- Electoral College calculation
- Random number generation and seeding
- Edge cases and error handling

## 🤝 Contributing

This is an educational project. Contributions welcome:

- Add more realistic polling data
- Implement visualization of results
- Add swing state analysis
- Model correlated polling errors
- Implement prediction market comparison
- Add historical election validation

## 📄 License

See the main repository [LICENSE](../../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** - Course creator and Professor at Carnegie Mellon University
- **Programming for Lovers** - Open online course for learning programming through real questions
- **FiveThirtyEight & Nate Silver** - Pioneering election forecasting
- **The forecasting community** - Developing robust prediction methods
- **Kalshi** - Making prediction markets accessible and legal

## 💡 Learning Path

### Recommended Progression

1. **Start with basics**: 01_parsing_data.py
   - Understand polling data format
   - Learn file parsing in Python
   - Practice data validation

2. **Simple simulation**: 02_single_election.py
   - Simulate one election
   - Calculate Electoral College
   - Determine winners

3. **Add uncertainty**: 03_multiple_elections.py
   - Model polling errors
   - Run Monte Carlo simulations
   - Compute win probabilities

4. **Complete system**: 04_electoral_college.py
   - Integrate all components
   - Generate forecasts
   - Understand limitations

### Prerequisites

- Basic Python (functions, loops, dictionaries)
- Understanding of random numbers (see monte-carlo module)
- Basic probability concepts
- Familiarity with CSV files

### Next Steps

After completing this module:
- Study actual election forecasting models (FiveThirtyEight)
- Learn about Bayesian statistics for better modeling
- Explore prediction markets as an alternative
- Apply Monte Carlo methods to other domains

---

**Ready to forecast elections and understand the power and limitations of prediction? Let's simulate! 🗳️📊💻**
