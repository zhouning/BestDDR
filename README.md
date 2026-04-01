# BestDDR

**中小企业财务报表预测系统** | Financial Forecast System for SMEs

基于历史财务数据和关键假设参数，自动生成符合中国企业会计准则的三年财务预测（利润表、资产负债表、现金流量表），三表联动，迭代收敛。

> https://www.bestddr.com

---

## 功能特性

- **三表联动模型** — 利润表驱动资产负债表，两者共同驱动现金流量表（间接法），自动迭代收敛处理利息/债务循环依赖
- **多场景对比** — 为同一家公司创建乐观、基准、悲观等多个预测场景，独立假设参数和预测结果
- **5 大行业模板** — 通用、制造业、科技、零售、服务业，各自预设行业适配的默认假设参数
- **历史数据录入** — 按利润表 / 资产负债表 / 现金流量表分类录入，支持多年数据
- **假设参数管理** — 收入增长率、毛利率、DSO/DIO/DPO 周转天数、资本开支比例、折旧率、税率等，逐年独立设置
- **自动平衡** — 资产负债表不平衡时自动通过短期借款（Debt Plug）补齐差额
- **报表导出** — 支持 Excel (.xlsx) 和 HTML 报告导出
- **中英文切换** — 默认中文，一键切换英文，所有页面完整国际化
- **安全认证** — JWT 认证 + 强密码策略 + 速率限制 + CORS 保护，数据按用户隔离

## 技术栈

| 层      | 技术 |
|---------|------|
| 后端    | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · Alembic |
| 前端    | React 19 · TypeScript · Vite · Ant Design 6 |
| 数据库  | PostgreSQL (asyncpg / psycopg) |
| 安全    | JWT (python-jose) · PBKDF2-SHA256 · 速率限制 · CORS 保护 |
| 国际化  | react-i18next · Ant Design locale |
| 导出    | openpyxl (Excel) · HTML 报告 |

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── auth.py              # JWT 认证 + 密码哈希
│   ├── seed.py              # 启动时初始化行业模板和科目定义
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── schemas/             # Pydantic 请求/响应模式
│   ├── routers/             # API 路由
│   │   ├── auth.py          #   注册 / 登录 / Token 刷新
│   │   ├── companies.py     #   公司 CRUD
│   │   ├── periods.py       #   历史数据录入
│   │   ├── scenarios.py     #   场景 / 假设 / 预测 / 报表
│   │   └── export.py        #   Excel / HTML 导出
│   └── engine/              # 预测引擎（纯函数，无 DB 依赖）
│       ├── income_statement.py
│       ├── balance_sheet.py
│       ├── cash_flow.py
│       ├── balancer.py      #   资产负债表自动平衡
│       └── forecast.py      #   迭代收敛主流程
frontend/
├── src/
│   ├── pages/               # 页面组件
│   │   ├── LoginPage.tsx    #   登录
│   │   ├── Dashboard.tsx    #   公司列表
│   │   ├── CompanyDetail.tsx#   数据录入 / 假设 / 报表 / 导出
│   │   └── HelpPage.tsx     #   使用指南
│   ├── locales/             # 中英文翻译
│   ├── contexts/            # Auth Context
│   └── api.ts               # API 封装
```

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

### 1. 克隆项目

```bash
git clone https://github.com/zhouning/BestDDR.git
cd BestDDR
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入数据库连接和 JWT 密钥
```

### 3. 启动数据库

```bash
docker compose up -d db
```

### 4. 启动后端

```bash
cd backend
uv sync --all-extras
uv run uvicorn app.main:app --reload --port 8002
```

后端启动时会自动创建表结构并初始化行业模板数据。

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 使用流程

```
创建公司 → 录入历史数据 → 创建预测场景 → 设置假设参数 → 运行预测 → 查看三表 → 导出报告
```

1. **创建公司** — 输入公司名称，选择行业模板
2. **录入历史数据** — 添加年份，填入利润表、资产负债表、现金流量表的关键科目
3. **创建场景** — 如"基准情景"、"乐观情景"，设置预测年份（如 2025-2027）
4. **调整假设参数** — 收入增长率、毛利率、周转天数等，每年可独立设置
5. **运行预测** — 引擎自动计算三表，迭代收敛处理利息/债务循环
6. **查看报表** — 历史数据（灰色）与预测数据（蓝色）并排展示，资产负债表自动校验平衡
7. **导出** — Excel 或 HTML 格式下载

## 预测引擎原理

```
利润表 → 资产负债表 → 自动平衡(Debt Plug) → 现金流量表 → 回写现金 → 迭代收敛
```

- **利润表**：收入 × 增长率 → 成本（毛利率）→ 费用（费用率）→ 利息（债务 × 利率）→ 净利润
- **资产负债表**：应收(DSO) / 存货(DIO) / 应付(DPO) / 固定资产(CapEx-折旧) / 留存收益
- **自动平衡**：资产 ≠ 负债+权益时，差额计入短期借款
- **现金流量表**：间接法，净利润 + 非现金项 + 营运资金变动
- **迭代收敛**：利息费用 ↔ 债务余额循环依赖，通常 2-3 轮收敛

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 登录获取 Token |
| GET/POST/DELETE | `/api/companies` | 公司 CRUD |
| GET/POST | `/api/companies/:id/periods` | 历史数据 |
| GET/POST/DELETE | `/api/companies/:id/scenarios` | 场景管理 |
| GET/PUT | `/api/companies/:id/scenarios/:sid/assumptions` | 假设参数 |
| POST | `/api/companies/:id/scenarios/:sid/forecast` | 运行预测 |
| GET | `/api/companies/:id/scenarios/:sid/statements` | 三表数据 |
| GET | `/api/companies/:id/scenarios/:sid/export/excel` | 导出 Excel |
| GET | `/api/companies/:id/scenarios/:sid/export/pdf` | 导出 HTML 报告 |

## License

MIT
