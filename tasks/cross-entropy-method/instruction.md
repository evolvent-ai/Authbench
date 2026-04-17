# Cross-Entropy Method

Implement the three missing methods in `/app/cross_entropy_method/cross_entropy.py` so the verifier passes.

You must complete:

- `PointEnv.step(action)`
- `PointEnv.evaluate_plans_memoized(plans)`
- `CrossEntropyMethod.optimize(num_samples, num_elites, iterations)`

Task constraints:

- The agent starts at `(0, 0)` inside a square environment with valid coordinates in `[-length/2, length/2]`.
- `PointEnv.action_map` defines the nine discrete displacements.
- Reward is `1` when the Euclidean distance to the goal is less than or equal to `goal_radius`, otherwise `0`.
- Positions must stay clipped to the environment boundary.
- `evaluate_plans_memoized()` must preserve correctness while providing a measurable speedup on heavily overlapping plans.
- `optimize()` must sample each timestep independently from the current per-step probability table and update `self.probs` from the elite trajectories.

The verifier imports the package directly from `/app`, so keep the package layout intact.
