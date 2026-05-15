import { AppRouteRecord } from '@/types/router'
import { foreignTradeRoutes } from './foreignTrade'
import { exceptionRoutes } from './exception'

/**
 * 导出所有模块化路由
 */
export const routeModules: AppRouteRecord[] = [
  foreignTradeRoutes,
  exceptionRoutes,
]
