# 微课交互、学习路径与参考资料审查

日期：2026-10-22。此文件记录范围与证据，不把自动检查通过等同于全部教学内容都已证明正确。

## 审查覆盖

- 对照当前 `lessons.json` 与 `course.json` 的全部 72 个 ID、实际顺序、章节、任务目标、学习路径提示和资源分类。
- 为全部 72 课逐条声明目标与交互归属，见 `curriculum/lab-alignment.json`。其中 12 课有独立概念实验，另外 60 课明确为 `widgetId: null`；这些课仍有例题、预测题和代码练习。
- 检查 `dist/app.js` 与可重建 UI 片段的真实调用路径，避免旧 `visual` 类型规则重新接入。
- 此次跨切面审查不代替 Python/Torch 两条线各自对 36 课讲解、示例、测验和代码的逐课审查，也不声称已建立完整技能依赖图。

## 用户报告的根因

报告中的“第 14 节”确实是 `p6`，主题为 `zip` 配对与 `accuracy`。旧实现因为 `visual: list` 直接给它展示通用列表索引；`p5` 是字典记录的严格阈值计数，却因为 `visual: values` 展示变量加 5。

旧概念实验仅对 `p1..p6`、`t1..t6` 显示。新扩展的 60 课虽然同样带有 `visual` 字段，实际已被 `conceptWidget` 的 ID 条件排除，因此不能把它们报告为“都显示了错误动画”。

旧 12 课中，`p3/p4/p5/p6/t2/t4/t5/t6` 的通用实验明显错位或只覆盖部分概念；`p1/p2/t1/t3` 至少主题大体相关。旧 `widget()` 的最后一个分支还把任何未知类型当作梯度图。未调用的 `renderContentBase` 与通用事件绑定同样保留了复发入口。

新的中央注册表按精确 lesson ID 查找，不根据 `visual` 或章节猜测。不存在注册项时返回空串；在 quiz/mission 页找不到实验容器时绑定安全退出。

浏览器集成还发现另一个独立问题：Torch 实验容器曾带 `data-lesson`，被旧的全局导航监听器捕获，点击实验按钮后又导航重绘，实验状态回到初值。修复将导航选择器限制为 `button.lesson-nav[data-lesson]`，实验容器不再使用该导航属性；对应约束已加入自动回归。

| lesson ID | 实际课程序号 | 本课实验目标 | 声明的 widget ID |
| --- | ---: | --- | --- |
| p1 | 1 | 逐行赋值、加 5 与标准输出 | lab-p1 |
| p2 | 7 | 列表正负索引及越界 | lab-p2 |
| p3 | 4 | for 循环逐项加 5、逐行输出 | lab-p3 |
| p4 | 13 | mean 返回值，区分 return 与 print | lab-p4 |
| p5 | 19 | 字典 loss 严格小于 threshold，等于不计 | lab-p5 |
| p6 | 14 | zip 配对、正确数、accuracy，双空返回 0 | lab-p6 |
| t1 | 37 | dim、逐行均值与输出形状 | torch-row-means |
| t2 | 43 | keepdim、逐行中心化与广播 | torch-center-rows |
| t3 | 49 | 区分 x² 与 x²+3x 的函数值和导数 | torch-autograd-functions |
| t4 | 55 | Linear(3,2) 的形状和参数数 | torch-linear-shapes |
| t5 | 61 | 清梯度、反向传播、一次 SGD 更新 | torch-sgd-step |
| t6 | 67 | 零初始化、100 步拟合 y=2x+1 | torch-affine-training |

Torch 概念实验使用明确展示的 JavaScript 数值公式，帮助观察形状、梯度和更新过程；它们不是在线 PyTorch 运行器。实际 PyTorch 代码仍由本机运行环境执行。

## 学习路径发现与修复入口

1. `py05` 位于第 8 节，已经要求定义函数，但第一个完整函数专题 `p4` 在第 13 节。旧 `py05` 主例只演示切片，缺少 `def`、形参与 `return` 的最小解释。修复采用本节函数接口先导，不调整用户已使用的 ID 与顺序。
2. `pt08` 位于第 46 节，已经要求保留计算图的零与可反向传播行为，但完整自动微分专题 `t3` 在第 49 节。修复采用本节最小计算图先导，说明与输入相连的零和独立常量的区别。
3. 其余默认 `prerequisites` 基本是上一章标题：可作为学习路线提示，不能称为逐项技能先修证明。UI 应使用“学习路径提示”。

`curriculum/prerequisite_fixes.py` 应在默认逐课元数据生成后、输出 JSON 前执行。两条线的教学修订负责先导正文，该文件负责对应提示和官方参考入口。

旧“逐步写出来”在原 12 课使用相同开头，但后面接了本课的 C++/Python 对照；这是讲解过于泛化的问题，并不等同于每课正文都错题。此次没有据此把全部 72 课大范围重写。

## 参考资料的诚实边界

CS50P、Helsinki MOOC 和 ARENA 原链接确实是官方课程目录；它们不是每一道原创题的对应章节，更不是官方原题来源。现将这些链接明确标记为“课程目录（延伸）”。官方 Python/PyTorch 教程全文链接仍可作章节参考，但不应冒充某个细节的直接证据。

12 个概念实验与 `py05/pt08` 两个先导新增了精确官方小节。共 13 个不同 URL 的 fragment 已通过 HTTP 获取 HTML、解析 `id` 属性逐一确认存在，并结合官方正文核对主题。记录见 `curriculum/resource-anchor-audit.json`；这是有日期的检查，不保证网站永久不改链接。

例如：

- `p6`：[Python zip](https://docs.python.org/3/library/functions.html#zip)。
- `p5`：[Python 字典](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)。
- `py05/p4`：[定义函数](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)。
- `t2`：[PyTorch 2.10 广播规则](https://docs.pytorch.org/docs/2.10/notes/broadcasting.html#general-semantics)。
- `pt08`：[张量、函数与计算图](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html#tensors-functions-and-computational-graph)。

其余 58 课的资源记录只声明章节参考分类；没有声称逐条核验每个教学命题、每个算法的原始来源或每个参考链接中全部内容。

## 自动回归与发布边界

`node verify_lab_alignment.mjs` 检查全部 72 个声明与真实 renderer，12 个唯一注册项、60 个有意留空项、原型名称等未知 ID、独立 DOM 锚点、章节顺序、参考分类、先导提示，以及 app/UI 片段中没有旧通用 render/bind 入口。计算与事件行为由 `verify_python_labs.mjs`、`verify_torch_labs.mjs` 另行验证。浏览器视觉和真实点击仍需独立 QA。

本次独立复跑：Python 六个实验通过 476 个实际 Python 对照案例及事件回调检查；Torch 六个实验通过 520 项数值比较与 158 个真实 PyTorch 对照案例。JS 数值演示与 float32 PyTorch 允许合理浮点误差，不把小数逐位相同作为要求。`prerequisite_fixes.py` 已接线并重建最终 JSON，alignment 检查实际通过，独立复核也再次通过。浏览器已逐个打开全部 12 个实验，实际点击验证 p6 配对/全对/双空、t5 梯度清空对照及 t6 训练至 100 步。

当前 Pages 准备脚本只复制 `dist` 顶层浏览器文件，不复制 Worker 目录、身份数据或运行记录。`.runtime`、`.env*`、`dist/server`、`dist/.openai` 已忽略；此范围的当前跟踪文件检查未见真实账号 token、学习者历史快照或本地凭证。这不是对所有 Git 历史或外部账号配置的穷尽审计。
