# 部署范围与在线 PyTorch 执行草案

核对日期：2026-10-22。本文是架构和实施草案；尚未建立公网原生执行 API、构建执行镜像或验证云端隔离环境。

## 当前版本实际能做什么

`dist/` 是静态前端。纯 Python 练习由浏览器中的 Pyodide 执行；原生 PyTorch 练习由本机 `server.py` → `runner.py` → `dist/grade.py` 执行。本机服务器目前只监听 `127.0.0.1:8766`。静态网站发布不会自动把这个本机 Python 进程部署到远端。

GitHub Pages 可以发布 HTML/CSS/JavaScript 与课程 JSON，并让 JavaScript 在访问者浏览器中运行；它不提供本项目需要的 Python/PyTorch 服务进程。若以后选择 GitHub Pages，原生执行仍需另外的计算服务。[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

## 三项决策建议

1. **先保留静态网站与个人本机运行。** 个人练习无需新增云资源，真实 PyTorch 继续在本人电脑运行。不能通过改监听地址、CORS 或端口转发，把现有服务直接变成公开多人判题 API。
2. **要让同学免安装在线运行，增加受控执行服务。** 前端保持静态；HTTPS 网关做登录、限流与任务归属；队列将每次提交交给独立、用后销毁的 CPU PyTorch 沙箱。公网不可信代码优先使用 gVisor/runsc 或微虚拟机作为执行边界，并对实际 PyTorch 算子和 profiler 兼容性做验证。课程规模较小时可以从一台专用 Linux 主机、少量并发开始，无需先上 Kubernetes。[gVisor 架构](https://gvisor.dev/docs/)
3. **浏览器 WebGPU 可另做已导出模型的演示，不能据此承诺全部练习兼容。** PyTorch 官方 ExecuTorch 已有实验性 WebGPU 浏览器路径，但其文档工作流是先用 Python 导出模型图再运行。由此不能推断任意学生 Python 源码、eager autograd、优化器、文件读写和 checkpoint 题都能直接在浏览器执行；完整课程仍应以经过验证的原生 CPU 环境为准。[ExecuTorch WebGPU 官方文档](https://docs.pytorch.org/executorch/stable/backends/webgpu/webgpu-overview.html)

## 为什么现有本机 API 不能直接公开

以下结论来自当前代码的只读审核，没有运行攻击性测试。

| 当前机制 | 实际作用及公开后的缺口 |
| --- | --- |
| `exec(compile(...))` 执行学生代码 | 代码拥有服务账户的普通 Python 权限，能读取该账户可读文件、发起网络请求和创建子进程。 |
| `python -I`、临时工作目录、精简环境变量 | 改善导入与文件组织，不会建立文件、网络、内核权限的隔离边界。 |
| 25 秒 `subprocess.run` 超时 | 限制直接子进程的等待时间；不能据此认为所有派生进程、内存和磁盘写入都受控。 |
| `StringIO` 后截取输出、`capture_output=True` | 截取发生在捕获之后；持续打印仍可能先耗尽内存，公开服务需要流式硬限额。 |
| `Origin` 白名单 | 没有登录、每人配额或任务归属；非浏览器请求可不带 Origin。CORS 本身不是用户认证。 |
| 教学用 AST 禁用调用 | 用于要求手写指定算法，不是安全沙箱。不能把它当作阻止任意代码执行的措施。 |

此外，当前测试与参考解属于教学资源，前端已有可读内容；当前判题反馈不能宣称具有防作弊考试系统的可信性。

## 最小执行架构

```text
访问者浏览器：静态课件、编辑器、个人进度
        │ HTTPS，经过认证的提交
        ▼
API 网关：身份/配额/题号校验/请求大小限制
        │ 内部任务队列，任务有用户归属
        ▼
可信调度器：固定镜像与固定命令，创建并监督容器
        │ stdin 写入 JSON；流式读取有上限的结果
        ▼
每次提交独立的临时沙箱：真实 CPU PyTorch + runner + 本次附件
        │ 完成、超时、超额或断开后统一销毁
        ▼
网关返回受限 JSON；不开放容器端口
```

每名学生必须有独立执行边界。这里建议进一步做到每次提交独立容器；若选择每学生一台临时虚拟机，也应在其中按提交重置工作空间。不同学生不得共用同一个长期 Python 解释器、`cwd` 或可写目录。可以预拉取固定镜像来减少冷启动，但不要复用已经执行过学生代码的可变容器。

API 网关与执行容器分别运行；执行容器不含网关会话密钥、云 API 密钥、课程管理员凭据、宿主目录或 Docker socket。仅可信调度器有创建执行环境的能力，学生不能提交镜像名、挂载路径、启动命令或 Docker 参数。

## Docker / 沙箱运行的必要条件

应在专用 Linux 执行主机验证以下配置。Docker 容器与宿主共享内核；普通容器不等于完整虚拟机。Rootless 能降低 daemon 与容器权限，但也不单独替代针对不可信代码的隔离层。[Docker Rootless 官方说明](https://docs.docker.com/engine/security/rootless/)

- 预构建不可变镜像：固定 Python、CPU PyTorch、NumPy 及课程版本；把 `runner.py`、`catalog.py`、`dist/grade.py` 与所需课程 JSON 放入镜像。镜像中不放任何凭据；运行中不开 `pip install`。
- 执行身份为非 root，根文件系统只读，去掉全部 capabilities，禁止获得新权限；不使用 privileged、host 网络、host PID/IPC 或宿主设备。保留适用的 seccomp 与主机安全策略；不要为了兼容直接使用 `seccomp=unconfined`。[Docker seccomp 文档](https://docs.docker.com/engine/security/seccomp/)
- 每次使用独立且有容量限制的临时可写目录，网络完全禁用。课程当前所需训练使用 CPU，无需 GPU 或设备透传。
- 宿主 cgroup 实际限制 CPU、内存、swap 和 PID 数；同时限制输出总字节、临时存储与队列并发。容器默认没有充分资源限制，必须明确设置并检查运行时是否生效。[Docker 资源限制](https://docs.docker.com/engine/containers/resource_constraints/)
- 超时由沙箱外部的调度器监督，并终止、删除整个执行容器。只停止 HTTP 请求、只终止 `docker run` 客户端或只杀一个 Python PID 都不足以证明清理完成。

下面是**尚未实测的启动参数示意**，不是已完成的部署脚本。`python-gym-runner:verified` 表示部署者需要构建并验证的自有固定镜像；生产环境应记录其 digest。`runsc` 也必须先按所选 Linux 环境配置，不能仅添加参数就认为安装完成。[gVisor Docker 接入](https://gvisor.dev/docs/user_guide/quick_start/docker/)

```sh
docker create --name job-SERVER_GENERATED_ID \
  --runtime=runsc \
  --interactive --network=none \
  --user=65532:65532 --read-only \
  --cap-drop=ALL --security-opt=no-new-privileges:true \
  --cpus=1 --memory=1536m --memory-swap=1536m \
  --pids-limit=128 --ulimit nofile=256:256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=128m \
  --workdir=/tmp --log-driver=none \
  --env HOME=/tmp --env USER=student \
  --env OMP_NUM_THREADS=1 --env MKL_NUM_THREADS=1 \
  --env OPENBLAS_NUM_THREADS=1 --env PYTHONDONTWRITEBYTECODE=1 \
  python-gym-runner:verified \
  python -X utf8 -I /app/runner.py
```

可信调度器随后 attach/start 容器，向 stdin 写入大小受限的 JSON 并关闭 stdin；增量读取 stdout/stderr，超过规定输出上限立即销毁容器。收集完整结果或失败状态后，在 `finally` 中删除容器，并用宿主定时回收任务处理调度器自身崩溃后遗留的容器。启动参数中的 1 CPU、1.5 GiB、128 PID、128 MiB 临时空间只是小题起始预算，需在整个题库与所选运行时上测量后调整。[Docker run 参数](https://docs.docker.com/reference/cli/docker/container/run/)

JSON 里的 code 只能作为数据通过 stdin 传递，不拼进 shell、镜像入口或容器名称。输出必须按文本处理、按 JSON 协议验证后再渲染，不能把学生 stdout 当 HTML。网关只允许服务端目录中的题号，不接受客户端上传参考解或判题表达式。

## 从草案到真正上线还缺什么

尚需实现网关、认证、队列、隔离调度器、结果协议和前端远程 API 接口；当前仓库没有这些公网服务。静态站本身只能调用另外配置并验证过的 HTTPS 后端。使用 Cookie 时需验证会话与 CSRF；跨域前后端需精确允许来源，不能用任意来源替代身份校验。

上线验收应在实际 Linux 镜像和沙箱内跑全题库与考核参考解，特别核对：PyTorch 自动求导、CPU profiler、空张量、临时文件、CSV/JSON、可信 checkpoint 的读写，以及错误与超时反馈。再用受控测试确认：不同任务无法读对方文件；执行容器无法访问网络和宿主秘密；内存/输出/进程限额真实生效；超时后整个容器消失；队列高峰不会无限增加宿主并发。

对外状态应明确区分“静态网站已发布”“原生 API 已部署”“PyTorch 代码已在该环境通过验证”。在上述实施和验收完成前，只能报告本机原生执行和浏览器纯 Python 能力。

## 浏览器路线的核对依据

当前 Pyodide 官方预构建包列表未列出 `torch`；普通 Linux/Windows PyTorch 二进制 wheel 也不能因使用 `micropip` 就自动适配浏览器。现有浏览器 Python Worker 因此不能承诺 `import torch`。[Pyodide 当前包列表](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)

ExecuTorch 的浏览器文档确实列出 WebGPU/Emscripten，但明确标为实验性，采用 `torch.export` → 委派图 → `.pte` → 浏览器执行的路径。把它用于已导出模型可视化是可研究方向；这与本课程任意代码、autograd、优化器和 checkpoint 的完整兼容是不同的验证目标。上文关于不能替代完整题库运行时的判断是基于这一工作流的工程推断，而非声称浏览器永远不能运行 PyTorch。[官方 WebGPU 工作流](https://docs.pytorch.org/executorch/stable/backends/webgpu/webgpu-overview.html)
