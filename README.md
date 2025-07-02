# 医疗保险理赔智能审核系统 🏥

一个基于多智能体协作架构的医疗保险理赔申请自动审核系统，模仿 Claude 的 Lead Agent + Subagents 模式。支持真实MIMIC-III医疗数据处理。

## 🚀 核心功能

- **智能信息提取**: 从理赔申请文本中自动提取关键信息（支持中英文、JSON格式）
- **保险条款检查**: 验证理赔申请是否符合保险条款（支持MIMIC-III常见医疗程序）
- **风险评估**: 基于金额、诊断和治疗类型进行多维度风险等级评估
- **智能决策**: 综合多方面信息做出最终审核决定
- **MIMIC-III集成**: 支持真实ICU医疗数据处理和分析

## 🧠 智能体架构

```
Lead Agent (主导智能体)
├── Claim Extractor (信息提取智能体) - 支持中英文+JSON
├── Policy Checker (条款检查智能体) - 包含MIMIC医疗程序
└── Decision Maker (决策制定智能体) - 多维度评估
```

### 各智能体职责

1. **Lead Agent**: 协调整个审核流程，调度其他智能体
2. **Claim Extractor**: 从文本中提取患者信息、诊断、治疗方案、费用等
3. **Policy Checker**: 检查承保范围、金额限制、排除条款等
4. **Decision Maker**: 综合所有信息做出最终决策

## 📁 项目结构

```
healthcare-project/
├── agents/                   # 智能体定义
│   ├── __init__.py
│   ├── lead_agent.py        # 主导智能体
│   ├── claim_extractor.py   # 信息提取智能体（支持多格式）
│   ├── policy_checker.py    # 条款检查智能体（支持MIMIC程序）
│   └── decision_maker.py    # 决策制定智能体
├── data/                     # 数据处理
│   ├── sample_claims.txt    # 示例理赔申请
│   ├── mimic_data_processor.py  # MIMIC-III数据处理器
│   └── mimic_claims.json    # 生成的MIMIC理赔数据
├── scripts/                  # 运行脚本
│   ├── run_agents.py        # 基础演示脚本
│   └── run_mimic_agents.py  # MIMIC数据演示脚本
├── requirements.txt          # 项目依赖
├── instructions.txt          # 项目指导文档
├── .gitignore               # Git忽略文件
└── README.md                # 项目说明
```

## 🛠️ 安装运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行基础演示

```bash
python scripts/run_agents.py
```

### 3. 运行MIMIC-III数据演示

```bash
# 生成MIMIC数据
python data/mimic_data_processor.py

# 运行智能审核
python scripts/run_mimic_agents.py
```

## 📊 MIMIC-III 数据集成

### 支持的ICD-9诊断代码
- 038.9: Unspecified septicemia
- 584.9: Acute kidney failure
- 518.81: Acute respiratory failure
- 410.71: Subendocardial infarction
- 428.0: Congestive heart failure
- 以及更多...

### 支持的ICD-9手术代码  
- 96.72: Continuous mechanical ventilation
- 96.04: Insertion of endotracheal tube
- 38.95: Venous catheterization
- 89.54: Monitoring of electrocardiogram
- 以及更多...

## 📊 演示结果

最新运行结果（真实MIMIC数据）：
- **处理案例**: 10个真实ICU患者理赔申请
- **批准率**: 60% (6个批准，4个拒绝)
- **总申请金额**: $130,760.11
- **批准金额**: $33,944.30
- **节省金额**: $96,815.81

## 🎯 决策类型

- **批准**: 完全符合保险条款
- **条件批准**: 符合条款但需要额外条件  
- **需要人工审核**: 高风险案例需要人工复核
- **拒绝**: 不符合保险条款要求

## 🔧 技术特性

- ✅ 多语言支持（中文、英文）
- ✅ 多格式数据处理（文本、JSON）
- ✅ 真实医疗数据集成（MIMIC-III）
- ✅ 智能风险评估（基于诊断+治疗+金额）
- ✅ 详细决策报告（理由+置信度+时间戳）
- ✅ 统计分析和财务报告

## 🏥 MIMIC-III 数据库

MIMIC-III 是公开的ICU病历数据库，包含去标识化的真实患者数据：
- 🔗 **申请地址**: https://physionet.org/content/mimiciii/1.4/
- 📋 **数据来源**: Beth Israel Deaconess Medical Center ICU
- 🔒 **隐私保护**: 完全去标识化处理
- 📊 **数据规模**: 40,000+住院记录，58,000+患者

## 🚀 Colab GPU 部署

按照 [cursor-colab-workflow](https://github.com/SophieXueZhang/cursor-colab-workflow-en) 推送到GitHub后在Colab中运行：

```bash
# 在Colab中克隆项目
!git clone https://github.com/your-username/healthcare-claim-auditor.git
%cd healthcare-claim-auditor

# 安装依赖
!pip install -r requirements.txt

# 运行MIMIC演示
!python scripts/run_mimic_agents.py
```

## 🔧 自定义配置

### 添加新的医疗程序
在 `agents/policy_checker.py` 中更新 `coverage_procedures` 列表

### 调整成本估算
在 `data/mimic_data_processor.py` 中修改 `cost_ranges` 字典

### 添加新的诊断代码
更新 `icd9_diagnoses` 和 `icd9_procedures` 映射

## 🚀 未来扩展

- [ ] 集成大语言模型（OpenAI、Claude）
- [ ] 连接真实保险条款数据库
- [ ] 添加机器学习风险模型
- [ ] 支持更多医疗数据格式（HL7、FHIR）
- [ ] 添加Web用户界面
- [ ] 支持实时数据流处理

## 📝 使用说明

1. 系统支持中英文理赔申请文本和JSON格式
2. 自动识别语言并提取关键信息
3. 基于预设条款和MIMIC医疗程序进行合规检查
4. 输出详细的审核决策、理由和置信度
5. 生成统计分析和财务报告

这是一个完整的MVP系统，集成了真实医疗数据处理能力，可以直接用于演示和进一步开发。 