# 美股投资AI策略生成器

基于DeepSeek大模型的智能美股投资策略生成系统，为投资者提供专业的投资建议和风险分析。

## 🚀 功能特点

- **AI驱动分析**: 集成DeepSeek大模型，提供专业投资策略分析
- **实时市场数据**: 获取美股主要指数和个股实时数据
- **多种投资风格**: 支持价值投资、成长投资、动量投资等多种策略
- **风险管理**: 智能仓位控制和风险评估
- **历史回测**: 提供投资组合历史表现分析
- **响应式设计**: 现代化Web界面，支持移动端访问

## 🛠️ 技术栈

### 前端
- React 18 + TypeScript
- Tailwind CSS
- Axios (API调用)
- Recharts (图表展示)

### 后端
- Python Flask
- AKShare (金融数据获取)
- DeepSeek API (AI分析)
- pandas + numpy (数据处理)

## 📦 安装部署

### 环境要求
- Node.js 16+
- Python 3.8+
- DeepSeek API密钥

### 1. 克隆项目
```bash
git clone https://github.com/your-username/ai-stock-strategy.git
cd ai-stock-strategy
```

### 2. 后端设置
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，添加你的DeepSeek API密钥
```

### 3. 前端设置
```bash
# 安装Node.js依赖
npm install

# 启动开发服务器
npm start
```

### 4. 启动后端
```bash
python app_with_deepseek.py
```

## 🔧 配置说明

### 环境变量 (.env)
```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=True

# 端口配置
PORT=5001
```

### DeepSeek API密钥获取
1. 访问 [DeepSeek官网](https://platform.deepseek.com)
2. 注册账号并获取API密钥
3. 将密钥配置到环境变量中

## 📊 使用说明

1. **设置投资偏好**: 选择投资金额、交易风格、风险偏好等参数
2. **生成AI策略**: 系统将基于DeepSeek大模型生成专业投资策略
3. **查看分析结果**: 包括市场分析、股票推荐、风险评估等
4. **历史回测**: 查看投资组合的历史表现数据

## 🎯 投资策略类型

- **价值投资**: 关注低估值、高分红的优质股票
- **成长投资**: 专注高成长性的科技和新兴行业股票
- **动量投资**: 基于技术分析和市场趋势的投资策略
- **逆向投资**: 寻找被市场低估的反转机会
- **低波动**: 追求稳健收益的低风险投资组合

## 🔒 风险管理

- 智能仓位控制，单只股票权重不超过设定比例
- 实时风险评估和止损建议
- 多元化投资组合构建
- 市场情景分析和压力测试

## 📈 数据来源

- **市场数据**: AKShare提供的实时美股数据
- **AI分析**: DeepSeek大模型提供的智能投资分析
- **历史数据**: 支持最长2年的历史回测数据

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

本系统仅供教育和研究目的使用。所有投资建议仅供参考，不构成实际投资建议。投资有风险，入市需谨慎。使用者应当根据自身情况做出独立的投资决策，并承担相应的投资风险。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-username/ai-stock-strategy/issues)
- 发送邮件至: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！# AI_Finance
