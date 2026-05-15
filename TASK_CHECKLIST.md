# 外贸团队协作工具 - 后续完善任务清单

## 项目路径
~/projects/art-design-pro

## 技术栈
- 前端: Vue3 + TypeScript + Vite + Element Plus + Tailwind CSS
- 后端: FastAPI + SQLAlchemy + SQLite
- 部署: 当前服务器 (154.219.108.60)

## 任务清单

### 阶段一：后端API开发（优先级：高）✅ 已完成

#### 1.1 创建FastAPI后端项目
- [x] 在 ~/projects/art-design-pro/backend 目录创建FastAPI项目
- [x] 配置数据库连接（SQLite）
- [x] 创建基础项目结构

#### 1.2 数据库设计与实现
- [x] 创建用户表 (users)
- [x] 创建产品表 (products)
- [x] 创建供货商表 (suppliers)
- [x] 创建订单表 (orders) - 暂未实现
- [x] 创建汇率配置表 (exchange_rates) - 使用 Frankfurter API 实时获取

#### 1.3 API接口开发
- [x] 认证接口
  - POST /api/auth/login
  - POST /api/auth/register
  - GET /api/auth/me
  - GET /api/auth/users（管理员）
  - PUT /api/auth/users/:id（管理员）
  - DELETE /api/auth/users/:id（管理员）
- [x] 产品接口
  - GET /api/products（列表，支持分页、筛选、排序）
  - GET /api/products/:id（详情）
  - POST /api/products（创建）
  - PUT /api/products/:id（更新）
  - DELETE /api/products/:id（删除）
  - POST /api/products/import（批量导入CSV）
  - GET /api/products/export/csv（导出CSV）
- [x] 供货商接口
  - GET /api/suppliers（列表）
  - GET /api/suppliers/:id（详情）
  - POST /api/suppliers（创建）
  - PUT /api/suppliers/:id（更新）
  - DELETE /api/suppliers/:id（删除）
- [x] 汇率接口
  - GET /api/exchange-rate（获取实时汇率 - Frankfurter API）
  - GET /api/exchange-rate/multi（多币种汇率）
- [x] 运费计算接口
  - POST /api/shipping/calculate（计算运费）
- [x] 统计接口
  - GET /api/statistics/dashboard（仪表盘统计数据）
- [x] 图片上传接口
  - POST /api/upload/image（上传图片）

### 阶段二：前端功能完善（优先级：高）✅ 已完成

#### 2.1 接入真实API
- [x] HTTP请求工具类 (src/utils/http/index.ts)
- [x] API接口文件 (src/api/foreign-trade/)
  - auth.ts
  - products.ts
  - suppliers.ts
  - shipping.ts
  - statistics.ts
  - users.ts
  - types.ts
- [x] 前端页面已接入真实API

#### 2.2 用户认证系统
- [x] 登录页面逻辑（对接 /api/auth/login）
- [x] 注册页面逻辑（对接 /api/auth/register）
- [x] Token管理（Bearer token 存储在 localStorage）
- [x] 路由守卫（权限控制）

#### 2.3 产品管理完善
- [x] 产品列表页面（从API加载）
- [x] 产品添加对话框（调用 createProduct）
- [x] 产品编辑对话框（调用 updateProduct）
- [x] 产品删除（调用 deleteProduct）
- [x] 批量导入功能（CSV上传）
- [x] 导出功能（CSV下载）

#### 2.4 供货商管理完善
- [x] 供货商列表（从API加载）
- [x] 供货商添加/编辑/删除（对接真实API）

#### 2.5 运费计算器完善
- [x] 运费计算对接后端API
- [x] 显示多渠道报价（快递、空运、海运）

#### 2.6 在线表格完善
- [x] 导出Excel功能（使用 xlsx 库）
- [x] 添加/删除行
- [x] 单元格编辑
- [x] 撤销/重做

#### 2.7 系统设置完善
- [x] 用户管理页面（添加/编辑/禁用/删除）
- [x] 汇率配置页面（显示来源说明、更新时间）
- [x] 物流渠道配置页面

### 阶段三：免费API集成（优先级：中）✅ 已完成

#### 3.1 汇率API
- [x] 使用 Frankfurter API (https://api.frankfurter.app) - 完全免费无限制
- [x] 汇率实时更新（前端每5分钟自动刷新）
- [x] 基于ECB数据

#### 3.2 运费计算
- [x] 后端实现运费计算逻辑（基于重量/体积/目的地）
- [x] 支持 EMS、DHL、FedEx、UPS、专线物流

#### 3.3 图片上传
- [x] 后端实现本地图片上传
- [x] 图片保存到 backend/uploads/ 目录
- [x] 静态文件服务

### 阶段四：测试与部署（优先级：中）🔄 进行中

#### 4.1 功能测试
- [x] 后端API测试（所有接口返回200）
- [x] 前端页面功能测试
- [ ] 完整用户流程测试

#### 4.2 部署
- [x] 后端服务运行在 http://154.219.108.60:8001
- [x] 前端服务运行在 http://154.219.108.60:3006
- [ ] 配置Nginx反向代理（可选）

## 免费API资源

### 汇率API
- Frankfurter (https://www.frankfurter.app/) - 已集成
  - 完全免费，无限制
  - 基于ECB数据
  - 支持 USD, CNY, EUR, GBP, JPY 等

## 已知问题
1. passlib 与 bcrypt>=4.1 不兼容，已降级到 bcrypt==4.0.1
2. 默认管理员账号: admin / admin123

## 注意事项
1. 所有API密钥应存储在环境变量中，不要硬编码
2. 数据库操作使用ORM，防止SQL注入
3. 用户密码必须加密存储
4. 实现请求频率限制，防止滥用
5. 添加错误处理和日志记录
