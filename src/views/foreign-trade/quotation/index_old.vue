<template>
  <div class="quotation-generator">
    <!-- 编辑区域 -->
    <div v-show="!previewMode" class="edit-section">
      <!-- 公司信息 -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="card-header">
            <span>Company Information / 公司信息</span>
          </div>
        </template>
        <el-form :model="form.company" label-width="140px">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="Company Name">
                <el-input v-model="form.company.name" placeholder="e.g. Shaanxi Dinghan Meiyuan Trading Co., Ltd." />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="16">
              <el-form-item label="Address">
                <el-input v-model="form.company.address" placeholder="Full company address" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="TEL">
                <el-input v-model="form.company.tel" placeholder="Phone number" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Logo / 商标">
                <el-upload
                  :show-file-list="false"
                  :before-upload="handleLogoUpload"
                  accept="image/*"
                >
                  <el-button size="small" type="primary">
                    <el-icon><i class="ep-upload" /></el-icon>
                    Upload Logo
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">Right-top corner logo, supports PNG/JPG/SVG</div>
                  </template>
                </el-upload>
                <div v-if="form.company.logoUrl" class="logo-preview-thumb">
                  <img :src="form.company.logoUrl" alt="Logo Preview" />
                  <el-button type="danger" size="small" link @click="form.company.logoUrl = ''">
                    <el-icon><i class="ep-delete" /></el-icon> Remove
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- Quotation Info -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="card-header">
            <span>Quotation Details / 报价信息</span>
          </div>
        </template>
        <el-form :model="form" label-width="140px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="To (Buyer)">
                <el-input v-model="form.buyerName" placeholder="Buyer company / name" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Attn (Contact)">
                <el-input v-model="form.attn" placeholder="Contact person" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Quotation No.">
                <el-input v-model="form.quotationNo" placeholder="e.g. DHMY260508" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Dates">
                <el-date-picker v-model="form.dates" type="date" placeholder="Select date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Valid Dates">
                <el-input v-model="form.validDates" placeholder="e.g. 7days" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Currency">
                <el-select v-model="form.currency" style="width: 100%">
                  <el-option v-for="c in currencyOptions" :key="c.value" :label="c.label" :value="c.value" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Trade Terms">
                <el-select v-model="form.tradeTerms" style="width: 100%">
                  <el-option label="DDP" value="DDP" />
                  <el-option label="FOB" value="FOB" />
                  <el-option label="CIF" value="CIF" />
                  <el-option label="CFR" value="CFR" />
                  <el-option label="EXW" value="EXW" />
                  <el-option label="FCA" value="FCA" />
                  <el-option label="DDU" value="DDU" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- Product Groups -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="card-header">
            <span>Products / 产品明细</span>
            <el-button type="primary" size="small" @click="addGroup">
              <el-icon><i class="ep-plus" /></el-icon>
              Add Product Group
            </el-button>
          </div>
        </template>

        <div v-for="(group, gi) in form.groups" :key="gi" class="product-group">
          <div class="group-header">
            <div class="group-title">
              <span class="group-label">Product {{ gi + 1 }}：</span>
              <el-input v-model="group.productNo" placeholder="Product No. / name" size="small" style="width: 260px" />
              <el-input v-model="group.spec" placeholder="Spec (e.g. 180G26inch)" size="small" style="width: 200px; margin-left: 8px" />
              <el-upload
                :show-file-list="false"
                :before-upload="(file: File) => handleProductImageUpload(gi, file)"
                accept="image/*"
                style="margin-left: 8px"
              >
                <el-button size="small" type="primary" plain>
                  <el-icon><i class="ep-picture" /></el-icon>
                  Picture
                </el-button>
              </el-upload>
              <div v-if="group.imageUrl" class="group-img-thumb">
                <img :src="group.imageUrl" alt="Product" />
                <el-button type="danger" size="small" link @click="group.imageUrl = ''">
                  <el-icon><i class="ep-delete" /></el-icon>
                </el-button>
              </div>
            </div>
            <el-button type="danger" size="small" link @click="removeGroup(gi)" :disabled="form.groups.length <= 1">
              <el-icon><i class="ep-delete" /></el-icon>
            </el-button>
          </div>

          <el-table :data="group.items" border size="small" class="group-table">
            <el-table-column label="Size / Color" min-width="160">
              <template #default="{ row }">
                <el-input v-model="row.size" placeholder="e.g. color 33" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="Qty" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.qty" :min="1" :precision="0" size="small" controls-position="right" style="width: 100%" @change="calcRow(row)" />
              </template>
            </el-table-column>
            <el-table-column label="Unit Price" width="130">
              <template #default="{ row }">
                <el-input-number v-model="row.unitPrice" :min="0" :precision="2" size="small" controls-position="right" style="width: 100%" @change="calcRow(row)" />
              </template>
            </el-table-column>
            <el-table-column label="Total Amount" width="130" align="right">
              <template #default="{ row }">
                <span class="amount-text">{{ cSymbol }} {{ fmt(row.amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="" width="60" align="center">
              <template #default="{ $index }">
                <el-button type="danger" size="small" link @click="removeItem(gi, $index)" :disabled="group.items.length <= 1">
                  <el-icon><i class="ep-delete" /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="group-add-row">
            <el-button size="small" @click="addItem(gi)">
              <el-icon><i class="ep-plus" /></el-icon> Add Row
            </el-button>
            <span class="group-subtotal">Subtotal: {{ cSymbol }} {{ fmt(groupSubtotal(gi)) }}</span>
          </div>
        </div>
      </el-card>

      <!-- Shipping -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="card-header">
            <span>Shipping / 运费</span>
          </div>
        </template>
        <el-form :model="form.shipping" label-width="180px">
          <el-row :gutter="20">
            <el-col :span="16">
              <el-form-item label="Shipping Method">
                <el-input v-model="form.shipping.method" placeholder="e.g. Shipping cost by sea (lead time 55-60 workdays after shipping)" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Cost">
                <el-input-number v-model="form.shipping.cost" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- Actions -->
      <div class="action-bar">
        <el-button type="primary" size="large" @click="previewMode = true">
          <el-icon><i class="ep-view" /></el-icon>
          Preview / 预览
        </el-button>
        <el-button size="large" @click="handleReset">
          <el-icon><i class="ep-refresh" /></el-icon>
          Reset / 重置
        </el-button>
        <el-button size="large" @click="showSaveDialog = true">
          <el-icon><i class="ep-folder-checked" /></el-icon>
          Save Template / 保存模板
        </el-button>
        <el-button size="large" @click="loadTemplateList">
          <el-icon><i class="ep-folder-opened" /></el-icon>
          Load Template / 加载模板
        </el-button>
      </div>
    </div>

    <!-- Preview - 完全按照Excel模板样式 -->
    <div v-show="previewMode" class="preview-section">
      <div class="preview-actions no-print">
        <el-button type="primary" size="large" @click="handleExportPDF">
          <el-icon><i class="ep-printer" /></el-icon>
          Export PDF
        </el-button>
        <el-button type="success" size="large" @click="handleExportExcel">
          <el-icon><i class="ep-download" /></el-icon>
          Export Excel
        </el-button>
        <el-button size="large" @click="previewMode = false">
          <el-icon><i class="ep-edit" /></el-icon>
          Back to Edit
        </el-button>
      </div>

      <div class="quotation-preview" id="quotation-preview">
        <!-- Header: Logo (right) + Company info -->
        <div class="x-header-row">
          <div class="x-header-left">
            <!-- Row 1: Company Name -->
            <div class="x-company">{{ form.company.name || 'Company Name' }}</div>
            <!-- Row 2: Add: -->
            <div class="x-address">
              <span class="x-label">Add: </span>{{ form.company.address || '-' }}
            </div>
            <!-- Row 3: TEL: -->
            <div class="x-tel">
              <span class="x-label">TEL: </span>{{ form.company.tel || '-' }}
            </div>
          </div>
          <div class="x-header-right">
            <img v-if="form.company.logoUrl" :src="form.company.logoUrl" class="x-logo-img" alt="Company Logo" />
          </div>
        </div>

        <!-- Row 4: blank -->

        <!-- Row 5: Quotation (centered, full width, with bottom border) -->
        <div class="x-title">Quotation</div>

        <!-- Row 6: To: ___buyer___ | Quotation No.: ___no___ -->
        <div class="x-row-6">
          <div class="x-left">
            <span class="x-label">To: </span>
            <span class="x-underline">{{ form.buyerName || '________________' }}</span>
          </div>
          <div class="x-right">
            <span class="x-label">Quotation No.: </span>
            <span class="x-val">{{ form.quotationNo || '-' }}</span>
          </div>
        </div>

        <!-- Row 7: Attn: ___contact___ | Dates: ___date___ -->
        <div class="x-row-7">
          <div class="x-left">
            <span class="x-label">Attn: </span>
            <span class="x-underline">{{ form.attn || '________________' }}</span>
          </div>
          <div class="x-right">
            <span class="x-label">Dates: </span>
            <span class="x-val">{{ form.dates || '-' }}</span>
          </div>
        </div>

        <!-- Row 8: (blank left) | Valid dates: ___days___ -->
        <div class="x-row-8">
          <div class="x-left"></div>
          <div class="x-right">
            <span class="x-label">Valid dates: </span>
            <span class="x-val">{{ form.validDates || '-' }}</span>
          </div>
        </div>

        <!-- Row 9: Table Header -->
        <table class="x-table">
          <thead>
            <tr>
              <th class="x-col-no">No.</th>
              <th class="x-col-pno">product No.</th>
              <th class="x-col-pic">product picture</th>
              <th class="x-col-size">Size</th>
              <th class="x-col-qty">Qty</th>
              <th class="x-col-price">unit price</th>
              <th class="x-col-total">total amount</th>
            </tr>
          </thead>
          <tbody>
            <!-- Trade terms row -->
            <tr class="x-terms-row">
              <td colspan="7" class="x-terms-cell">{{ form.tradeTerms }} PRICE</td>
            </tr>

            <!-- Product groups -->
            <template v-for="(group, gi) in form.groups" :key="gi">
              <tr v-for="(item, ii) in group.items" :key="`${gi}-${ii}`" class="x-data-row">
                <!-- No. column: merged for group -->
                <td v-if="ii === 0" class="x-col-no center" :rowspan="group.items.length">{{ gi + 1 }}</td>
                <!-- Product No.: merged for group -->
                <td v-if="ii === 0" class="x-col-pno center" :rowspan="group.items.length">{{ group.productNo || '-' }}</td>
                <!-- Picture placeholder: merged for group -->
                <td v-if="ii === 0" class="x-col-pic center" :rowspan="group.items.length">
                  <img v-if="group.imageUrl" :src="group.imageUrl" class="x-product-img" alt="Product" />
                  <span v-else class="x-pic-placeholder">[Picture]</span>
                </td>
                <!-- Size / Color -->
                <td class="x-col-size">{{ item.size || '-' }}</td>
                <!-- Qty -->
                <td class="x-col-qty center">{{ item.qty }}</td>
                <!-- Unit Price -->
                <td class="x-col-price right">{{ fmt(item.unitPrice) }}</td>
                <!-- Total Amount -->
                <td class="x-col-total right">{{ fmt(item.amount) }}</td>
              </tr>
            </template>

            <!-- Shipping row -->
            <tr class="x-shipping-row">
              <td></td>
              <td colspan="5" class="x-shipping-label">{{ form.shipping.method || 'Shipping cost' }}</td>
              <td class="x-col-total right">{{ fmt(form.shipping.cost) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <!-- Total row -->
            <tr class="x-total-row">
              <td colspan="6" class="x-total-label">TOTAL AMOUNT({{ form.tradeTerms }}):</td>
              <td class="x-col-total right x-total-amount">{{ cSymbol }} {{ fmt(grandTotal) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Save Template Dialog -->
    <el-dialog v-model="showSaveDialog" title="Save Template / 保存模板" width="450px">
      <el-form label-width="100px">
        <el-form-item label="Name / 名称">
          <el-input v-model="saveForm.name" placeholder="Template name" />
        </el-form-item>
        <el-form-item label="Desc / 描述">
          <el-input v-model="saveForm.description" type="textarea" :rows="2" placeholder="Optional description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveTemplate" :loading="saving">Save / 保存</el-button>
      </template>
    </el-dialog>

    <!-- Load Template Dialog -->
    <el-dialog v-model="showLoadDialog" title="Load Template / 加载模板" width="600px">
      <div v-if="loadingTemplates" class="loading-box">
        <el-icon class="is-loading"><i class="ep-loading" /></el-icon>
        Loading...
      </div>
      <div v-else-if="templateList.length === 0" class="empty-box">
        No templates saved yet.
      </div>
      <div v-else class="template-list">
        <div
          v-for="t in templateList"
          :key="t.id"
          class="template-item"
          :class="{ selected: selectedTemplateId === t.id }"
          @click="selectedTemplateId = t.id"
        >
          <div class="template-info">
            <div class="template-name">{{ t.name }}</div>
            <div class="template-desc">{{ t.description || 'No description' }}</div>
            <div class="template-time">{{ t.updated_at?.slice(0, 16) }}</div>
          </div>
          <div class="template-actions">
            <el-button type="primary" size="small" @click.stop="handleLoadTemplate(t.id)">Load / 加载</el-button>
            <el-button type="danger" size="small" @click.stop="handleDeleteTemplate(t.id)">Delete / 删除</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

defineOptions({ name: 'ForeignTradeQuotation' })

const currencyOptions = [
  { value: 'USD', label: 'USD', symbol: '$' },
  { value: 'EUR', label: 'EUR', symbol: '€' },
  { value: 'GBP', label: 'GBP', symbol: '£' },
  { value: 'CNY', label: 'CNY', symbol: '¥' },
]

const previewMode = ref(false)

// Template management state
const showSaveDialog = ref(false)
const showLoadDialog = ref(false)
const saving = ref(false)
const loadingTemplates = ref(false)
const templateList = ref<any[]>([])
const selectedTemplateId = ref<number | null>(null)
const saveForm = reactive({ name: '', description: '' })

interface ProductItem {
  size: string
  qty: number
  unitPrice: number
  amount: number
}

interface ProductGroup {
  productNo: string
  spec: string
  items: ProductItem[]
  imageUrl: string
}

const newItem = (): ProductItem => ({ size: '', qty: 1, unitPrice: 0, amount: 0 })
const newGroup = (): ProductGroup => ({ productNo: '', spec: '', items: [newItem()], imageUrl: '' })

const form = reactive({
  company: { name: '', address: '', tel: '', logoUrl: '' },
  buyerName: '',
  attn: '',
  quotationNo: '',
  dates: '',
  validDates: '',
  currency: 'USD',
  tradeTerms: 'DDP',
  groups: [newGroup()] as ProductGroup[],
  shipping: { method: 'Shipping cost by sea (lead time 55-60 workdays after shipping)', cost: 0 },
})

const cSymbol = computed(() => currencyOptions.find(c => c.value === form.currency)?.symbol || '$')

const grandTotal = computed(() => {
  const productsTotal = form.groups.reduce((sum, g) => sum + g.items.reduce((s, i) => s + i.amount, 0), 0)
  return productsTotal + form.shipping.cost
})

function calcRow(row: ProductItem) {
  row.amount = Number((row.qty * row.unitPrice).toFixed(2))
}

function groupSubtotal(gi: number) {
  return form.groups[gi].items.reduce((s, i) => s + i.amount, 0)
}

function addGroup() {
  form.groups.push(newGroup())
}

function removeGroup(gi: number) {
  if (form.groups.length <= 1) return
  form.groups.splice(gi, 1)
}

function addItem(gi: number) {
  form.groups[gi].items.push(newItem())
}

function removeItem(gi: number, ii: number) {
  if (form.groups[gi].items.length <= 1) return
  form.groups[gi].items.splice(ii, 1)
}

function fmt(val: number): string {
  return val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function handleReset() {
  ElMessageBox.confirm('Reset all fields?', 'Confirm', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(() => {
    form.company = { name: '', address: '', tel: '', logoUrl: '' }
    form.buyerName = ''
    form.attn = ''
    form.quotationNo = ''
    form.dates = ''
    form.validDates = ''
    form.currency = 'USD'
    form.tradeTerms = 'DDP'
    form.groups = [newGroup()]
    form.shipping = { method: 'Shipping cost by sea (lead time 55-60 workdays after shipping)', cost: 0 }
    ElMessage.success('Reset complete')
  }).catch(() => {})
}

function handleExportPDF() {
  window.print()
}

function handleLogoUpload(file: File): boolean {
  const reader = new FileReader()
  reader.onload = (e) => {
    form.company.logoUrl = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false // prevent auto upload
}

function handleProductImageUpload(gi: number, file: File): boolean {
  const reader = new FileReader()
  reader.onload = (e) => {
    form.groups[gi].imageUrl = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false
}

async function handleExportExcel() {
  try {
    const resp = await fetch('/api/quotation/export/excel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company: form.company,
        buyerName: form.buyerName,
        attn: form.attn,
        quotationNo: form.quotationNo,
        dates: form.dates,
        validDates: form.validDates,
        currency: form.currency,
        tradeTerms: form.tradeTerms,
        groups: form.groups,
        shipping: form.shipping,
      })
    })
    if (!resp.ok) throw new Error('Export failed')
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Quotation_${form.quotationNo || 'draft'}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('Excel exported successfully')
  } catch {
    ElMessage.error('Export failed')
  }
}

async function handleSaveTemplate() {
  if (!saveForm.name.trim()) {
    ElMessage.warning('Please enter template name')
    return
  }
  saving.value = true
  try {
    const resp = await fetch('/api/quotation-templates/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: saveForm.name,
        description: saveForm.description,
        company: form.company,
        buyer_name: form.buyerName,
        attn: form.attn,
        quotation_no: form.quotationNo,
        dates: form.dates,
        valid_dates: form.validDates,
        currency: form.currency,
        trade_terms: form.tradeTerms,
        groups: form.groups,
        shipping: form.shipping,
      })
    })
    if (!resp.ok) throw new Error('Save failed')
    const data = await resp.json()
    ElMessage.success(`Template "${data.name}" saved`)
    showSaveDialog.value = false
    saveForm.name = ''
    saveForm.description = ''
  } catch {
    ElMessage.error('Failed to save template')
  } finally {
    saving.value = false
  }
}

async function loadTemplateList() {
  showLoadDialog.value = true
  loadingTemplates.value = true
  try {
    const resp = await fetch('/api/quotation-templates/')
    if (!resp.ok) throw new Error('Load failed')
    const data = await resp.json()
    templateList.value = data.items || []
  } catch {
    ElMessage.error('Failed to load templates')
    templateList.value = []
  } finally {
    loadingTemplates.value = false
  }
}

async function handleLoadTemplate(id: number) {
  try {
    const resp = await fetch(`/api/quotation-templates/${id}`)
    if (!resp.ok) throw new Error('Load failed')
    const t = await resp.json()
    // Apply template data to form
    form.company = t.company || { name: '', address: '', tel: '', logoUrl: '' }
    form.buyerName = t.buyer_name || ''
    form.attn = t.attn || ''
    form.quotationNo = t.quotation_no || ''
    form.dates = t.dates || ''
    form.validDates = t.valid_dates || ''
    form.currency = t.currency || 'USD'
    form.tradeTerms = t.trade_terms || 'DDP'
    form.groups = t.groups?.length ? t.groups : [newGroup()]
    form.shipping = t.shipping || { method: 'Shipping cost by sea', cost: 0 }
    showLoadDialog.value = false
    ElMessage.success(`Template "${t.name}" loaded`)
  } catch {
    ElMessage.error('Failed to load template')
  }
}

async function handleDeleteTemplate(id: number) {
  try {
    await ElMessageBox.confirm('Delete this template?', 'Confirm', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    })
    const resp = await fetch(`/api/quotation-templates/${id}`, { method: 'DELETE' })
    if (!resp.ok) throw new Error('Delete failed')
    templateList.value = templateList.value.filter(t => t.id !== id)
    ElMessage.success('Template deleted')
  } catch {
    // User cancelled or error
  }
}
</script>

<style scoped>
.quotation-generator { padding: 0; }
.mb-4 { margin-bottom: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 15px; }
.amount-text { font-weight: 600; color: var(--el-color-primary); }
.action-bar { display: flex; justify-content: center; gap: 16px; padding: 24px 0; }
.preview-actions { display: flex; justify-content: center; gap: 16px; padding: 16px 0; }

.product-group { margin-bottom: 16px; padding: 12px; border: 1px solid var(--el-border-color-lighter); border-radius: 6px; background: #fafafa; }
.group-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.group-title { display: flex; align-items: center; gap: 4px; }
.group-label { font-weight: 600; font-size: 14px; white-space: nowrap; }
.group-add-row { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.group-subtotal { font-weight: 600; font-size: 14px; color: var(--el-color-primary); }

/* ========== Preview: 完全按照Excel模板 ========== */
.quotation-preview {
  background: #fff;
  padding: 30px 40px;
  max-width: 900px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: Arial, 'Helvetica Neue', sans-serif;
  color: #000;
  font-size: 13px;
  line-height: 1.4;
  font-weight: 700;
}

/* Logo preview in edit form */
.logo-preview-thumb {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-preview-thumb img {
  height: 60px;
  max-width: 200px;
  object-fit: contain;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 4px;
}

/* Header row: company info left, logo right */
.x-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}
.x-header-left { flex: 1; }
.x-header-right {
  flex-shrink: 0;
  margin-left: 20px;
}
.x-logo-img {
  height: 80px;
  max-width: 180px;
  object-fit: contain;
}

/* Row 1: Company Name - large, centered, bold */
.x-company {
  text-align: left;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

/* Row 2: Add: address */
.x-address {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 2px;
}

/* Row 3: TEL: */
.x-tel {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 16px;
}

.x-label {
  font-weight: 700;
}

/* Row 5: Quotation title - centered, large, bottom border */
.x-title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 8px;
  padding-bottom: 8px;
  border-bottom: 2px solid #000;
  margin-bottom: 12px;
}

/* Rows 6-8: Reference info */
.x-row-6, .x-row-7, .x-row-8 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 4px;
  min-height: 22px;
}

.x-left {
  flex: 1;
}

.x-right {
  text-align: right;
  min-width: 280px;
}

.x-val {
  font-weight: 700;
}

.x-underline {
  font-weight: 700;
  border-bottom: 1px solid #000;
  padding: 0 8px;
  min-width: 120px;
  display: inline-block;
}

/* Product Table */
.x-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 13px;
  font-weight: 700;
}

.x-table th,
.x-table td {
  border: 1px solid #000;
  padding: 5px 8px;
}

.x-table th {
  text-align: center;
  font-weight: 700;
  font-size: 12px;
  background: #fff;
}

/* Column widths matching Excel */
.x-col-no { width: 40px; }
.x-col-pno { width: 100px; }
.x-col-pic { width: 140px; }
.x-col-size { width: 140px; }
.x-col-qty { width: 60px; }
.x-col-price { width: 100px; }
.x-col-total { width: 110px; }

.center { text-align: center; }
.right { text-align: right; }

/* Trade terms row */
.x-terms-row .x-terms-cell {
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 8px;
  background: #fff;
}

/* Data rows */
.x-data-row td {
  font-weight: 700;
}

/* Picture placeholder */
.x-pic-placeholder {
  color: #999;
  font-size: 11px;
  font-weight: 400;
}

/* Product image in preview table */
.x-product-img {
  max-width: 120px;
  max-height: 100px;
  object-fit: contain;
}

/* Group product image thumbnail in edit form */
.group-img-thumb {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
}
.group-img-thumb img {
  height: 40px;
  max-width: 80px;
  object-fit: contain;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 2px;
}

/* Group cells (merged) */
.x-table td[rowspan] {
  vertical-align: middle;
  text-align: center;
}

/* Shipping row */
.x-shipping-row .x-shipping-label {
  text-align: center;
  font-size: 14px;
  font-weight: 700;
}

/* Total row */
.x-total-row {
  border-top: 3px double #000;
}

.x-total-label {
  text-align: center;
  font-size: 16px;
  font-weight: 700;
}

.x-total-amount {
  font-size: 15px;
  font-weight: 700;
  color: #000;
}

/* Template list dialog */
.loading-box, .empty-box {
  text-align: center;
  padding: 40px;
  color: #999;
}
.template-list {
  max-height: 400px;
  overflow-y: auto;
}
.template-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.template-item:hover {
  background: var(--el-fill-color-light);
}
.template-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.template-info {
  flex: 1;
}
.template-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}
.template-desc {
  font-size: 12px;
  color: #666;
}
.template-time {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}
.template-actions {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}

@media print {
  .no-print { display: none !important; }
  .edit-section { display: none !important; }
  .preview-section { display: block !important; }
  .quotation-preview { border: none; padding: 15px 25px; max-width: 100%; box-shadow: none; }
  body { margin: 0; padding: 0; }
  @page { margin: 12mm; size: A4; }
}
</style>
