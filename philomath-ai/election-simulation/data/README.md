# Sample Polling Data

This directory contains sample polling data files for the election simulation module.

## File Format

Polling data files should be in CSV format with the following columns:

- **State**: Name of the state
- **CandidateA**: Polling percentage for Candidate A (0-100)
- **CandidateB**: Polling percentage for Candidate B (0-100)
- **ElectoralVotes**: Number of electoral votes for this state

## Example

```csv
State,CandidateA,CandidateB,ElectoralVotes
Pennsylvania,48.5,47.2,19
Michigan,49.1,46.8,15
Wisconsin,48.9,47.5,10
```

## Files Included

- **sample_polls.csv**: Sample swing state polling data for demonstration

## Using Your Own Data

To use your own polling data:

1. Create a CSV file with the required columns
2. Add your state-by-state polling data
3. Pass the filename to `parse_polling_file()` function

Example:
```python
from election_simulation import parse_polling_file

# Load your data
state_polls = parse_polling_file('data/my_polls.csv')
```

## Notes

- Percentages should be in the range 0-100 (not 0-1)
- Electoral votes must be positive integers
- State names should be unique
- Total percentages for candidates don't need to add to 100 (accounts for third parties, undecided voters)
