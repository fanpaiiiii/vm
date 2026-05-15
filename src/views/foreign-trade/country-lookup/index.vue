<template>
  <div class="country-lookup p-4 md:p-6">
    <!-- 搜索区域 - 高层级确保下拉不被遮挡 -->
    <div class="search-wrapper" :class="{ 'has-results': showDropdown && searchResults.length > 0 }">
      <el-card shadow="never" class="search-card">
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="输入国家名称、ISO代码、城市名或邮编（如：美国、US、Tokyo、10001）"
            size="large"
            clearable
            prefix-icon="Search"
            @input="onSearchInput"
            @clear="onClearSearch"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
          />
        </div>
      </el-card>

      <!-- 搜索下拉 - 固定定位，独立于文档流 -->
      <Transition name="dropdown">
        <div v-if="showDropdown && searchResults.length > 0" class="search-dropdown">
          <div class="dropdown-header">
            <span class="text-gray-400 text-sm">找到 {{ searchResults.length }} 个结果</span>
          </div>
          <div class="dropdown-list">
            <div
              v-for="(item, index) in searchResults"
              :key="item.iso2"
              class="search-item"
              :style="{ animationDelay: `${index * 30}ms` }"
              @mousedown.prevent="selectCountry(item.iso2)"
            >
              <span v-if="item.flag_emoji" class="text-xl mr-2">{{ item.flag_emoji }}</span>
              <div class="item-info">
                <span class="font-medium">{{ item.name_cn }}</span>
                <span class="text-gray-400 ml-2 text-sm">{{ item.name_en }}</span>
              </div>
              <el-tag size="small" class="ml-auto">{{ item.iso2 }}</el-tag>
              <el-tag size="small" type="info" class="ml-1">{{ item.region }}</el-tag>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 国家详情 -->
    <Transition name="fade-slide" mode="out-in">
      <el-card v-if="selectedCountry" key="detail" shadow="never" class="detail-card mb-4">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <Transition name="bounce" appear>
                <span v-if="detail.flag_emoji" class="flag-icon">{{ detail.flag_emoji }}</span>
              </Transition>
              <div>
                <h2 class="text-xl font-bold m-0">{{ detail.name_cn }}</h2>
                <p class="text-gray-400 text-sm m-0">{{ detail.name_en }} · {{ detail.iso2 }}/{{ detail.iso3 }}</p>
              </div>
              <Transition name="scale" appear>
                <el-tag v-if="detail.trade?.fta_with_china" type="success" effect="dark">中国FTA伙伴</el-tag>
              </Transition>
            </div>
            <el-button text @click="clearSelection" :icon="ArrowLeft">返回列表</el-button>
          </div>
        </template>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <!-- 物流信息 -->
          <el-tab-pane label="📦 物流信息" name="shipping">
            <Transition name="fade" mode="out-in">
              <div :key="'shipping-' + activeTab">
                <div v-if="detail.shipping?.available === false" class="empty-state">
                  <el-empty description="该地区暂无可用物流方式" />
                </div>
                <template v-else>
                  <el-table :data="detail.shipping?.methods || []" stripe border class="mb-4 animated-table">
                    <el-table-column prop="carrier" label="承运商" width="200">
                      <template #default="{ row }">
                        <span class="font-medium">{{ row.carrier }}</span>
                        <span class="text-gray-400 text-xs ml-1">({{ carrierLabel(row.carrier) }})</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="service" label="服务类型" min-width="150" />
                    <el-table-column label="时效(天)" width="120">
                      <template #default="{ row }">
                        <el-tag effect="plain" size="small">{{ row.days_min }}-{{ row.days_max }}天</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="费用等级" width="120">
                      <template #default="{ row }">
                        <el-tag :type="costTagType(row.cost)" size="small">{{ costLabel(row.cost) }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="追踪" width="80" align="center">
                      <template #default="{ row }">
                        <span v-if="row.tracking" class="text-green-500 text-lg">✓</span>
                        <span v-else class="text-gray-400 text-lg">✗</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="notes" label="备注" min-width="120" />
                    <el-table-column label="数据来源" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag v-if="row.source === 'manual'" type="success" size="small" effect="plain">手动</el-tag>
                        <el-tag v-else-if="row.source === 'api'" type="primary" size="small" effect="plain">API</el-tag>
                        <el-tag v-else type="info" size="small" effect="plain">估算</el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                  <el-descriptions :column="2" border size="small" class="animated-card mb-4">
                    <el-descriptions-item label="清关时间">{{ detail.shipping?.customs_clearance_days || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="偏远地区附加费">{{ detail.shipping?.remote_area_surcharge ? '是' : '否' }}</el-descriptions-item>
                  </el-descriptions>
                </template>

                <!-- 不可用物流方式（始终显示） -->
                <div v-if="detail.shipping?.unavailable_methods?.length" class="animated-card">
                    <h4 class="mb-2 flex items-center gap-2">
                      <span class="dot dot--red"></span> 不可用物流方式
                    </h4>
                    <div class="unavailable-list">
                      <div v-for="carrier in detail.shipping.unavailable_methods" :key="carrier" class="unavailable-item">
                        <span class="unavailable-icon">✗</span>
                        <span>{{ carrier }}</span>
                        <span class="text-gray-400 text-xs">({{ carrierLabel(carrier) }})</span>
                        <el-tag size="small" type="info" effect="plain" class="ml-2">暂不支持</el-tag>
                      </div>
                    </div>
                  </div>
              </div>
              
              <!-- 数据来源说明 -->
              <div class="data-source-note mt-4">
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>
                    <span class="text-sm">数据来源说明</span>
                  </template>
                  <template #default>
                    <div class="text-xs text-gray-500">
                      <p class="mb-1"><el-tag type="success" size="small" effect="plain">手动</el-tag> = 用户手动更新的数据</p>
                      <p class="mb-1"><el-tag type="primary" size="small" effect="plain">API</el-tag> = 来自承运商官方API</p>
                      <p><el-tag type="info" size="small" effect="plain">估算</el-tag> = 基于行业常识的估算值，仅供参考</p>
                      <p class="mt-2">最后更新: {{ detail.shipping?.last_updated || '未知' }}</p>
                    </div>
                  </template>
                </el-alert>
              </div>
            </Transition>
          </el-tab-pane>
          <el-tab-pane label="💰 贸易信息" name="trade">
            <Transition name="fade" mode="out-in">
              <div :key="'trade-' + activeTab">
                <el-descriptions :column="2" border class="mb-4 animated-card">
                  <el-descriptions-item label="平均关税">
                    <span class="text-lg font-bold text-orange-500">{{ detail.trade?.tariff_avg_pct }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="关税范围">{{ detail.trade?.tariff_range_pct }}</el-descriptions-item>
                  <el-descriptions-item label="增值税(VAT)">
                    <span class="text-lg font-bold text-blue-500">{{ detail.trade?.vat_pct }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="FTA与中国">
                    <el-tag v-if="detail.trade?.fta_with_china" type="success" effect="dark" size="small">是</el-tag>
                    <el-tag v-else type="info" size="small">否</el-tag>
                  </el-descriptions-item>
                </el-descriptions>

                <Transition name="slide-fade" appear>
                  <div v-if="detail.trade?.fta_details" class="info-box info-box--green mb-4">
                    <strong>自贸协定：</strong>{{ detail.trade.fta_details }}
                  </div>
                </Transition>

                <Transition name="slide-fade" appear>
                  <div v-if="detail.trade?.import_duties_notes" class="info-box info-box--blue mb-4">
                    <strong>关税说明：</strong>{{ detail.trade.import_duties_notes }}
                  </div>
                </Transition>

                <div class="mb-4 animated-card">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--blue"></span> 清关要求
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="item in (detail.trade?.customs_requirements || [])" :key="item" class="tag-item">{{ item }}</el-tag>
                    <span v-if="!detail.trade?.customs_requirements?.length" class="text-gray-400">暂无数据</span>
                  </div>
                </div>

                <div class="mb-4 animated-card">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--red"></span> 禁运商品
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="item in (detail.trade?.prohibited_items || [])" :key="item" type="danger" effect="dark" class="tag-item">{{ item }}</el-tag>
                    <span v-if="!detail.trade?.prohibited_items?.length" class="text-gray-400">暂无数据</span>
                  </div>
                </div>

                <div class="mb-4 animated-card">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--orange"></span> 限制商品
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="item in (detail.trade?.restricted_items || [])" :key="item" type="warning" class="tag-item">{{ item }}</el-tag>
                    <span v-if="!detail.trade?.restricted_items?.length" class="text-gray-400">暂无数据</span>
                  </div>
                </div>

                <div class="mb-4 animated-card">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--yellow"></span> 反倾销商品
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="item in (detail.trade?.anti_dumping || [])" :key="item" type="warning" effect="plain" class="tag-item">{{ item }}</el-tag>
                    <span v-if="!detail.trade?.anti_dumping?.length" class="text-gray-400">暂无数据</span>
                  </div>
                </div>

                <div class="mb-4 animated-card">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--green"></span> 所需单证
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="item in (detail.trade?.documentation || [])" :key="item" type="info" class="tag-item">{{ item }}</el-tag>
                  </div>
                </div>
              </div>
            </Transition>
          </el-tab-pane>

          <!-- 基础信息 -->
          <el-tab-pane label="🌍 基础信息" name="basic">
            <Transition name="fade" mode="out-in">
              <div :key="'basic-' + activeTab">
                <el-descriptions :column="2" border class="mb-4 animated-card">
                  <el-descriptions-item label="首都">
                    <span class="font-medium">{{ detail.capital }}</span> ({{ detail.capital_en }})
                  </el-descriptions-item>
                  <el-descriptions-item label="地区">{{ detail.region }} · {{ detail.subregion }}</el-descriptions-item>
                  <el-descriptions-item label="货币">{{ detail.currency }} ({{ detail.currency_name }})</el-descriptions-item>
                  <el-descriptions-item label="国际电话">{{ detail.phone_code }}</el-descriptions-item>
                  <el-descriptions-item label="域名">{{ detail.tld || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="语言">{{ (detail.languages || []).join(', ') || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="电压/频率">{{ detail.voltage || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="插座类型">{{ detail.plug_type || '-' }}</el-descriptions-item>
                </el-descriptions>

                <div class="mb-4 animated-card" v-if="detail.business?.major_cities?.length">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--purple"></span> 主要城市
                  </h4>
                  <div class="tag-list">
                    <el-tag
                      v-for="city in detail.business.major_cities"
                      :key="city"
                      class="tag-item clickable-tag"
                      @click="searchByCity(city)"
                    >{{ city }}</el-tag>
                  </div>
                </div>

                <div class="mb-4 animated-card" v-if="detail.business?.major_ports?.length">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--blue"></span> 主要港口
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="port in detail.business.major_ports" :key="port" type="primary" class="tag-item">{{ port }}</el-tag>
                  </div>
                </div>

                <div class="mb-4 animated-card" v-if="detail.business?.payment_methods?.length">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--green"></span> 支付方式
                  </h4>
                  <div class="tag-list">
                    <el-tag v-for="pm in detail.business.payment_methods" :key="pm" type="success" effect="plain" class="tag-item">{{ pm }}</el-tag>
                  </div>
                </div>

                <div class="mb-4 animated-card" v-if="detail.business?.business_language">
                  <h4 class="mb-2">商务语言</h4>
                  <span>{{ detail.business.business_language }}</span>
                </div>

                <div class="mb-4 animated-card" v-if="detail.borders?.length">
                  <h4 class="mb-2 flex items-center gap-2">
                    <span class="dot dot--orange"></span> 邻国
                  </h4>
                  <div class="tag-list">
                    <el-tag
                      v-for="b in detail.borders"
                      :key="b"
                      class="tag-item clickable-tag"
                      @click="selectCountry(b)"
                    >{{ b }} →</el-tag>
                  </div>
                </div>

                <div v-if="detail.maps_url" class="mt-4">
                  <el-button type="primary" plain @click="openMaps" :icon="MapLocation">在 Google Maps 中查看</el-button>
                </div>
              </div>
            </Transition>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- 所有国家列表 -->
      <el-card v-else key="list" shadow="never" class="list-card">
        <template #header>
          <div class="flex items-center justify-between flex-wrap gap-2">
            <h3 class="m-0">全球国家/地区 ({{ filteredCountries.length }})</h3>
            <div class="flex items-center gap-2">
              <el-segmented v-model="regionFilter" :options="regionOptions" size="small" />
              <el-input v-model="tableFilter" placeholder="筛选国家..." clearable style="width:200px" size="small" />
            </div>
          </div>
        </template>
        <el-table
          :data="paginatedCountries"
          stripe
          border
          v-loading="loading"
          @row-click="(row: any) => selectCountry(row.iso2)"
          class="country-table"
          row-class-name="country-row"
        >
          <el-table-column prop="name_cn" label="国家/地区" min-width="120">
            <template #default="{ row }">
              <div class="flex items-center gap-2">
                <span v-if="row.flag_emoji" class="text-lg">{{ row.flag_emoji }}</span>
                <span class="font-medium text-blue-600 cursor-pointer hover:text-blue-800 transition-colors">{{ row.name_cn }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="name_en" label="英文名" min-width="140" />
          <el-table-column prop="iso2" label="ISO" width="70">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.iso2 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="region" label="地区" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="regionTagType(row.region)">{{ row.region }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="capital" label="首都" width="120" />
          <el-table-column prop="currency" label="货币" width="80" />
          <el-table-column prop="phone_code" label="区号" width="80" />
          <el-table-column label="FTA" width="70" align="center">
            <template #default="{ row }">
              <span v-if="row.fta_with_china" class="text-green-500 font-bold">✓</span>
              <span v-else class="text-gray-300">-</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="flex justify-center mt-4">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="filteredCountries.length"
            layout="prev, pager, next, total"
            background
          />
        </div>
      </el-card>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, MapLocation } from '@element-plus/icons-vue'
import { fetchCountrySearch, fetchCountryDetail, fetchAllCountries } from '@/api/foreign-trade/country'

// State
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const showDropdown = ref(false)
const searchFocused = ref(false)
const selectedCountry = ref('')
const detail = ref<any>({})
const activeTab = ref('shipping')
const allCountries = ref<any[]>([])
const loading = ref(false)
const tableFilter = ref('')
const currentPage = ref(1)
const pageSize = 50
const regionFilter = ref('全部')

import { useDebounceFn } from '@vueuse/core'

const regionOptions = computed(() => {
  const regions = new Set<string>(allCountries.value.map((c: any) => c.region).filter(Boolean))
  return ['全部', ...Array.from(regions).sort()]
})

// Load all countries on mount
onMounted(async () => {
  loading.value = true
  try {
    const res = await fetchAllCountries()
    allCountries.value = (res as any)?.countries || []
  } catch (e) {
    console.error('Failed to load countries:', e)
  } finally {
    loading.value = false
  }
})

// Filtered countries for table
const filteredCountries = computed(() => {
  let list = allCountries.value
  if (regionFilter.value && regionFilter.value !== '全部') {
    list = list.filter((c: any) => c.region === regionFilter.value)
  }
  if (tableFilter.value) {
    const q = tableFilter.value.toLowerCase()
    list = list.filter(
      (c: any) =>
        c.name_cn?.toLowerCase().includes(q) ||
        c.name_en?.toLowerCase().includes(q) ||
        c.iso2?.toLowerCase().includes(q) ||
        c.capital?.toLowerCase().includes(q)
    )
  }
  return list
})

// Paginated countries
const paginatedCountries = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredCountries.value.slice(start, start + pageSize)
})

const doSearch = useDebounceFn(async (val: string) => {
  try {
    const res = await fetchCountrySearch(val)
    searchResults.value = (res as any)?.results || []
    showDropdown.value = searchResults.value.length > 0
  } catch {
    searchResults.value = []
  }
}, 300)

function onSearchInput(val: string) {
  if (!val || val.length < 1) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  doSearch(val)
}

function onClearSearch() {
  searchResults.value = []
  showDropdown.value = false
}

function onSearchFocus() {
  searchFocused.value = true
  if (searchResults.value.length > 0) {
    showDropdown.value = true
  }
}

function onSearchBlur() {
  searchFocused.value = false
  // Delay hide so click on dropdown item can fire
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

async function selectCountry(iso2: string) {
  showDropdown.value = false
  selectedCountry.value = iso2
  activeTab.value = 'shipping'
  loading.value = true
  try {
    const res = await fetchCountryDetail(iso2)
    detail.value = res || {}
  } catch (e) {
    console.error('Failed to load country detail:', e)
    detail.value = {}
  } finally {
    loading.value = false
  }
}

function clearSelection() {
  selectedCountry.value = ''
  detail.value = {}
  searchQuery.value = ''
}

function searchByCity(city: string) {
  searchQuery.value = city
  onSearchInput(city)
}

function openMaps() {
  if (detail.value.maps_url) {
    window.open(detail.value.maps_url, '_blank')
  }
}

// Region tag color
function regionTagType(region: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    '亚洲': 'warning',
    '欧洲': 'info',
    '非洲': 'danger',
    '北美洲': 'success',
    '南美洲': 'success',
    '大洋洲': 'info',
    '南极洲': 'info',
  }
  return map[region] || 'info'
}

// Cost level helpers
function costTagType(cost: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    very_low: 'success',
    low: 'success',
    medium: 'warning',
    high: 'danger',
    very_high: 'danger',
  }
  return (map[cost] || 'info') as any
}

function costLabel(cost: string) {
  const map: Record<string, string> = {
    very_low: '极低',
    low: '低',
    medium: '中等',
    high: '高',
    very_high: '极高',
  }
  return map[cost] || cost
}

// 承运商中文名映射
const CARRIER_NAMES: Record<string, string> = {
  DHL: 'DHL国际快递',
  FedEx: '联邦快递',
  UPS: 'UPS快递',
  EMS: '邮政特快(EMS)',
  ePacket: 'e邮宝',
  '海运': '国际海运',
  '铁路': '中欧铁路',
}

function carrierLabel(carrier: string) {
  return CARRIER_NAMES[carrier] || carrier
}
</script>

<style scoped>
.country-lookup {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

/* === 搜索区域层级修复 === */
.search-wrapper {
  position: relative;
  z-index: 1000; /* 远高于下方卡片 */
  margin-bottom: 1rem;
}

.search-card {
  position: relative;
  z-index: 1001;
}

.search-section {
  position: relative;
}

/* === 搜索下拉 - 高层级 + 独立定位 === */
.search-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 2000;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06);
  max-height: 420px;
  overflow: hidden;
}

.dropdown-header {
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.dropdown-list {
  max-height: 380px;
  overflow-y: auto;
}

.search-item {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.15s, transform 0.15s;
  animation: itemSlideIn 0.2s ease-out both;
}

.search-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.search-item:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
  min-width: 0;
}

/* === 下拉动画 === */
.dropdown-enter-active {
  animation: dropdownIn 0.2s ease-out;
}
.dropdown-leave-active {
  animation: dropdownOut 0.15s ease-in;
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scaleY(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scaleY(1);
  }
}

@keyframes dropdownOut {
  from {
    opacity: 1;
    transform: translateY(0) scaleY(1);
  }
  to {
    opacity: 0;
    transform: translateY(-8px) scaleY(0.95);
  }
}

@keyframes itemSlideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* === 页面切换动画 === */
.fade-slide-enter-active {
  animation: fadeSlideIn 0.35s ease-out;
}
.fade-slide-leave-active {
  animation: fadeSlideOut 0.2s ease-in;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeSlideOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* === 内容淡入 === */
.fade-enter-active {
  transition: opacity 0.25s ease;
}
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* === 滑入淡出 === */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  transform: translateY(10px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* === 国旗弹入 === */
.bounce-enter-active {
  animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounceIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* === 标签弹入 === */
.scale-enter-active {
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* === 国旗图标 === */
.flag-icon {
  font-size: 2.5rem;
  line-height: 1;
  display: inline-block;
}

/* === 详情卡片 === */
.detail-card {
  animation: cardEnter 0.3s ease-out;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* === 信息框 === */
.info-box {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  border-left: 4px solid;
}

.info-box--green {
  background: #f0f9ff;
  border-color: #67c23a;
  color: #529a2e;
}

.info-box--blue {
  background: #f0f7ff;
  border-color: #409eff;
  color: #337ecc;
}

/* === 彩色圆点指示器 === */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.dot--blue { background: #409eff; }
.dot--red { background: #f56c6c; }
.dot--orange { background: #e6a23c; }
.dot--yellow { background: #f5c542; }
.dot--green { background: #67c23a; }
.dot--purple { background: #9b59b6; }

/* === 标签列表 === */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  transition: transform 0.15s;
}
.tag-item:hover {
  transform: scale(1.05);
}

.clickable-tag {
  cursor: pointer;
  transition: all 0.2s;
}
.clickable-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* === 不可用物流方式 === */
.unavailable-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.unavailable-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 6px;
  font-size: 13px;
  color: #909399;
  transition: all 0.2s;
}

.unavailable-item:hover {
  background: #fde2e2;
  transform: translateY(-1px);
}

.unavailable-icon {
  color: #f56c6c;
  font-weight: bold;
  font-size: 14px;
}

/* === 空状态 === */
.empty-state {
  padding: 40px 0;
}

/* === 数据来源说明 === */
.data-source-note {
  margin-top: 16px;
}
.data-source-note .el-alert {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
}

/* === 表格行交互 === */
:deep(.country-row) {
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
:deep(.country-row:hover td) {
  background: #ecf5ff !important;
}

/* === 分页 === */
:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
}

/* === Tabs 样式 === */
.detail-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.detail-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

/* === 描述列表标签宽度 === */
:deep(.el-descriptions__label) {
  width: 120px;
}

/* === 响应式 === */
@media (max-width: 768px) {
  .country-lookup {
    padding: 0.5rem;
  }
  .search-dropdown {
    max-height: 300px;
  }
  .flag-icon {
    font-size: 2rem;
  }
}
</style>
