/**
 * 快速入口配置
 */
import type { FastEnterConfig } from '@/types/config'

const fastEnterConfig: FastEnterConfig = {
  // 显示条件（屏幕宽度）
  minWidth: 1200,
  // 应用列表
  applications: [
    {
      name: '工作台',
      description: '系统概览与数据统计',
      icon: 'ri:pie-chart-line',
      iconColor: '#377dff',
      enabled: true,
      order: 1,
      routeName: 'ForeignTradeDashboard'
    },
    {
      name: '产品管理',
      description: '产品列表与管理',
      icon: 'ri:shopping-bag-line',
      iconColor: '#ff3b30',
      enabled: true,
      order: 2,
      routeName: 'ForeignTradeProductsList'
    },
    {
      name: '供货商',
      description: '供货商信息管理',
      icon: 'ri:building-line',
      iconColor: '#7A7FFF',
      enabled: true,
      order: 3,
      routeName: 'ForeignTradeSuppliersList'
    },
    {
      name: '运费计算',
      description: '物流运费估算',
      icon: 'ri:truck-line',
      iconColor: '#13DEB9',
      enabled: true,
      order: 4,
      routeName: 'ForeignTradeShipping'
    },
    {
      name: '在线表格',
      description: '数据表格编辑',
      icon: 'ri:file-list-line',
      iconColor: '#ffb100',
      enabled: true,
      order: 5,
      routeName: 'ForeignTradeSpreadsheet'
    },
    {
      name: '系统设置',
      description: '汇率与物流渠道配置',
      icon: 'ri:settings-line',
      iconColor: '#ff6b6b',
      enabled: true,
      order: 6,
      routeName: 'ForeignTradeSettingsUsers'
    }
  ],
  // 快速链接
  quickLinks: [
    {
      name: '登录',
      enabled: true,
      order: 1,
      routeName: 'Login'
    },
    {
      name: '注册',
      enabled: true,
      order: 2,
      routeName: 'Register'
    }
  ]
}

export default Object.freeze(fastEnterConfig)
