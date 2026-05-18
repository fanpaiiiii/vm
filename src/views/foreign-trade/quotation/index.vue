<template>
  <div class="qm">
    <!-- Top Bar -->
    <div class="topbar">
      <div class="topbar-inner">
        <div class="topbar-left">
          <div class="brand">
            <el-icon :size="20"><i class="ep-document-checked" /></el-icon>
            <span>Quotation Maker</span>
          </div>
          <el-divider direction="vertical" />
          <el-select v-model="templateStyle" size="small" class="style-select">
            <el-option label="Classic" value="classic" />
            <el-option label="Modern" value="modern" />
            <el-option label="Minimal" value="minimal" />
          </el-select>
        </div>
        <div class="topbar-right">
          <el-dropdown @command="handleTpl" trigger="click">
            <el-button size="small" text>
              <el-icon><i class="ep-folder" /></el-icon> Templates
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="save">Save Template</el-dropdown-item>
                <el-dropdown-item command="load">Load Template</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button size="small" text @click="exportPDF">
            <el-icon><i class="ep-printer" /></el-icon> PDF
          </el-button>
          <el-button size="small" text type="success" @click="exportExcel">
            <el-icon><i class="ep-download" /></el-icon> Excel
          </el-button>
          <el-upload :show-file-list="false" :before-upload="importExcel" accept=".xlsx,.xls">
            <el-button size="small" text type="warning">
              <el-icon><i class="ep-upload" /></el-icon> Import
            </el-button>
          </el-upload>
        </div>
      </div>
    </div>

    <!-- Main -->
    <div class="main">
      <!-- Sidebar -->
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><i :class="sidebarCollapsed ? 'ep-arrow-right' : 'ep-arrow-left'" /></el-icon>
        </div>
        <div class="sidebar-content" v-show="!sidebarCollapsed">
          <div class="sidebar-title">Settings</div>
          <div class="sg">
            <label>Currency</label>
            <el-select v-model="form.currency" size="small" class="w-full">
              <el-option v-for="(sym, cur) in currencies" :key="cur" :label="`${cur} (${sym})`" :value="cur" />
            </el-select>
          </div>
          <div class="sg">
            <label>Trade Terms</label>
            <el-select v-model="form.tradeTerms" size="small" class="w-full">
              <el-option label="DDP" value="DDP" />
              <el-option label="FOB" value="FOB" />
              <el-option label="CIF" value="CIF" />
              <el-option label="EXW" value="EXW" />
              <el-option label="DDU" value="DDU" />
            </el-select>
          </div>
          <el-divider />
          <div class="sg">
            <label>Company Logo</label>
            <div class="logo-box" @click="triggerLogo">
              <img v-if="form.company.logo" :src="form.company.logo" class="logo-preview" />
              <div v-else class="logo-add"><el-icon :size="20"><i class="ep-plus" /></el-icon><span>Upload</span></div>
            </div>
            <input ref="logoInput" type="file" accept="image/*" hidden @change="onLogo" />
          </div>
          <el-divider />
          <div class="sg">
            <label>Notes</label>
            <el-input v-model="form.notes" type="textarea" :rows="3" size="small" placeholder="Payment terms..." />
          </div>
          <div class="sg">
            <label>Bank</label>
            <el-input v-model="form.bank" size="small" placeholder="Bank Name" class="mb-8" />
            <el-input v-model="form.account" size="small" placeholder="Account" class="mb-8" />
            <el-input v-model="form.swift" size="small" placeholder="SWIFT" />
          </div>
        </div>
      </div>

      <!-- Paper -->
      <div class="paper-wrap">
        <div :class="['paper', `style-${templateStyle}`]" id="invoice-paper">
          <!-- Header -->
          <div class="hdr">
            <div class="hdr-left">
              <img v-if="form.company.logo" :src="form.company.logo" class="hdr-logo" />
              <div class="hdr-company">
                <div class="hc-name" contenteditable @blur="form.company.name = getText($event)">{{ form.company.name || 'Company Name' }}</div>
                <div class="hc-addr" contenteditable @blur="form.company.address = getText($event)">{{ form.company.address || 'Address' }}</div>
                <div class="hc-tel" contenteditable @blur="form.company.tel = getText($event)">{{ form.company.tel || 'TEL' }}</div>
              </div>
            </div>
            <div class="hdr-right">
              <div class="hdr-title" contenteditable @blur="form.title = getText($event)">{{ form.title }}</div>
            </div>
          </div>
          <div class="line"></div>

          <!-- Meta -->
          <div class="meta">
            <div class="meta-buyer">
              <div class="meta-sec">Bill To</div>
              <div class="mf"><span class="ml">Company</span><span class="mv" contenteditable @blur="form.buyerName = getText($event)">{{ form.buyerName || 'Client' }}</span></div>
              <div class="mf"><span class="ml">Contact</span><span class="mv" contenteditable @blur="form.attn = getText($event)">{{ form.attn || 'Contact' }}</span></div>
              <div class="mf"><span class="ml">Address</span><span class="mv" contenteditable @blur="form.buyerAddress = getText($event)">{{ form.buyerAddress || 'Address' }}</span></div>
            </div>
            <div class="meta-doc">
              <div class="mdr"><span class="mdl">No.</span><span class="mdv" contenteditable @blur="form.quotationNo = getText($event)">{{ form.quotationNo || 'QT-001' }}</span></div>
              <div class="mdr"><span class="mdl">Date</span><input type="date" v-model="form.dates" class="mdi" /></div>
              <div class="mdr"><span class="mdl">Valid</span><input type="date" v-model="form.validDates" class="mdi" /></div>
              <div class="mdr"><span class="mdl">Terms</span><span class="mdv hl">{{ form.tradeTerms }}</span></div>
            </div>
          </div>

          <!-- Product Groups -->
          <div class="groups">
            <div v-for="(group, gi) in form.groups" :key="gi" class="group">
              <div class="gh">
                <div class="gh-left">
                  <span class="g-badge">{{ gi + 1 }}</span>
                  <input v-model="group.productNo" class="g-pno" placeholder="Product No." />
                  <input v-model="group.productName" class="g-pname" placeholder="Product Name" />
                </div>
                <div class="gh-right">
                  <div class="g-photo" @click="triggerGroupImg(gi)">
                    <img v-if="group.image" :src="group.image" class="g-photo-img" />
                    <span v-else class="g-photo-add"><el-icon><i class="ep-camera" /></el-icon></span>
                  </div>
                  <input :ref="(el: any) => { if(el) gImgRefs[gi] = el }" type="file" accept="image/*" hidden @change="(e: Event) => onGroupImg(gi, e)" />
                  <el-button v-if="form.groups.length > 1" type="danger" text size="small" @click="removeGroup(gi)"><el-icon><i class="ep-delete" /></el-icon></el-button>
                </div>
              </div>

              <!-- Table -->
              <table class="vt">
                <thead>
                  <tr>
                    <th class="vw-idx">#</th>
                    <th v-for="col in group.columns" :key="col.key"><input v-model="col.label" class="th-inp" /></th>
                    <th class="vw-qty">Qty</th>
                    <th class="vw-price">Price</th>
                    <th class="vw-amt">Amount</th>
                    <th class="vw-act"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in group.rows" :key="ri">
                    <td class="vw-idx">{{ ri + 1 }}</td>
                    <td v-for="col in group.columns" :key="col.key"><input v-model="row[col.key]" class="vc" /></td>
                    <td class="vw-qty"><input v-model.number="row.qty" type="number" min="1" class="vc ctr" @input="calcRow(gi, ri)" /></td>
                    <td class="vw-price"><input v-model.number="row.price" type="number" step="0.01" class="vc rgt" @input="calcRow(gi, ri)" /></td>
                    <td class="vw-amt rgt">{{ cSym }}{{ fmt(row.amount) }}</td>
                    <td class="vw-act"><el-button v-if="group.rows.length > 1" type="danger" text size="small" @click="removeRow(gi, ri)"><el-icon><i class="ep-close" /></el-icon></el-button></td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="sub">
                    <td :colspan="2 + group.columns.length" class="rgt"><span class="sub-lbl">Subtotal ({{ groupQty(gi) }} pcs)</span></td>
                    <td class="vw-qty ctr">{{ groupQty(gi) }}</td>
                    <td></td>
                    <td class="vw-amt rgt bold">{{ cSym }}{{ fmt(groupTotal(gi)) }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>

              <div class="g-acts">
                <el-button text size="small" @click="addRow(gi)"><el-icon><i class="ep-plus" /></el-icon> Row</el-button>
                <el-dropdown @command="(cmd: string) => addCol(gi, cmd)" trigger="click">
                  <el-button text size="small"><el-icon><i class="ep-grid" /></el-icon> Column</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="color">Color</el-dropdown-item>
                      <el-dropdown-item command="size">Size</el-dropdown-item>
                      <el-dropdown-item command="material">Material</el-dropdown-item>
                      <el-dropdown-item command="custom" divided>Custom...</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <div class="add-prod" @click="addGroup">
              <el-icon :size="18"><i class="ep-plus" /></el-icon> Add Product
            </div>
          </div>

          <!-- Summary -->
          <div class="summary">
            <div></div>
            <div class="sum-right">
              <div class="sum-row"><span>Subtotal</span><span>{{ cSym }}{{ fmt(productsTotal) }}</span></div>
              <div class="sum-row">
                <input v-model="form.shipping.label" class="sum-inp" placeholder="Shipping" />
                <input v-model.number="form.shipping.cost" type="number" step="0.01" class="sum-inp rgt" />
              </div>
              <div class="sum-row total"><span>TOTAL ({{ form.tradeTerms }})</span><span>{{ cSym }}{{ fmt(grandTotal) }}</span></div>
            </div>
          </div>

          <!-- Footer -->
          <div class="ftr">
            <div><span class="fk">Bank:</span> <span contenteditable @blur="form.bank = getText($event)">{{ form.bank || 'Bank' }}</span></div>
            <div><span class="fk">Account:</span> <span contenteditable @blur="form.account = getText($event)">{{ form.account || 'Account' }}</span></div>
            <div><span class="fk">SWIFT:</span> <span contenteditable @blur="form.swift = getText($event)">{{ form.swift || 'SWIFT' }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialogs -->
    <el-dialog v-model="showSave" title="Save Template" width="400px">
      <el-form label-width="80px">
        <el-form-item label="Name"><el-input v-model="tplName" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSave = false">Cancel</el-button>
        <el-button type="primary" @click="doSave">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showLoad" title="Load Template" width="500px">
      <div v-if="tplLoading" class="tpl-st">Loading...</div>
      <div v-else-if="tplList.length === 0" class="tpl-st">No templates</div>
      <div v-else class="tpl-list">
        <div v-for="t in tplList" :key="t.id" class="tpl-item" @click="doLoad(t.id)">
          <div><div class="tpl-n">{{ t.name }}</div><div class="tpl-d">{{ t.updated_at?.slice(0, 10) }}</div></div>
          <el-button type="danger" text size="small" @click.stop="doDelete(t.id)"><el-icon><i class="ep-delete" /></el-icon></el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showColDlg" title="Add Column" width="300px">
      <el-input v-model="colName" placeholder="Column name" @keyup.enter="confirmCol" />
      <template #footer>
        <el-button @click="showColDlg = false">Cancel</el-button>
        <el-button type="primary" @click="confirmCol">Add</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

defineOptions({ name: 'QuotationMaker' })

// Helper
function getText(e: Event): string {
  return (e.target as HTMLElement).textContent || ''
}

const currencies: Record<string, string> = { USD: '$', EUR: '€', GBP: '£', CNY: '¥' }
const cSym = computed(() => currencies[form.currency] || '$')

const sidebarCollapsed = ref(false)
const templateStyle = ref('classic')

// Types
interface Column { key: string; label: string; default: string }
interface Row { qty: number; price: number; amount: number; [k: string]: any }
interface Group { productNo: string; productName: string; image: string; columns: Column[]; rows: Row[] }

function makeRow(cols: Column[]): Row {
  const r: any = { qty: 1, price: 0, amount: 0 }
  cols.forEach(c => { r[c.key] = '' })
  return r
}

function defaultGroup(): Group {
  const cols = [{ key: 'color', label: 'Color', default: 'Color' }, { key: 'size', label: 'Size', default: 'Size' }]
  return { productNo: '', productName: '', image: '', columns: cols, rows: [makeRow(cols)] }
}

const form = reactive({
  title: 'QUOTATION',
  company: { name: '', address: '', tel: '', logo: '' },
  buyerName: '', buyerAddress: '', attn: '',
  quotationNo: '', dates: '', validDates: '',
  currency: 'USD', tradeTerms: 'DDP',
  groups: [defaultGroup()] as Group[],
  shipping: { label: 'Shipping', cost: 0 },
  notes: '', bank: '', account: '', swift: '',
})

// Calculations
function calcRow(gi: number, ri: number) {
  const r = form.groups[gi].rows[ri]
  r.amount = Number(((r.qty || 0) * (r.price || 0)).toFixed(2))
}
function groupTotal(gi: number) { return form.groups[gi].rows.reduce((s, r) => s + r.amount, 0) }
function groupQty(gi: number) { return form.groups[gi].rows.reduce((s, r) => s + (r.qty || 0), 0) }
const productsTotal = computed(() => form.groups.reduce((s, _, i) => s + groupTotal(i), 0))
const grandTotal = computed(() => productsTotal.value + (form.shipping.cost || 0))
function fmt(v: number) { return v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }

// Group ops
function addGroup() { form.groups.push(defaultGroup()) }
function removeGroup(gi: number) { if (form.groups.length > 1) form.groups.splice(gi, 1) }
function addRow(gi: number) { form.groups[gi].rows.push(makeRow(form.groups[gi].columns)) }
function removeRow(gi: number, ri: number) { if (form.groups[gi].rows.length > 1) form.groups[gi].rows.splice(ri, 1) }

// Column ops
const showColDlg = ref(false)
const colName = ref('')
const pendingGi = ref(-1)
const presets: Record<string, Column> = {
  color: { key: 'color', label: 'Color', default: 'Color' },
  size: { key: 'size', label: 'Size', default: 'Size' },
  material: { key: 'material', label: 'Material', default: 'Material' },
}

function addCol(gi: number, cmd: string) {
  if (cmd === 'custom') { pendingGi.value = gi; colName.value = ''; showColDlg.value = true; return }
  const p = presets[cmd]
  if (!p) return
  const g = form.groups[gi]
  if (g.columns.find(c => c.key === p.key)) return ElMessage.warning('Exists')
  g.columns.push({ ...p })
  g.rows.forEach(r => { r[p.key] = '' })
}

function confirmCol() {
  const name = colName.value.trim()
  if (!name) return
  const key = name.toLowerCase().replace(/\s+/g, '_')
  form.groups[pendingGi.value].columns.push({ key, label: name, default: name })
  form.groups[pendingGi.value].rows.forEach(r => { r[key] = '' })
  showColDlg.value = false
}

// Image uploads
const logoInput = ref<HTMLInputElement>()
function triggerLogo() { logoInput.value?.click() }
function onLogo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { form.company.logo = ev.target?.result as string }
  reader.readAsDataURL(file)
}

const gImgRefs: Record<number, HTMLInputElement> = {}
function triggerGroupImg(gi: number) { gImgRefs[gi]?.click() }
function onGroupImg(gi: number, e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { form.groups[gi].image = ev.target?.result as string }
  reader.readAsDataURL(file)
}

// Templates
const showSave = ref(false)
const showLoad = ref(false)
const tplName = ref('')
const tplLoading = ref(false)
const tplList = ref<any[]>([])

function handleTpl(cmd: string) {
  if (cmd === 'save') showSave.value = true
  if (cmd === 'load') { showLoad.value = true; fetchTpl() }
}

async function fetchTpl() {
  tplLoading.value = true
  try { const r = await fetch('/api/quotation-templates/'); const d = await r.json(); tplList.value = d.items || [] }
  catch { tplList.value = [] } finally { tplLoading.value = false }
}

async function doSave() {
  if (!tplName.value.trim()) return ElMessage.warning('Enter name')
  try {
    await fetch('/api/quotation-templates/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: tplName.value, company: form.company, buyer_name: form.buyerName, attn: form.attn, quotation_no: form.quotationNo, dates: form.dates, valid_dates: form.validDates, currency: form.currency, trade_terms: form.tradeTerms, groups: form.groups, shipping: form.shipping })
    })
    ElMessage.success('Saved'); showSave.value = false; tplName.value = ''
  } catch { ElMessage.error('Failed') }
}

async function doLoad(id: number) {
  try {
    const r = await fetch(`/api/quotation-templates/${id}`); const t = await r.json()
    form.company = t.company || { name: '', address: '', tel: '', logo: '' }
    form.buyerName = t.buyer_name || ''; form.attn = t.attn || ''; form.quotationNo = t.quotation_no || ''
    form.dates = t.dates || ''; form.validDates = t.valid_dates || ''
    form.currency = t.currency || 'USD'; form.tradeTerms = t.trade_terms || 'DDP'
    form.shipping = t.shipping || { label: 'Shipping', cost: 0 }
    if (t.groups?.length) {
      form.groups = t.groups.map((g: any) => ({
        productNo: g.productNo || '', productName: g.productName || '', image: g.image || '',
        columns: g.columns || [{ key: 'color', label: 'Color', default: 'Color' }, { key: 'size', label: 'Size', default: 'Size' }],
        rows: (g.rows || []).map((r: any) => ({ ...r, amount: r.amount || (r.qty || 0) * (r.price || 0) }))
      }))
    }
    showLoad.value = false; ElMessage.success('Loaded')
  } catch { ElMessage.error('Failed') }
}

async function doDelete(id: number) {
  await ElMessageBox.confirm('Delete?', 'Confirm')
  await fetch(`/api/quotation-templates/${id}`, { method: 'DELETE' })
  tplList.value = tplList.value.filter(t => t.id !== id); ElMessage.success('Deleted')
}

// Export
function exportPDF() { window.print() }

async function exportExcel() {
  try {
    const groups = form.groups.map(g => ({
      productNo: g.productNo, spec: g.productName, imageUrl: g.image,
      items: g.rows.map(r => ({ size: g.columns.map(c => r[c.key]).filter(Boolean).join('/'), qty: r.qty, unitPrice: r.price, amount: r.amount }))
    }))
    const r = await fetch('/api/quotation/export/excel', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company: { name: form.company.name, address: form.company.address, tel: form.company.tel, logoUrl: form.company.logo }, buyerName: form.buyerName, attn: form.attn, quotationNo: form.quotationNo, dates: form.dates, validDates: form.validDates, currency: form.currency, tradeTerms: form.tradeTerms, groups, shipping: form.shipping })
    })
    if (!r.ok) throw new Error()
    const blob = await r.blob(); const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = `Quotation_${form.quotationNo || 'draft'}.xlsx`; a.click()
    URL.revokeObjectURL(url)
  } catch { ElMessage.error('Export failed') }
}

// Import Excel
async function importExcel(file: File) {
  try {
    const XLSX = await import('xlsx')
    const data = await file.arrayBuffer()
    const wb = XLSX.read(data)
    const ws = wb.Sheets[wb.SheetNames[0]]
    const json = XLSX.utils.sheet_to_json(ws, { header: 1 }) as any[][]

    // Find company name
    for (let i = 0; i < Math.min(5, json.length); i++) {
      const row = json[i] || []
      for (const cell of row) {
        const val = String(cell || '')
        if (val.includes('Trading') || val.includes('Company') || val.includes('Ltd')) {
          form.company.name = val
          if (json[i + 1]) form.company.address = (json[i + 1] || []).slice(1).filter(Boolean).join(' ')
          break
        }
      }
      if (form.company.name) break
    }

    // Find meta info
    for (let i = 0; i < Math.min(15, json.length); i++) {
      const row = (json[i] || []).map(String)
      const str = row.join('|')
      if (str.includes('To:')) { const c = row.find(v => v.startsWith('To:')); if (c) form.buyerName = c.replace('To:', '').trim() }
      if (str.includes('Attn:')) { const c = row.find(v => v.startsWith('Attn:')); if (c) form.attn = c.replace('Attn:', '').trim() }
      if (str.includes('Quotation No')) { const c = row.find(v => v.includes('Quotation No')); if (c) form.quotationNo = c.replace(/Quotation No[.:：]?\s*/i, '').trim() }
    }

    // Find header row
    let hdrRow = -1
    for (let i = 0; i < Math.min(15, json.length); i++) {
      const str = (json[i] || []).join('|').toLowerCase()
      if (str.includes('size') && str.includes('qty')) { hdrRow = i; break }
    }
    if (hdrRow === -1) { ElMessage.error('Cannot find headers'); return false }

    // Parse groups
    const groups: Group[] = []
    let cur: Group | null = null

    for (let i = hdrRow + 1; i < json.length; i++) {
      const row = json[i] || []
      if (row.every((c: any) => !c)) continue
      const str = row.join('|')

      if (str.toLowerCase().includes('shipping')) {
        form.shipping = { label: String(row.find((c: any) => String(c || '').toLowerCase().includes('shipping')) || 'Shipping'), cost: Number(row[row.length - 1] || 0) }
        continue
      }
      if (str.toUpperCase().includes('TOTAL')) continue

      const colA = String(row[0] || '').trim()
      if (colA && !isNaN(Number(colA)) && Number(colA) > 0) {
        cur = { productNo: String(row[1] || ''), productName: '', image: '', columns: [{ key: 'color', label: 'Color', default: 'Color' }], rows: [] }
        groups.push(cur)
      } else if (!cur) {
        cur = { productNo: String(row[1] || ''), productName: '', image: '', columns: [{ key: 'color', label: 'Color', default: 'Color' }], rows: [] }
        groups.push(cur)
      }

      const size = String(row[3] || '').trim()
      const qty = Number(row[4] || 0)
      const price = Number(row[5] || 0)
      if (size && qty > 0 && cur) {
        cur.rows.push({ color: size, qty, price, amount: Number((qty * price).toFixed(2)) })
        const spec = String(row[7] || '').trim()
        if (spec && !cur.productName) cur.productName = spec
      }
    }

    if (groups.length > 0) form.groups = groups
    ElMessage.success(`Imported ${groups.length} product(s)`)
  } catch (e) {
    console.error(e)
    ElMessage.error('Import failed')
  }
  return false
}
</script>

<style scoped>
.qm { background: #f0f2f5; min-height: 100vh; display: flex; flex-direction: column; }
.topbar { background: #fff; border-bottom: 1px solid #e4e7ed; position: sticky; top: 0; z-index: 100; }
.topbar-inner { display: flex; justify-content: space-between; align-items: center; padding: 0 20px; height: 48px; max-width: 1400px; margin: 0 auto; }
.topbar-left, .topbar-right { display: flex; align-items: center; gap: 8px; }
.brand { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 15px; }
.style-select { width: 120px; }
.main { display: flex; flex: 1; max-width: 1400px; margin: 0 auto; width: 100%; }
.sidebar { width: 240px; background: #fff; border-right: 1px solid #e4e7ed; position: sticky; top: 48px; height: calc(100vh - 48px); overflow-y: auto; transition: width 0.3s; flex-shrink: 0; }
.sidebar.collapsed { width: 40px; }
.sidebar-toggle { position: absolute; right: -12px; top: 12px; width: 24px; height: 24px; background: #fff; border: 1px solid #e4e7ed; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1; font-size: 12px; }
.sidebar-toggle:hover { color: #409eff; border-color: #409eff; }
.sidebar-content { padding: 16px; }
.sidebar-title { font-size: 14px; font-weight: 600; margin-bottom: 16px; }
.sg { margin-bottom: 14px; }
.sg label { display: block; font-size: 12px; color: #606266; margin-bottom: 6px; }
.w-full { width: 100%; }
.mb-8 { margin-bottom: 8px; }
.logo-box { width: 100%; height: 70px; border: 2px dashed #dcdfe6; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; }
.logo-box:hover { border-color: #409eff; }
.logo-preview { max-width: 100%; max-height: 100%; object-fit: contain; }
.logo-add { display: flex; flex-direction: column; align-items: center; gap: 4px; color: #909399; font-size: 12px; }
.paper-wrap { flex: 1; padding: 24px; overflow-x: auto; }
.paper { background: #fff; max-width: 900px; margin: 0 auto; padding: 36px 44px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); border-radius: 8px; }
.style-modern .line { height: 4px; background: linear-gradient(90deg, #409eff, #53a8ff); }
.style-modern .g-badge { background: #409eff; }
.style-minimal .line { height: 1px; background: #e4e7ed; }
.style-minimal .paper { box-shadow: none; border: 1px solid #e4e7ed; }
.hdr { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.hdr-left { display: flex; gap: 14px; align-items: flex-start; }
.hdr-logo { height: 56px; max-width: 130px; object-fit: contain; }
.hdr-company { display: flex; flex-direction: column; gap: 1px; }
.hc-name { font-size: 18px; font-weight: 700; padding: 2px 4px; border-radius: 4px; }
.hc-name:hover { background: #f5f7fa; }
.hc-name:focus { outline: none; background: #fff8e1; }
.hc-addr, .hc-tel { font-size: 12px; color: #606266; padding: 2px 4px; border-radius: 4px; }
.hc-addr:hover, .hc-tel:hover { background: #f5f7fa; }
.hc-addr:focus, .hc-tel:focus { outline: none; background: #fff8e1; }
.hdr-title { font-size: 28px; font-weight: 800; letter-spacing: 4px; padding: 4px 8px; border-radius: 4px; }
.hdr-title:hover { background: #f5f7fa; }
.hdr-title:focus { outline: none; background: #fff8e1; }
.line { height: 3px; background: #1a1a1a; margin-bottom: 16px; }
.meta { display: flex; justify-content: space-between; margin-bottom: 20px; gap: 24px; }
.meta-buyer { flex: 1; }
.meta-sec { font-size: 11px; font-weight: 600; color: #909399; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.mf { display: flex; gap: 6px; margin-bottom: 3px; }
.ml { font-size: 11px; color: #909399; min-width: 50px; }
.mv { font-size: 13px; padding: 2px 4px; border-radius: 4px; min-width: 80px; }
.mv:hover { background: #f5f7fa; }
.mv:focus { outline: none; background: #fff8e1; }
.meta-doc { display: flex; flex-direction: column; gap: 4px; min-width: 180px; }
.mdr { display: flex; justify-content: space-between; align-items: center; padding: 4px 8px; background: #f9fafb; border-radius: 4px; }
.mdl { font-size: 11px; color: #909399; }
.mdv { font-size: 13px; font-weight: 600; padding: 2px 4px; border-radius: 4px; }
.mdv:hover { background: #f0f2f5; }
.mdv:focus { outline: none; background: #fff8e1; }
.mdv.hl { color: #409eff; }
.mdi { border: 1px solid #dcdfe6; border-radius: 4px; padding: 3px 6px; font-size: 12px; }
.groups { margin-bottom: 20px; }
.group { border: 1px solid #e4e7ed; border-radius: 8px; padding: 14px; margin-bottom: 14px; }
.group:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.gh { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.gh-left { display: flex; align-items: center; gap: 8px; flex: 1; }
.g-badge { width: 26px; height: 26px; background: #303133; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.g-pno { width: 120px; border: 1px solid transparent; padding: 5px 8px; font-size: 13px; font-weight: 700; border-radius: 5px; background: transparent; }
.g-pno:hover { border-color: #dcdfe6; background: #f9fafb; }
.g-pno:focus { outline: none; border-color: #409eff; background: #fff; }
.g-pname { flex: 1; border: 1px solid transparent; padding: 5px 8px; font-size: 13px; border-radius: 5px; background: transparent; }
.g-pname:hover { border-color: #dcdfe6; background: #f9fafb; }
.g-pname:focus { outline: none; border-color: #409eff; background: #fff; }
.gh-right { display: flex; align-items: center; gap: 6px; }
.g-photo { width: 52px; height: 52px; border: 2px dashed #dcdfe6; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; }
.g-photo:hover { border-color: #409eff; background: #f5f7ff; }
.g-photo-img { width: 100%; height: 100%; object-fit: cover; }
.g-photo-add { color: #c0c4cc; font-size: 16px; }
.vt { width: 100%; border-collapse: collapse; margin-bottom: 6px; }
.vt th { background: #f5f7fa; padding: 6px 8px; font-size: 11px; font-weight: 600; color: #606266; text-align: left; border-bottom: 2px solid #e4e7ed; }
.vt td { padding: 6px 8px; border-bottom: 1px solid #f0f2f5; font-size: 13px; }
.vt tr:hover { background: #fafbfc; }
.th-inp { border: none; background: transparent; font-size: 11px; font-weight: 600; color: #606266; width: 100%; }
.th-inp:focus { outline: none; color: #409eff; }
.vc { width: 100%; border: 1px solid transparent; background: transparent; padding: 3px 6px; font-size: 13px; border-radius: 4px; }
.vc:hover { border-color: #dcdfe6; }
.vc:focus { outline: none; border-color: #409eff; background: #fff; }
.vc.ctr { text-align: center; }
.vc.rgt { text-align: right; }
.vw-idx { width: 32px; text-align: center; color: #c0c4cc; font-size: 12px; }
.vw-qty { width: 60px; }
.vw-price { width: 90px; }
.vw-amt { width: 90px; text-align: right; font-weight: 600; }
.vw-act { width: 36px; }
.rgt { text-align: right; }
.ctr { text-align: center; }
.bold { font-weight: 700; }
.sub { background: #f9fafb; }
.sub td { border-top: 2px solid #e4e7ed; font-weight: 600; }
.sub-lbl { font-size: 12px; color: #909399; }
.g-acts { display: flex; gap: 4px; padding-top: 4px; }
.add-prod { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 14px; border: 2px dashed #dcdfe6; border-radius: 8px; color: #909399; cursor: pointer; font-size: 13px; }
.add-prod:hover { border-color: #409eff; color: #409eff; background: #f5f7ff; }
.summary { display: flex; justify-content: flex-end; margin-top: 20px; }
.sum-right { width: 280px; }
.sum-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; }
.sum-row.total { border-top: 3px double #1a1a1a; margin-top: 6px; padding-top: 10px; font-size: 16px; font-weight: 800; }
.sum-inp { border: 1px solid transparent; background: transparent; padding: 3px 6px; font-size: 13px; width: 130px; border-radius: 4px; }
.sum-inp:hover { border-color: #dcdfe6; }
.sum-inp:focus { outline: none; border-color: #409eff; background: #fff; }
.sum-inp.rgt { text-align: right; width: 80px; }
.ftr { display: flex; justify-content: space-between; margin-top: 28px; padding-top: 14px; border-top: 1px solid #e4e7ed; font-size: 12px; color: #909399; }
.fk { font-weight: 600; margin-right: 4px; }
.ftr span[contenteditable] { padding: 2px 4px; border-radius: 4px; color: #606266; }
.ftr span[contenteditable]:hover { background: #f5f7fa; }
.ftr span[contenteditable]:focus { outline: none; background: #fff8e1; }
.tpl-st { text-align: center; padding: 30px; color: #909399; }
.tpl-list { max-height: 300px; overflow-y: auto; }
.tpl-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border: 1px solid #f0f2f5; border-radius: 6px; margin-bottom: 6px; cursor: pointer; }
.tpl-item:hover { background: #f5f7ff; border-color: #d4e5ff; }
.tpl-n { font-weight: 600; }
.tpl-d { font-size: 11px; color: #c0c4cc; }
@media print {
  .topbar, .sidebar { display: none !important; }
  .main { display: block; }
  .paper-wrap { padding: 0; }
  .paper { box-shadow: none; margin: 0; padding: 16px; max-width: 100%; border-radius: 0; }
  .vw-act, .g-acts, .add-prod { display: none !important; }
  .vc, .sum-inp, .th-inp { border: none !important; }
  @page { margin: 12mm; size: A4; }
}
</style>
