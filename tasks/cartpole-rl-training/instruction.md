# CartPole RL Training

Train an agent for the `CartPole-v1` environment.

Your final deliverable must satisfy all of the following:

- Create `/app/agent.py` with an `Agent` class.
- `Agent.select_action(current_observation)` must return a valid CartPole action.
- `Agent.save(dir_path)` must write the saved policy inside the exact `dir_path` argument that is passed in.
- `Agent.load(dir_path)` must restore the saved policy from the exact `dir_path` argument that is passed in.
- The saved model directory must be smaller than `100KB`.
- The loaded agent must achieve a mean reward greater than `300` over `100` evaluation episodes.

Important details:

- The verifier will call `agent.save(Path("/app/test_trained_model"))`, so `save()` must create files under that directory.
- The verifier will call `Agent()` and then immediately call `save()` on that fresh instance, so `save()` must also work before any explicit training method is called.
- The verifier will separately call `agent.load(Path("/app/trained_model"))`, so the final training flow must also save a working policy under `/app/trained_model`.
- Do not report claimed evaluation numbers unless the implementation actually achieves them under Gymnasium `CartPole-v1`.
- A compact deterministic policy is enough. A tiny linear controller or similarly small NumPy-based policy is preferred over a heavyweight training stack.
- You do not need PyTorch. A very small deterministic controller with a few scalar weights is acceptable if it genuinely achieves the verifier threshold.
- Training is optional. A compact hand-crafted policy is acceptable if `save()` / `load()` work correctly and the loaded policy exceeds the reward threshold.

You may use Gymnasium and NumPy. Keep the final artifact compact, deterministic, and faithful to the required `save()` / `load()` contract.
