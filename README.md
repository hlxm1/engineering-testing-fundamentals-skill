# 工程测试技术基础 · 可溯源学习技能

以曾光奇、胡均安主编《工程测试技术基础》（华中科技大学出版社，2002）为学习来源，将知识整理为可调用的agent skill与工程判断工具。

**9章 · 46小节导航 · 双页码索引 · 公式核验分级 · 原创算例 · 自动测试**

> 本仓库不是电子书镜像，不含原书PDF、扫描图片或全文OCR。内容为AI辅助原创提炼；不能代替原书、现行标准、计量校准或安全认证。

## 先从这里开始
- [技能入口](skills/zeng-engineering-testing/SKILL.md)：调用规则、测量主线、章节与主题索引。
- [决策速查](skills/zeng-engineering-testing/cheatsheet.md)：什么时候用什么方法，哪些现象意味着要改方案。
- [学习路径](skills/zeng-engineering-testing/references/learning-path.md)：九单元学习与自测。
- [方法模式](skills/zeng-engineering-testing/patterns.md)与[双语术语](skills/zeng-engineering-testing/glossary.md)。
- [公式核验](skills/zeng-engineering-testing/references/formula-audit.md)：V=选定原页视觉核验；D=推导/自定义教学模型；U=待核验。
- [来源与46小节页码](skills/zeng-engineering-testing/references/source-index.json)、[质量报告](skills/zeng-engineering-testing/references/quality-report.md)。

## 内容
| 章 | 主题 | 解决的问题 |
|---|---|---|
| 1 | 信号分析 | 均值/RMS、频谱、相关与功率谱怎么选 |
| 2 | 装置响应 | 静态准确为什么仍可能动态失真 |
| 3 | 传感器 | 原理、安装、交叉敏感与调理如何匹配 |
| 4 | 智能化传感器 | 补偿、自诊断、模糊语言输出如何验证 |
| 5 | 信号调理 | 桥路、调制、滤波、采样与ADC如何连接 |
| 6 | 记录存储 | 带宽、时基、吞吐与记录容量如何预算 |
| 7 | 分析仪/微机 | 混叠、泄漏、栅栏效应与多通道同步 |
| 8 | 虚拟仪器 | 硬件、算法、界面如何分层与验证 |
| 9 | 典型量测量 | 振动、位移、速度、噪声、温度和压力 |

## 安装skill
`skills/zeng-engineering-testing/`是完整、独立的技能目录；复制整个目录到你所用agent已经配置的技能根目录即可。也可以使用不覆盖已有文件的安装脚本：

```text
python scripts/install_skill.py --dest "<你的技能根目录>"
```

脚本只复制该技能，不读取原书、不联网、不修改agent全局配置。若目录已存在，停止而不覆盖。你也可以只在线阅读，无需安装。

### 可用的提问示例
- “使用zeng-engineering-testing解释RMS与标准差，给出自编算例和两套来源页码。”
- “时间常数0.1s的传感器测1Hz信号，分别估计幅值与相位误差。”
- “给一个应变桥设计方案，先列激励、桥臂变化、增益、ADC跨度及抗混叠条件。”
- “按第9章设计机床振动测量计划，区分安装、同步、标定和频谱误差。”

## 运行原创教学程序
Python 3.10+，只用标准库；运行不依赖PDF、OCR、网络或付费API。

```text
python examples/run_examples.py
python -m unittest discover -s tests -v
python scripts/validate_repo.py
```

示例演示统计量、一阶响应、桥路输出、量化区间、混叠、测速、声压级及小规模DFT。程序不驱动真实硬件，不是认证测量软件。DFT为教学直算，非生产FFT。

- [测量计划模板](templates/measurement-plan.md)
- [采样记录元数据模板](templates/acquisition-metadata.json)
- [验证记录](VALIDATION.md)与[机器可读结果](validation-results.json)

## 原书溯源与已记录差异
曾光奇、胡均安主编，卢文祥主审；华中科技大学出版社；2002年3月第1版；ISBN 7-5609-2668-1。输入PDF共308页，正文及参考文献的逻辑印刷页为1–294，对应PDF10–303。

- 第4章目录起页123，实际章首页PDF131（逻辑印刷p.122），索引按实际位置记录。
- p.240机械阻抗概述与随后列式方向不同；技能显式区分F/X、F/V、F/A和倒数导纳。
- 旧软件、磁带/软盘规格及噪声标准只保留时代语境，不作为当前操作或合规依据。

## 整理方法与范围
使用本地book-to-skill工作流；扫描版先逐页本地OCR，再按目录分章提炼并重点查看公式原页。OCR完成不等于全部文字和习题已人工核对。识别模型分数不当作准确率。完整范围和未核验项见质量报告。

## 版权与许可
仓库原创文字、程序和模板采用MIT许可，范围见[LICENSE](LICENSE)。书名、作者等书目信息用于来源说明；教材及第三方内容权利不因本仓库许可而改变，见[NOTICE](NOTICE)。请使用合法获得的原书进行深度学习与核验。
