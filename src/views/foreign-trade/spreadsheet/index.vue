<template>
  <div class="spreadsheet">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>在线表格</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddRow">
              <el-icon><i class="ep-plus" /></el-icon>
              添加行
            </el-button>
            <el-button type="success" @click="handleExport">
              <el-icon><i class="ep-download" /></el-icon>
              导出Excel
            </el-button>
            <el-upload
              :show-file-list="false"
              :before-upload="handleImportFile"
              accept=".csv,.xlsx,.xls"
            >
              <el-button type="warning">
                <el-icon><i class="ep-upload" /></el-icon>
                导入
              </el-button>
            </el-upload>
          </div>
        </div>
      </template>

      <!-- 公式工具栏 -->
      <div class="formula-toolbar">
        <div class="formula-buttons">
          <el-button-group>
            <el-button @click="calcFormula('SUM')" :disabled="selectedCells.length === 0" type="primary" plain>
              <el-icon><i class="ep-s-operation" /></el-icon>
              求和 SUM
            </el-button>
            <el-button @click="calcFormula('AVG')" :disabled="selectedCells.length === 0" type="primary" plain>
              平均值 AVG
            </el-button>
            <el-button @click="calcFormula('COUNT')" :disabled="selectedCells.length === 0" type="primary" plain>
              计数 COUNT
            </el-button>
            <el-button @click="calcFormula('MAX')" :disabled="selectedCells.length === 0" type="primary" plain>
              最大值 MAX
            </el-button>
            <el-button @click="calcFormula('MIN')" :disabled="selectedCells.length === 0" type="primary" plain>
              最小值 MIN
            </el-button>
          </el-button-group>
          <el-divider direction="vertical" />
          <el-tag v-if="selectedCells.length > 0" type="info" size="small">
            已选 {{ selectedCells.length }} 个单元格
          </el-tag>
        </div>
        <div v-if="formulaResult !== null" class="formula-result">
          <el-tag :type="formulaResultTagType" size="large" effect="dark">
            {{ formulaResultLabel }}: {{ formulaResult }}
          </el-tag>
        </div>
      </div>

      <!-- 插入公式区域 -->
      <div class="formula-input-bar">
        <el-input
          v-model="formulaInput"
          placeholder="输入公式，如 =SUM(E1:E5)  =AVG(F1:F3)  =MAX(G1:G4)"
          clearable
          @keyup.enter="handleInsertFormula"
          style="width: 500px"
        >
          <template #prefix>
            <span style="font-weight: bold; color: #409eff">fx</span>
          </template>
          <template #append>
            <el-button @click="handleInsertFormula" type="primary">计算</el-button>
          </template>
        </el-input>
        <el-dropdown @command="insertFormulaTemplate" trigger="click">
          <el-button type="info" plain style="margin-left: 8px">
            插入公式模板 <el-icon><i class="ep-arrow-down" /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="=SUM()">=SUM(范围) - 求和</el-dropdown-item>
              <el-dropdown-item command="=AVG()">=AVG(范围) - 平均值</el-dropdown-item>
              <el-dropdown-item command="=MAX()">=MAX(范围) - 最大值</el-dropdown-item>
              <el-dropdown-item command="=MIN()">=MIN(范围) - 最小值</el-dropdown-item>
              <el-dropdown-item command="=COUNT()">=COUNT(范围) - 计数</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="spreadsheet-toolbar">
        <el-button-group>
          <el-tooltip content="Ctrl+Z">
            <el-button @click="handleUndo" :disabled="!canUndo">
              <el-icon><i class="ep-refresh-left" /></el-icon>
              撤销
            </el-button>
          </el-tooltip>
          <el-tooltip content="Ctrl+Y">
            <el-button @click="handleRedo" :disabled="!canRedo">
              <el-icon><i class="ep-refresh-right" /></el-icon>
              重做
            </el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-button @click="handleCopy" :disabled="selectedRows.length === 0">
            <el-icon><i class="ep-document-copy" /></el-icon>
            复制
          </el-button>
          <el-button @click="handlePaste">
            <el-icon><i class="ep-folder-add" /></el-icon>
            粘贴
          </el-button>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button @click="handleClearAll" type="danger" plain>
          <el-icon><i class="ep-delete" /></el-icon>
          清空
        </el-button>
      </div>

      <div class="spreadsheet-container">
        <el-table
          ref="tableRef"
          :data="tableData"
          border
          style="width: 100%"
          @selection-change="handleSelectionChange"
          @cell-click="handleCellClick"
          @cell-dblclick="handleCellDblClick"
          highlight-current-row
        >
          <el-table-column type="selection" width="55" />
          <el-table-column type="index" label="序号" width="60">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column
            v-for="col in columns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :width="col.width"
          >
            <template #default="{ row, $index }">
              <div
                :class="['cell-wrapper', { 'cell-selected': isCellSelected($index, col.prop) }]"
                @click.ctrl="handleCtrlCellClick($index, col.prop, row[col.prop])"
              >
                <el-input
                  v-if="editingCell.row === $index && editingCell.col === col.prop"
                  v-model="row[col.prop]"
                  size="small"
                  @blur="handleCellBlur($index, col.prop)"
                  @keyup.enter="handleCellBlur($index, col.prop)"
                  ref="editInputRef"
                />
                <span v-else class="cell-text">{{ row[col.prop] }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ $index }">
              <el-button type="danger" link @click="handleDeleteRow($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="spreadsheet-footer">
        <div class="footer-info">
          <span>共 {{ tableData.length }} 行</span>
          <span>已选 {{ selectedRows.length }} 行</span>
          <span v-if="undoStack.length > 0">可撤销 {{ undoStack.length }} 步</span>
          <span v-if="selectedCells.length > 0" class="selected-cells-info">
            选中单元格: {{ selectedCells.map(c => getCellRef(c.row, c.col)).join(', ') }}
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="handleSaveToLocal">保存到本地</el-button>
          <el-button type="primary" @click="handleSave">保存到服务器</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== 类型定义 ====================
interface TableRow {
  [key: string]: any
}

interface UndoRecord {
  data: TableRow[]
  description: string
}

interface CellRef {
  row: number
  col: string
  value: any
}

// ==================== 状态 ====================
const tableRef = ref()
const editInputRef = ref()
const selectedRows = ref<TableRow[]>([])
const canUndo = ref(false)
const canRedo = ref(false)

// 撤销/重做栈
const undoStack = ref<UndoRecord[]>([])
const redoStack = ref<UndoRecord[]>([])
const MAX_UNDO_STEPS = 50

const editingCell = reactive({
  row: -1,
  col: '',
})

// ==================== 公式计算状态 ====================
const selectedCells = ref<CellRef[]>([])
const formulaResult = ref<number | null>(null)
const formulaResultLabel = ref('')
const formulaResultTagType = ref<'success' | 'warning' | 'danger' | 'info'>('success')
const formulaInput = ref('')

// 列定义
const columns = [
  { prop: 'name', label: '产品名称', width: 200 },
  { prop: 'sku', label: 'SKU', width: 120 },
  { prop: 'category', label: '分类', width: 100 },
  { prop: 'price_cny', label: '价格(CNY)', width: 110 },
  { prop: 'price_usd', label: '价格(USD)', width: 110 },
  { prop: 'quantity', label: '数量', width: 100 },
  { prop: 'supplier', label: '供货商', width: 150 },
  { prop: 'status', label: '状态', width: 100 },
  { prop: 'notes', label: '备注', width: 200 },
]

// 表格数据
const tableData = ref<TableRow[]>([])

// ==================== 单元格选择 ====================
function getCellRef(row: number, col: string): string {
  // 列名映射：找到列的索引
  const colIndex = columns.findIndex(c => c.prop === col)
  const colLetter = String.fromCharCode(65 + colIndex) // A, B, C, ...
  return `${colLetter}${row + 1}`
}

function isCellSelected(row: number, col: string): boolean {
  return selectedCells.value.some(c => c.row === row && c.col === col)
}

function handleCellClick(row: TableRow, column: any, cell: HTMLElement, event: MouseEvent) {
  const colProp = column.property
  if (!colProp) return

  // Ctrl+点击 多选
  if (event.ctrlKey || event.metaKey) {
    handleCtrlCellClick(tableData.value.indexOf(row), colProp, row[colProp])
  } else {
    // 普通点击：单选
    const rowIndex = tableData.value.indexOf(row)
    const value = row[colProp]
    selectedCells.value = [{ row: rowIndex, col: colProp, value }]
  }
}

function handleCtrlCellClick(rowIndex: number, colProp: string, value: any) {
  const existingIndex = selectedCells.value.findIndex(c => c.row === rowIndex && c.col === colProp)
  if (existingIndex >= 0) {
    // 取消选中
    selectedCells.value.splice(existingIndex, 1)
  } else {
    // 添加选中
    selectedCells.value.push({ row: rowIndex, col: colProp, value })
  }
}

// ==================== 公式计算 ====================
const FORMULA_LABELS: Record<string, string> = {
  SUM: '求和',
  AVG: '平均值',
  COUNT: '计数',
  MAX: '最大值',
  MIN: '最小值',
}

const FORMULA_TAG_TYPES: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
  SUM: 'success',
  AVG: 'warning',
  COUNT: 'info',
  MAX: 'danger',
  MIN: 'warning',
}

function calcFormula(type: string) {
  const values = selectedCells.value
    .map(c => {
      const row = tableData.value[c.row]
      return row ? Number(row[c.col]) : NaN
    })
    .filter(v => !isNaN(v))

  if (values.length === 0) {
    ElMessage.warning('选中的单元格中没有数值')
    return
  }

  let result: number
  switch (type) {
    case 'SUM':
      result = values.reduce((a, b) => a + b, 0)
      break
    case 'AVG':
      result = values.reduce((a, b) => a + b, 0) / values.length
      break
    case 'COUNT':
      result = values.length
      break
    case 'MAX':
      result = Math.max(...values)
      break
    case 'MIN':
      result = Math.min(...values)
      break
    default:
      return
  }

  formulaResult.value = type === 'COUNT' ? result : Number(result.toFixed(4))
  formulaResultLabel.value = FORMULA_LABELS[type] || type
  formulaResultTagType.value = FORMULA_TAG_TYPES[type] || 'success'
}

// ==================== 插入公式解析 ====================
function parseFormula(formula: string): number | null {
  // 匹配 =FUNC(An:Bm) 格式
  const match = formula.match(/^=(SUM|AVG|MAX|MIN|COUNT)\(([A-Z])(\d+):([A-Z])(\d+)\)$/i)
  if (!match) {
    ElMessage.error('公式格式错误，请使用如 =SUM(E1:E5) 的格式')
    return null
  }

  const func = match[1].toUpperCase()
  const startCol = match[2].toUpperCase()
  const startRow = parseInt(match[3])
  const endCol = match[4].toUpperCase()
  const endRow = parseInt(match[5])

  if (startCol !== endCol) {
    ElMessage.error('目前仅支持单列范围，如 =SUM(E1:E5)')
    return null
  }

  // 找到对应的列 prop
  const colIndex = startCol.charCodeAt(0) - 65
  if (colIndex < 0 || colIndex >= columns.length) {
    ElMessage.error(`列 ${startCol} 不存在`)
    return null
  }

  const colProp = columns[colIndex].prop

  // 收集范围内的值
  const values: number[] = []
  for (let i = startRow - 1; i < endRow && i < tableData.value.length; i++) {
    if (i < 0) continue
    const val = Number(tableData.value[i][colProp])
    if (!isNaN(val)) {
      values.push(val)
    }
  }

  if (values.length === 0) {
    ElMessage.warning('公式范围内没有数值')
    return null
  }

  switch (func) {
    case 'SUM':
      return values.reduce((a, b) => a + b, 0)
    case 'AVG':
      return values.reduce((a, b) => a + b, 0) / values.length
    case 'MAX':
      return Math.max(...values)
    case 'MIN':
      return Math.min(...values)
    case 'COUNT':
      return values.length
    default:
      return null
  }
}

function handleInsertFormula() {
  if (!formulaInput.value.trim()) return

  const result = parseFormula(formulaInput.value.trim())
  if (result !== null) {
    const func = formulaInput.value.match(/^=(\w+)/)?.[1]?.toUpperCase() || ''
    formulaResult.value = Number(result.toFixed(4))
    formulaResultLabel.value = `${FORMULA_LABELS[func] || func} (${formulaInput.value})`
    formulaResultTagType.value = FORMULA_TAG_TYPES[func] || 'success'
    ElMessage.success(`公式计算结果: ${result.toFixed(4)}`)
  }
}

function insertFormulaTemplate(template: string) {
  formulaInput.value = template
}

// ==================== 撤销/重做 ====================
function saveUndoState(description: string) {
  const record: UndoRecord = {
    data: JSON.parse(JSON.stringify(tableData.value)),
    description,
  }
  undoStack.value.push(record)
  
  if (undoStack.value.length > MAX_UNDO_STEPS) {
    undoStack.value.shift()
  }
  
  redoStack.value = []
  updateUndoRedoState()
}

function updateUndoRedoState() {
  canUndo.value = undoStack.value.length > 0
  canRedo.value = redoStack.value.length > 0
}

function handleUndo() {
  if (undoStack.value.length === 0) return
  
  const currentRecord: UndoRecord = {
    data: JSON.parse(JSON.stringify(tableData.value)),
    description: 'undo',
  }
  redoStack.value.push(currentRecord)
  
  const record = undoStack.value.pop()!
  tableData.value = record.data
  
  updateUndoRedoState()
  ElMessage.info(`撤销: ${record.description}`)
}

function handleRedo() {
  if (redoStack.value.length === 0) return
  
  const currentRecord: UndoRecord = {
    data: JSON.parse(JSON.stringify(tableData.value)),
    description: 'redo',
  }
  undoStack.value.push(currentRecord)
  
  const record = redoStack.value.pop()!
  tableData.value = record.data
  
  updateUndoRedoState()
  ElMessage.info(`重做完成`)
}

// ==================== 单元格编辑 ====================
const handleSelectionChange = (rows: TableRow[]) => {
  selectedRows.value = rows
}

const handleCellDblClick = (row: TableRow, column: any) => {
  const rowIndex = tableData.value.indexOf(row)
  const colProp = column.property
  if (colProp) {
    editingCell.row = rowIndex
    editingCell.col = colProp
    nextTick(() => {
      if (editInputRef.value?.[0]) {
        editInputRef.value[0].focus()
      }
    })
  }
}

const handleCellBlur = (rowIndex: number, colProp: string) => {
  editingCell.row = -1
  editingCell.col = ''
  saveUndoState(`编辑 ${colProp}`)
}

// ==================== 行操作 ====================
const handleAddRow = () => {
  saveUndoState('添加行')
  tableData.value.push({
    name: '',
    sku: '',
    category: '',
    price_cny: 0,
    price_usd: 0,
    quantity: 0,
    supplier: '',
    status: '',
    notes: '',
  })
}

const handleDeleteRow = (index: number) => {
  saveUndoState('删除行')
  tableData.value.splice(index, 1)
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有数据吗？', '确认', { type: 'warning' })
    saveUndoState('清空全部')
    tableData.value = []
  } catch {
    // 取消
  }
}

// ==================== 复制/粘贴 ====================
const clipboard = ref<string>('')

const handleCopy = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要复制的行')
    return
  }
  
  const headers = columns.map(c => c.label).join('\t')
  const rows = selectedRows.value.map(row => 
    columns.map(c => row[c.prop] ?? '').join('\t')
  )
  clipboard.value = [headers, ...rows].join('\n')
  
  navigator.clipboard?.writeText(clipboard.value).then(() => {
    ElMessage.success(`已复制 ${selectedRows.value.length} 行`)
  }).catch(() => {
    ElMessage.success(`已复制 ${selectedRows.value.length} 行到内存`)
  })
}

const handlePaste = async () => {
  let text = clipboard.value
  
  try {
    text = await navigator.clipboard.readText()
  } catch {
    // 使用内存中的剪贴板
  }
  
  if (!text) {
    ElMessage.warning('剪贴板为空')
    return
  }
  
  saveUndoState('粘贴')
  
  const lines = text.split('\n').filter(line => line.trim())
  const startRow = tableData.value.length
  
  for (const line of lines) {
    const cells = line.split('\t')
    if (cells.length >= columns.length) {
      const newRow: TableRow = {}
      columns.forEach((col, i) => {
        newRow[col.prop] = cells[i] || ''
      })
      tableData.value.push(newRow)
    }
  }
  
  ElMessage.success(`已粘贴 ${lines.length} 行`)
}

// ==================== 导入/导出 ====================
const handleExport = async () => {
  const XLSX = await import('xlsx')

  const exportData = tableData.value.map(row => {
    const obj: any = {}
    columns.forEach(col => {
      obj[col.label] = row[col.prop]
    })
    return obj
  })
  
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(exportData)
  
  ws['!cols'] = columns.map(c => ({ wch: c.width ? c.width / 8 : 15 }))
  
  XLSX.utils.book_append_sheet(wb, ws, '数据')
  
  const now = new Date().toISOString().slice(0, 10)
  XLSX.writeFile(wb, `表格数据_${now}.xlsx`)
  
  ElMessage.success('导出成功')
}

const handleImportFile = async (file: File) => {
  const XLSX = await import('xlsx')

  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      const data = e.target?.result
      const wb = XLSX.read(data, { type: 'binary' })
      const ws = wb.Sheets[wb.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(ws)
      
      if (jsonData.length === 0) {
        ElMessage.warning('文件为空')
        return
      }
      
      saveUndoState('导入数据')
      
      const columnMap: Record<string, string> = {}
      columns.forEach(col => {
        columnMap[col.label] = col.prop
        columnMap[col.prop] = col.prop
      })
      
      const imported = jsonData.map((row: any) => {
        const newRow: TableRow = {}
        Object.keys(row).forEach(key => {
          const prop = columnMap[key] || key
          newRow[prop] = row[key]
        })
        return newRow
      })
      
      tableData.value = [...tableData.value, ...imported]
      ElMessage.success(`成功导入 ${imported.length} 行数据`)
    } catch (err) {
      ElMessage.error('导入失败，请检查文件格式')
      // 导入失败
    }
  }
  
  reader.readAsBinaryString(file)
  return false
}

// ==================== 保存 ====================
const handleSaveToLocal = () => {
  const json = JSON.stringify(tableData.value, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `表格数据_${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已保存到本地文件')
}

const handleSave = () => {
  ElMessage.success('保存成功（开发中）')
}

// ==================== 快捷键 ====================
const handleKeydown = (e: KeyboardEvent) => {
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'z' && !e.shiftKey) {
      e.preventDefault()
      handleUndo()
    } else if (e.key === 'z' && e.shiftKey) {
      e.preventDefault()
      handleRedo()
    } else if (e.key === 'y') {
      e.preventDefault()
      handleRedo()
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="scss">
.spreadsheet {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.formula-toolbar {
  margin-bottom: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.formula-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.formula-result {
  display: flex;
  align-items: center;
  gap: 8px;
}

.formula-input-bar {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.spreadsheet-toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.spreadsheet-container {
  margin-bottom: 16px;
  overflow-x: auto;
}

.cell-wrapper {
  padding: 2px 4px;
  min-height: 32px;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #ecf5ff;
  }

  &.cell-selected {
    background-color: #d9ecff;
    border: 1px solid #409eff;
  }
}

.cell-text {
  display: inline-block;
  min-height: 20px;
  width: 100%;
}

.selected-cells-info {
  color: #409eff;
  font-size: 12px;
}

.spreadsheet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .footer-info {
    display: flex;
    gap: 20px;
    color: #909399;
    font-size: 14px;
  }
  
  .footer-actions {
    display: flex;
    gap: 10px;
  }
}
</style>
