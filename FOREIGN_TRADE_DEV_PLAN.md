# VM 外贸工具 - 开发计划

## 项目概述
基于 Art Design Pro 模板，为阿里巴巴国际站卖家打造的团队协作工具。

## 核心功能模块

### 1. 仪表盘 (Dashboard)
- [ ] 汇率实时显示卡片
- [ ] 今日订单统计
- [ ] 待办事项
- [ ] 快捷入口

### 2. 产品管理 (Products)
- [ ] 产品列表（在线表格，支持筛选排序分页）
- [ ] 产品详情页
  - 基本信息（名称/SKU/图片）
  - 阿里巴巴信息（链接/上架时间/状态）
  - 供货商信息（1688链接/厂家/采购价）
  - 利润计算
- [ ] 添加/编辑产品表单
- [ ] 批量导入导出

### 3. 供货商管理 (Suppliers)
- [ ] 供货商列表
- [ ] 供货商详情（联系方式/合作产品）
- [ ] 添加/编辑

### 4. 运费计算器 (Shipping)
- [ ] 输入区（重量/体积/目的地）
- [ ] 物流方式选择
- [ ] 结果展示（费用/时效）

### 5. 在线表格 (Spreadsheet)
- [ ] 可编辑表格组件
- [ ] 公式计算
- [ ] 导出 Excel/CSV

### 6. 系统设置 (Settings)
- [ ] 用户管理
  - 用户列表
  - 角色权限（管理员/普通用户）
  - 添加/编辑用户
- [ ] 汇率API配置
- [ ] 物流渠道配置

## 技术栈
- 前端: Vue3 + TypeScript + Vite + Element Plus + Tailwind CSS
- 后端: FastAPI + SQLAlchemy + SQLite（后续可迁移到PostgreSQL）
- 部署: 当前服务器 (154.219.108.60)

## 开发阶段

### 阶段一：基础框架搭建（1-2天）
- [ ] 项目结构调整
- [ ] 路由配置
- [ ] API接口设计
- [ ] 数据库设计

### 阶段二：核心功能开发（3-5天）
- [ ] 仪表盘页面
- [ ] 产品管理模块
- [ ] 供货商管理模块

### 阶段三：辅助功能开发（2-3天）
- [ ] 运费计算器
- [ ] 在线表格
- [ ] 汇率显示组件

### 阶段四：系统完善（1-2天）
- [ ] 用户权限系统
- [ ] 系统设置
- [ ] 测试和优化

## 数据库设计

### 用户表 (users)
```sql
id, username, password_hash, email, role, created_at, updated_at
```

### 产品表 (products)
```sql
id, name, sku, category, image_url, 
alibaba_link, listing_date, listing_status,
supplier_id, purchase_price, selling_price,
description, created_at, updated_at
```

### 供货商表 (suppliers)
```sql
id, name, type (1688/厂家/其他), 
contact_person, phone, email, 
link, address, notes,
created_at, updated_at
```

### 订单表 (orders)
```sql
id, product_id, customer_name, customer_email,
quantity, total_price, status,
created_at, updated_at
```

## API接口设计

### 认证接口
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/me

### 产品接口
- GET /api/products
- GET /api/products/:id
- POST /api/products
- PUT /api/products/:id
- DELETE /api/products/:id
- POST /api/products/import
- GET /api/products/export

### 供货商接口
- GET /api/suppliers
- GET /api/suppliers/:id
- POST /api/suppliers
- PUT /api/suppliers/:id
- DELETE /api/suppliers/:id

### 汇率接口
- GET /api/exchange-rate

### 运费计算接口
- POST /api/shipping/calculate

## 配色方案
- 主色: #1890FF（蓝色）
- 辅助色: #52C41A（绿色）
- 背景色: #F5F7FA（浅灰）
- 文字色: #333333（深灰）

## 页面布局
```
┌─────────────────────────────────────────────┐
│  顶部导航栏 (Logo + 搜索 + 用户头像 + 通知)   │
├──────┬──────────────────────────────────────┤
│      │                                      │
│  侧  │          主 内 容 区                  │
│  边  │                                      │
│  导  │                                      │
│  航  │                                      │
│  栏  │                                      │
│      │                                      │
├──────┴──────────────────────────────────────┤
│  底部状态栏 (版本 + 在线用户数)                │
└─────────────────────────────────────────────┘
```
