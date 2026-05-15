import { AppRouteRecord } from '@/types/router'

/**
 * 外贸工具路由配置
 */
export const foreignTradeRoutes: AppRouteRecord = {
  path: '/foreign-trade',
  name: 'ForeignTrade',
  redirect: '/foreign-trade/dashboard',
  component: () => import('@views/index/index.vue'),
  meta: {
    title: 'menus.foreignTrade.title',
    icon: 'ep:goods',
  },
  children: [
    {
      path: 'dashboard',
      name: 'ForeignTradeDashboard',
      component: () => import('@views/foreign-trade/dashboard/index.vue'),
      meta: {
        title: 'menus.foreignTrade.dashboard',
        icon: 'ep:data-board',
      },
    },
    {
      path: 'products',
      name: 'ForeignTradeProducts',
      redirect: '/foreign-trade/products/list',
      meta: {
        title: 'menus.foreignTrade.products',
        icon: 'ep:shopping-bag',
      },
      children: [
        {
          path: 'list',
          name: 'ForeignTradeProductsList',
          component: () => import('@views/foreign-trade/products/list/index.vue'),
          meta: {
            title: 'menus.foreignTrade.productsList',
            icon: 'ep:list',
          },
        },
        {
          path: 'add',
          name: 'ForeignTradeProductsAdd',
          component: () => import('@views/foreign-trade/products/add/index.vue'),
          meta: {
            title: 'menus.foreignTrade.productsAdd',
            icon: 'ep:plus',
          },
        },
        {
          path: 'edit/:id',
          name: 'ForeignTradeProductsEdit',
          component: () => import('@views/foreign-trade/products/edit/index.vue'),
          meta: {
            title: 'menus.foreignTrade.productsEdit',
            icon: 'ep:edit',
            isHideMenu: true,
          },
        },
        {
          path: 'detail/:id',
          name: 'ForeignTradeProductsDetail',
          component: () => import('@views/foreign-trade/products/detail/index.vue'),
          meta: {
            title: 'menus.foreignTrade.productsDetail',
            icon: 'ep:view',
            isHideMenu: true,
          },
        },
      ],
    },
    {
      path: 'suppliers',
      name: 'ForeignTradeSuppliers',
      redirect: '/foreign-trade/suppliers/list',
      meta: {
        title: 'menus.foreignTrade.suppliers',
        icon: 'ep:office-building',
      },
      children: [
        {
          path: 'list',
          name: 'ForeignTradeSuppliersList',
          component: () => import('@views/foreign-trade/suppliers/list/index.vue'),
          meta: {
            title: 'menus.foreignTrade.suppliersList',
            icon: 'ep:list',
          },
        },
        {
          path: 'add',
          name: 'ForeignTradeSuppliersAdd',
          component: () => import('@views/foreign-trade/suppliers/add/index.vue'),
          meta: {
            title: 'menus.foreignTrade.suppliersAdd',
            icon: 'ep:plus',
          },
        },
        {
          path: 'edit/:id',
          name: 'ForeignTradeSuppliersEdit',
          component: () => import('@views/foreign-trade/suppliers/edit/index.vue'),
          meta: {
            title: 'menus.foreignTrade.suppliersEdit',
            icon: 'ep:edit',
            isHideMenu: true,
          },
        },
      ],
    },
    {
      path: 'shipping',
      name: 'ForeignTradeShipping',
      component: () => import('@views/foreign-trade/shipping/index.vue'),
      meta: {
        title: 'menus.foreignTrade.shipping',
        icon: 'ep:van',
      },
    },
    {
      path: 'spreadsheet',
      name: 'ForeignTradeSpreadsheet',
      component: () => import('@views/foreign-trade/spreadsheet/index.vue'),
      meta: {
        title: 'menus.foreignTrade.spreadsheet',
        icon: 'ep:document',
      },
    },
    {
      path: 'settings',
      name: 'ForeignTradeSettings',
      redirect: '/foreign-trade/settings/users',
      meta: {
        title: 'menus.foreignTrade.settings',
        icon: 'ep:setting',
      },
      children: [
        {
          path: 'users',
          name: 'ForeignTradeSettingsUsers',
          component: () => import('@views/foreign-trade/settings/users/index.vue'),
          meta: {
            title: 'menus.foreignTrade.settingsUsers',
            icon: 'ep:user',
          },
        },
        {
          path: 'exchange-rate',
          name: 'ForeignTradeSettingsExchangeRate',
          component: () => import('@views/foreign-trade/settings/exchange-rate/index.vue'),
          meta: {
            title: 'menus.foreignTrade.settingsExchangeRate',
            icon: 'ep:money',
          },
        },
        {
          path: 'shipping-channels',
          name: 'ForeignTradeSettingsShippingChannels',
          component: () => import('@views/foreign-trade/settings/shipping-channels/index.vue'),
          meta: {
            title: 'menus.foreignTrade.settingsShippingChannels',
            icon: 'ep:ship',
          },
        },
      ],
    },
  ],
}
