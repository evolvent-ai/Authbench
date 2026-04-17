# AIMO Problem 1: Airline Departure Problem

Three airline companies operate flights from Dodola island:

- The first company departs every 100 days
- The second company departs every 120 days
- The third company departs every 150 days

Find the greatest positive integer `d` such that there will always be `d` consecutive days without a flight, regardless of the departure offsets chosen by the three airlines.

You may solve this by exhaustive search over one full 600-day cycle, because `lcm(100, 120, 150) = 600`.

Use this exact interpretation:

- Choose offsets `a`, `b`, and `c` with `0 <= a < 100`, `0 <= b < 120`, and `0 <= c < 150`
- In one 600-day cycle, the three airlines depart on days congruent to `a mod 100`, `b mod 120`, and `c mod 150`
- For one fixed offset triple, compute the largest cyclic gap between consecutive departure days
- The number of quiet days between departure day `x` and the next departure day `y` is `y - x - 1`
- Include the wrap-around gap from the last departure in the cycle back to the first departure in the next cycle
- The required answer is the minimum, over all offset triples, of that largest cyclic gap

Your task:

1. Create `/app/airline_analysis.py`
2. Run it so that it writes the final answer, as a single number, to `/app/results.txt`
