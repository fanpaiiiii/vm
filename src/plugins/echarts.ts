/**
 * ECharts 插件配置 - 懒加载版本
 *
 * 使用动态导入按需加载 ECharts，减小初始打包体积。
 * echarts 核心库（~800KB）将被分离到独立 chunk，仅在图表初始化时加载。
 *
 * @module plugins/echarts
 * @author Art Design Pro Team
 */

// 缓存已加载的 echarts 实例
let echartsPromise: Promise<typeof import('echarts/core')> | null = null

/**
 * 懒加载 ECharts 核心模块
 * 首次调用时动态导入并注册所有需要的图表和组件，
 * 后续调用直接返回缓存的 Promise。
 */
export async function loadEcharts() {
  if (!echartsPromise) {
    echartsPromise = (async () => {
      const [echarts, chartsMod, componentsMod, renderersMod] = await Promise.all([
        import('echarts/core'),
        import('echarts/charts'),
        import('echarts/components'),
        import('echarts/renderers')
      ])

      echarts.use([
        // 图表类型
        chartsMod.BarChart,
        chartsMod.LineChart,
        chartsMod.PieChart,
        chartsMod.ScatterChart,
        chartsMod.RadarChart,
        chartsMod.MapChart,
        chartsMod.CandlestickChart,

        // 组件
        componentsMod.TitleComponent,
        componentsMod.TooltipComponent,
        componentsMod.GridComponent,
        componentsMod.LegendComponent,
        componentsMod.DataZoomComponent,
        componentsMod.MarkPointComponent,
        componentsMod.MarkLineComponent,
        componentsMod.ToolboxComponent,
        componentsMod.BrushComponent,
        componentsMod.GeoComponent,
        componentsMod.VisualMapComponent,

        // 渲染器
        renderersMod.CanvasRenderer
      ])

      return echarts
    })()
  }
  return echartsPromise
}

// Re-export types (these are type-only, no bundle impact)
export type { EChartsOption, BarSeriesOption } from 'echarts'
