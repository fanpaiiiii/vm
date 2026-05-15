import { AppRouteRecord } from '@/types/router'

/**
 * 外贸工具路由配置
 */
export const foreignTradeRoutes: AppRouteRecord = {
  path: '/foreign-trade',
  name: 'ForeignTrade',
  redirect: '/foreign-trade/dashboard',
  component: '/index/index',
  meta: {
    title: 'menus.foreignTrade.title',
    icon: 'ep:goods',
  },
  children: [
    {
      path: 'dashboard',
      name: 'ForeignTradeDashboard',
      component: '/foreign-trade/dashboard',
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
          component: '/foreign-trade/products/list',
          meta: {
            title: 'menus.foreignTrade.productsList',
            icon: 'ep:list',
          },
        },
        {
          path: 'add',
          name: 'ForeignTradeProductsAdd',
          component: '/foreign-trade/products/add',
          meta: {
            title: 'menus.foreignTrade.productsAdd',
            icon: 'ep:plus',
          },
        },
        {
          path: 'edit/:id',
          name: 'ForeignTradeProductsEdit',
          component: '/foreign-trade/products/edit',
          meta: {
            title: 'menus.foreignTrade.productsEdit',
            icon: 'ep:edit',
            isHideMenu: true,
          },
        },
        {
          path: 'detail/:id',
          name: 'ForeignTradeProductsDetail',
          component: '/foreign-trade/products/detail',
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
          component: '/foreign-trade/suppliers/list',
          meta: {
            title: 'menus.foreignTrade.suppliersList',
            icon: 'ep:list',
          },
        },
        {
          path: 'add',
          name: 'ForeignTradeSuppliersAdd',
          component: '/foreign-trade/suppliers/add',
          meta: {
            title: 'menus.foreignTrade.suppliersAdd',
            icon: 'ep:plus',
          },
        },
        {
          path: 'edit/:id',
          name: 'ForeignTradeSuppliersEdit',
          component: '/foreign-trade/suppliers/edit',
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
      component: '/foreign-trade/shipping',
      meta: {
        title: 'menus.foreignTrade.shipping',
        icon: 'ep:van',
      },
    },
    {
      path: 'spreadsheet',
      name: 'ForeignTradeSpreadsheet',
      component: '/foreign-trade/spreadsheet',
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
          component: '/foreign-trade/settings/users',
          meta: {
            title: 'menus.foreignTrade.settingsUsers',
            icon: 'ep:user',
          },
        },
        {
          path: 'exchange-rate',
          name: 'ForeignTradeSettingsExchangeRate',
          component: '/foreign-trade/settings/exchange-rate',
          meta: {
            title: 'menus.foreignTrade.settingsExchangeRate',
            icon: 'ep:money',
          },
        },
        {
          path: 'shipping-channels',
          name: 'ForeignTradeSettingsShippingChannels',
          component: '/foreign-trade/settings/shipping-channels',
          meta: {
            title: 'menus.foreignTrade.settingsShippingChannels',
            icon: 'ep:ship',
          },
        },
      ],
    },
  ],
}
