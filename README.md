<h1 align="center">AuthBench: Do Agents Know What They Should Be Allowed to Access?</h1>

<div align="center">

[![Evolvent AI][evolvent-image]][evolvent-url]
[![Blog][blog-image]][blog-url]
[![YouTube][youtube-image]][youtube-url]
[![Discord][discord-image]][discord-url]
[![X][x-image]][x-url]
[![LinkedIn][linkedin-image]][linkedin-url]
[![WeChat][wechat-image]][wechat-url]
[![Hugging Face][huggingface-image]][huggingface-url]
[![Star][star-image]][star-url]
[![License][license-image]][license-url]

</div>

<p align="center">
  A benchmark for evaluating whether coding agents can infer task-level permission boundaries that are both executable and safe.
</p>

AuthBench studies a simple but increasingly important question: as coding agents become stronger at using terminals and operating real environments, do they also know what they should be allowed to access?

We build AuthBench to evaluate task-level permission generation for terminal tasks. The benchmark collects and adapts `120` tasks from sources including `Terminal-Bench`, `SWE-Bench`, and `OpenThoughts-TBLite`, covering both ordinary terminal workflows and tasks with dangerous shortcuts or sensitive access paths. Each task is evaluated from two complementary perspectives: static permission quality and real constrained execution outcomes.

## Coming Soon

We are cleaning up the repository for the first public release. The benchmark code, task definitions, annotations, and evaluation pipeline will be open-sourced before **April 20, 2026**.

The initial release will include:

- benchmark tasks and task-level permission specifications
- permission-generation and constrained-execution pipelines
- evaluation code and metrics
- documentation for reproducing the main experiments

<p align="center">
  <img src="https://oss.evolvent.co/articles/1776250280728_authbench-agent-scope-and-permission-awareness.png" alt="Evolution of coding agents from chat and completion tools to terminal and long-running workflow agents, alongside the question of whether they can infer the right permission boundary." width="100%" />
</p>

<p align="center">
  <em>As coding agents take on broader scopes, permission-boundary awareness becomes a standalone capability.</em>
</p>

<p align="center">
  <img src="https://oss.evolvent.co/articles/1776250437746_authbench-task-evaluation-pipeline.png" alt="AuthBench task abstraction and evaluation pipeline, showing task definition, generated permission policy, and the split between static evaluation and constrained execution." width="100%" />
</p>

<p align="center">
  <em>AuthBench evaluates permission generation with both static comparison and real constrained execution.</em>
</p>

[evolvent-image]: https://img.shields.io/badge/Evolvent_AI-evolvent.co-0f141b
[evolvent-url]: https://evolvent.co
[blog-image]: https://img.shields.io/badge/Blog-Evolvent_Research-2563eb
[blog-url]: https://evolvent.co/en/research
[youtube-image]: https://img.shields.io/badge/YouTube-Evolvent_AI-FF0000?logo=youtube&logoColor=white
[youtube-url]: https://www.youtube.com/watch?v=uHIKgki3B8Q
[discord-image]: https://img.shields.io/badge/Discord-Join%20Us-5865F2?logo=discord&logoColor=white
[discord-url]: https://discord.gg/RCFuy6wttC
[x-image]: https://img.shields.io/twitter/follow/Evolvent_AI?style=social
[x-url]: https://x.com/Evolvent_AI
[linkedin-image]: https://img.shields.io/badge/LinkedIn-Evolvent_AI-0A66C2?logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/company/evolvent-ai
[wechat-image]: https://img.shields.io/badge/WeChat-Evolvent_AI-07C160?logo=wechat&logoColor=white
[wechat-url]: https://evolvent.co
[huggingface-image]: https://img.shields.io/badge/Hugging_Face-EvolventAI-FFD21E?logo=huggingface&logoColor=black
[huggingface-url]: https://huggingface.co/EvolventAI
[star-image]: https://img.shields.io/github/stars/evolvent-ai/Authbench?label=stars&logo=github&color=brightgreen
[star-url]: https://github.com/evolvent-ai/Authbench/stargazers
[license-image]: https://img.shields.io/badge/License-TBD-lightgrey
[license-url]: https://github.com/evolvent-ai/Authbench
