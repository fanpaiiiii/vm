# 外贸团队协作工具

轻量级外贸团队协作工具，面向阿里巴巴国际站运营团队。

## 功能模块

- **工作台** - 仪表盘概览、汇率显示、快捷入口
- **产品管理** - 产品列表、添加/编辑/删除、详情查看
- **供货商管理** - 供货商信息维护、关联产品
- **运费计算** - 多渠道物流费用估算（快递/空运/海运）
- **在线表格** - 数据编辑与管理
- **系统设置** - 用户管理、汇率配置、物流渠道配置

## 技术栈

**前端**
- Vue 3 + TypeScript + Vite
- Element Plus + Tailwind CSS
- Pinia 状态管理

**后端**
- FastAPI + SQLAlchemy + SQLite
- JWT 认证
- Frankfurter 汇率 API（免费）

## 快速开始

```bash
# 前端
pnpm install
pnpm dev

# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 默认账号

- 用户名: `admin`
- 密码: `admin123`
