# Stock Analysis

股票数据分析与机器学习预测平台，提供数据获取、模型训练、价格预测等功能。

## 功能特性

- **数据获取** - 通过 yfinance 获取股票 OHLCV 数据，支持单只/批量获取
- **数据存储** - SQLite 本地存储股票数据与预测结果
- **机器学习** - 基于 RandomForest 的股票价格预测模型
- **REST API** - FastAPI 提供完整的数据与模型接口
- **后台任务** - 支持异步执行耗时操作（训练、数据获取）
- **离线分析** - 专注于本地数据分析与模型训练

## 项目结构

```
stock_analysis/
├── src/
│   ├── data/              # 数据获取模块
│   │   ├── fetcher.py     # yfinance 数据拉取
│   │   └── models.py      # OHLCV 数据模型
│   ├── ml/                # 机器学习模块
│   │   ├── train.py       # 模型训练
│   │   ├── predict.py     # 模型预测
│   │   └── models/        # 保存的模型文件
│   ├── storage/           # 数据存储模块
│   │   ├── database.py    # 数据库连接 (SQLite)
│   │   ├── models.py      # SQLAlchemy 模型
│   │   └── crud.py        # 数据库操作
│   ├── api/               # API 接口模块
│   │   ├── main.py        # FastAPI 应用
│   │   ├── schemas.py     # 请求/响应模型
│   │   └── routes/        # 路由定义
│   └── tasks/             # 后台任务模块
│       ├── celery_app.py  # 任务执行器
│       ├── ml_tasks.py    # ML 任务
│       ├── data_tasks.py  # 数据任务
│       └── scheduler.py   # 定时任务
├── alembic/               # 数据库迁移
├── tests/                 # 测试文件
├── main.py                # 应用入口
└── requirements.txt       # 依赖列表
```

## 快速开始

### 环境要求

- Python 3.10+

### 安装

```bash
git clone https://github.com/neimengtian/stock_analysis.git
cd stock_analysis
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 配置

创建 `.env` 文件（可选）：

```env
DATABASE_URL=sqlite:///stock_data.db
```

### 数据库迁移

```bash
alembic upgrade head
```

### 启动服务

```bash
python main.py
```

## API 接口

### 股票数据

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/stocks/` | 创建股票记录 |
| GET | `/stocks/{ticker}` | 获取股票信息 |
| GET | `/stocks/{ticker}/prices` | 获取历史价格 |
| POST | `/stocks/{ticker}/fetch` | 获取数据（同步） |
| POST | `/stocks/{ticker}/fetch/background` | 获取数据（后台） |

### 机器学习

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/ml/train` | 训练模型（同步） |
| POST | `/ml/train/background` | 训练模型（后台） |
| POST | `/ml/predict` | 获取预测（同步） |
| POST | `/ml/predict/background` | 获取预测（后台） |
| GET | `/ml/tasks/{task_id}` | 查询后台任务状态 |

### 示例

```bash
# 获取苹果股票数据
curl -X POST http://localhost:8000/stocks/AAPL/fetch

# 训练模型
curl -X POST http://localhost:8000/ml/train \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# 获取预测
curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "days_ahead": 1}'
```

## 测试

```bash
pytest tests/
```

## 技术栈

- **后端框架**: FastAPI
- **机器学习**: scikit-learn, pandas, numpy
- **数据源**: yfinance
- **数据库**: SQLite + SQLAlchemy
- **数据库迁移**: Alembic

## License

MIT
