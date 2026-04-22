你就**别跟 Codex 聊抽象想法**，直接给它一份“任务书”。
官方给 Codex 的建议也是：**把指令放前面、范围写死、给清楚的成功标准和验证命令**；长任务最好有一个 plan/runbook，让它按计划执行、控制改动范围、每个阶段跑验证。([OpenAI开发者][1])

你这个场景，最适合直接贴下面这段。

```text
任务：在当前仓库中加入 RT-DETR 基线，并用 YOLO 作为对比，在 NEU-DET 上做严格、可复现的实验。

目标
1. 新增 RT-DETR 训练与评估流程，适配 NEU-DET。
2. 保留 YOLO 基线，和 RT-DETR 使用同一套数据划分与评估协议。
3. 采用 4-fold stratified cross-validation。
4. 输出每折 AP50、mAP50-95、per-class AP。
5. 生成用于统计检验的结果文件，便于后续做 ANOVA 和 Tukey HSD。
6. 不做无关重构，不改动与本任务无关的代码。

仓库上下文
- 数据集：NEU-DET
- 任务：表面缺陷目标检测
- 模型：RT-DETR 作为主模型，YOLO 作为对比基线
- 重点：不是单次最高分，而是严格对比和可复现评估

你先做什么
1. 先阅读仓库结构，找出现有数据加载、训练、评估、配置管理入口。
2. 先给我一个简短执行计划，列出将修改/新增哪些文件。
3. 计划确认后再开始实现。

实现要求
1. 新增 RT-DETR 的配置与训练脚本，尽量复用现有训练框架。
2. 新增 4-fold stratified split 脚本，保证类别分布均衡。
3. 训练和评估都支持 fold_id 参数。
4. 结果保存为统一格式，例如 CSV/JSON：
   - model_name
   - fold_id
   - seed
   - AP50
   - mAP50_95
   - per_class_AP
5. 新增一个统计分析脚本，读取所有 fold 结果，导出可用于 ANOVA/Tukey 的表格。
6. 新增 README 或 docs，说明如何运行 RT-DETR、YOLO、4-fold CV 和统计分析。

约束
1. 不要大规模重构。
2. 不要改已有 YOLO 结果定义。
3. 不要偷偷换数据划分协议。
4. 所有新增依赖都要写清楚。
5. 改动尽量小而集中。

验证要求
1. 至少跑通一个 fold 的 smoke test。
2. 给出完整命令：
   - 数据划分命令
   - RT-DETR 训练命令
   - YOLO 训练命令
   - 评估命令
   - 统计分析命令
3. 最后汇报：
   - 改了哪些文件
   - 每个文件作用
   - 还缺什么才能开始正式全量实验

输出格式
1. 先输出计划。
2. 然后实施。
3. 最后给我：
   - 改动摘要
   - 运行命令
   - 风险点/待确认事项
```

你还可以再加一句，效果通常更好：

```text
注意：请把“同一数据划分协议下的公平比较”放在首位，不要为了追单次最好分数改动评估口径。
```

如果你想让 Codex **更稳**，再补 4 个具体信息。官方也建议这类信息尽量前置，不要让模型自己猜。([OpenAI Help Center][2])

1. **仓库路径/入口文件**
   例如：`train.py`、`configs/`、`datasets/`、`scripts/`

2. **你已经有的 YOLO 代码在哪**
   例如：`models/yolo/`、`tools/train_yolo.py`

3. **你想保存结果的格式**
   例如：`runs/neu_det/{model}/fold_{k}/metrics.json`

4. **你只允许它先跑 smoke test，不要全量训练**
   这样它不会乱烧资源。

你也可以更短一点，直接一句话版：

```text
请在这个仓库里实现 NEU-DET 上的 RT-DETR vs YOLO 公平对比实验：统一使用 4-fold stratified CV，输出 AP50/mAP50-95/per-class AP 和统计分析输入表；先给计划，再做最小改动实现，最后给出可复现命令。
```

如果你这个任务会比较长，官方更推荐把“计划”和“执行规则”写成 repo 里的文档文件，让 Codex按文档执行，比如 `PLAN.md` 和 `IMPLEMENT.md`，其中 plan 是目标和里程碑，implement 是“按计划执行、控制 diff、每步跑验证、持续更新文档”的 runbook。([OpenAI开发者][3])

你现在最需要的，其实不是“怎么跟 Codex 说”，而是**把你要它做的边界写死**。
不然它很容易擅自：

* 改评估协议
* 换默认增强
* 重构一堆无关代码
* 最后给你一个“看起来能跑”的东西，但不适合写论文

你要的话，我可以直接把上面这段再改成**更像你当前项目目录结构**的版本。

[1]: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide?utm_source=chatgpt.com "Codex Prompting Guide"
[2]: https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api?utm_source=chatgpt.com "Best practices for prompt engineering with the OpenAI API"
[3]: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex?utm_source=chatgpt.com "Run long horizon tasks with Codex"
