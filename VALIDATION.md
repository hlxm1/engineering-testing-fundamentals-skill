# 验证记录

日期：2026-10-20。环境：Python 3.12 / Windows；仓库中的教学程序及结构验证仅依赖Python标准库。

## 本次结果
- 结构、相对链接、JSON、UTF-8、Python语法及发布文件检查：通过。
- 分章索引：9章、46小节；OCR统计页码连续覆盖308页。
- 原创计算测试：**21项通过，0失败、0错误**；覆盖统计、标定、一/二阶、桥路、ADC、混叠、测速、声压与DFT端点。
- 例程输出与[参考结果](examples/expected-results.json)：相对/绝对容差1e-12内一致；无实测或安全阈值含义。
- skill-creator基础格式检查：通过。
- book-to-skill安全扫描：核心13份Markdown通过；再用同一文本规则扩展检查仓库全部Markdown，未发现已知注入/越权模式。该扫描不是全面安全审计，第三方扫描器仅在本机运行，未复制入仓库。
- 安装脚本：私有临时目录复制结果与源技能逐文件一致；已存在目标会拒绝覆盖。
- 发布文件：仅原创文字、程序、模板与来源/质量元数据；无PDF、扫描图片、全文OCR、模型、个人路径或识别到的凭据模式。
- 连续原文匹配辅助检查：公开Markdown未发现与私有OCR去空白后连续80字符相同的片段。该启发式不是法律结论或完整版权检测。
- 技能入口与支撑文件符合转换流程检索预算；所用o200k_base编码为尺寸估算，不等于实际会话用量。详见[token计数](skills/zeng-engineering-testing/references/token-budget.json)。

## 可重复运行
```text
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python examples/run_examples.py
```

上述命令不需要原书、OCR环境、联网、私有路径或付费服务。CI运行结构检查、计算测试和例程；安全扫描结果为本次本地检查的记录。

## 完整性
[artifact-manifest.json](artifact-manifest.json)记录发布文件SHA-256和字节数，结构验证脚本会核对。为避免递归自校验，manifest自身、本文与validation-results.json不列入其哈希覆盖；Git提交记录覆盖它们。公开仓库的Git可见性、提交与远端状态在推送后另行核实。

## 未声称完成的事
没有逐字人工校对全书，没有解完全部习题，没有复刻全部历史CVI代码，没有核对所有数表、标准限值或器件现行性。视觉核验范围与待查项见[公式记录](skills/zeng-engineering-testing/references/formula-audit.md)和[质量报告](skills/zeng-engineering-testing/references/quality-report.md)。
