import { invoke } from '@tauri-apps/api/tauri';
import { open } from '@tauri-apps/api/dialog';

// 状态管理
let currentTab = 'json';
const langDirs = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
  initializeNavigation();
  initializeJsonTab();
  initializeExcelTab();
  initializeFieldExtractTab();
  initializeTranslationTab();
});

// 初始化导航
function initializeNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tabName = item.dataset.tab;
      switchTab(tabName);
    });
  });
}

// 切换页签
function switchTab(tabName) {
  // 更新导航高亮
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.tab === tabName);
  });
  
  // 显示对应内容
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.toggle('active', content.id === `tab-${tabName}`);
  });
  
  currentTab = tabName;
  updateStatus('就绪');
}

// 更新状态栏
function updateStatus(message) {
  const statusBar = document.getElementById('status-bar');
  statusBar.textContent = message;
}

// 显示结果
function showResult(elementId, text) {
  const resultBox = document.getElementById(elementId);
  resultBox.textContent += text + '\n';
  resultBox.scrollTop = resultBox.scrollHeight;
}

// 清空结果
function clearResult(elementId) {
  const resultBox = document.getElementById(elementId);
  resultBox.textContent = '';
}

// ==================== JSON检测页签 ====================
function initializeJsonTab() {
  // 浏览路径
  document.getElementById('json-browse').addEventListener('click', async () => {
    const selected = await open({
      directory: true,
      multiple: false,
      title: '选择JSON文件或文件夹'
    });
    if (selected) {
      document.getElementById('json-path').value = selected;
    }
  });

  // 开始检测
  document.getElementById('json-start').addEventListener('click', async () => {
    const path = document.getElementById('json-path').value;

    if (!path) {
      alert('请选择JSON文件或文件夹');
      return;
    }

    updateStatus('正在检测JSON格式...');
    clearResult('json-result');
    showResult('json-result', '开始检测JSON格式...\n');

    try {
      const result = await invoke('run_json_detector', { path });
      showResult('json-result', result);
      updateStatus('检测完成');
    } catch (error) {
      showResult('json-result', `错误: ${error}`);
      updateStatus('检测失败');
    }
  });

  // 清空结果
  document.getElementById('json-clear').addEventListener('click', () => {
    clearResult('json-result');
  });
}

// ==================== Excel数据处理页签 ====================
function initializeExcelTab() {
  // 浏览输入文件
  document.getElementById('excel-browse-input').addEventListener('click', async () => {
    const selected = await open({
      filters: [{
        name: 'Excel',
        extensions: ['xlsx', 'xls']
      }],
      title: '选择Excel文件'
    });
    if (selected) {
      document.getElementById('excel-input').value = selected;
    }
  });

  // 浏览输出文件夹
  document.getElementById('excel-browse-output').addEventListener('click', async () => {
    const selected = await open({
      directory: true,
      multiple: false,
      title: '选择输出文件夹'
    });
    if (selected) {
      document.getElementById('excel-output').value = selected;
    }
  });

  // 开始处理
  document.getElementById('excel-start').addEventListener('click', async () => {
    const inputFile = document.getElementById('excel-input').value;
    const outputFolder = document.getElementById('excel-output').value;
    const mode = document.getElementById('excel-mode').value;

    if (!inputFile || !outputFolder) {
      alert('请选择输入文件和输出文件夹');
      return;
    }

    updateStatus('正在处理Excel数据...');
    clearResult('excel-result');
    showResult('excel-result', '开始处理Excel数据...\n');

    try {
      const result = await invoke('run_excel_processor', {
        inputFile,
        outputFolder,
        mode
      });
      showResult('excel-result', result);
      updateStatus('处理完成');
    } catch (error) {
      showResult('excel-result', `错误: ${error}`);
      updateStatus('处理失败');
    }
  });

  // 清空结果
  document.getElementById('excel-clear').addEventListener('click', () => {
    clearResult('excel-result');
  });
}

// ==================== 表字段导出页签 ====================
function initializeFieldExtractTab() {
  // 浏览目录
  document.getElementById('field-browse-dir').addEventListener('click', async () => {
    const selected = await open({
      directory: true,
      multiple: false,
      title: '选择扫描目录'
    });
    if (selected) {
      document.getElementById('field-directory').value = selected;
    }
  });

  // 浏览输出目录
  document.getElementById('field-browse-output').addEventListener('click', async () => {
    const selected = await open({
      directory: true,
      multiple: false,
      title: '选择输出目录'
    });
    if (selected) {
      document.getElementById('field-output').value = selected;
    }
  });

  // 开始提取
  document.getElementById('field-start').addEventListener('click', async () => {
    const directory = document.getElementById('field-directory').value;
    const output = document.getElementById('field-output').value;
    const format = document.getElementById('field-format').value;
    const recursive = document.getElementById('field-recursive').checked;

    if (!directory || !output) {
      alert('请选择扫描目录和输出目录');
      return;
    }

    updateStatus('正在提取字段...');
    clearResult('field-result');
    showResult('field-result', '开始提取表字段信息...\n');

    try {
      const result = await invoke('run_field_extractor', {
        directory,
        outputFolder: output,
        format,
        recursive
      });
      showResult('field-result', result);
      updateStatus('提取完成');
    } catch (error) {
      showResult('field-result', `错误: ${error}`);
      updateStatus('提取失败');
    }
  });

  // 清空结果
  document.getElementById('field-clear').addEventListener('click', () => {
    clearResult('field-result');
  });
}

// ==================== 多语言翻译提取页签 ====================
function initializeTranslationTab() {
  // 浏览JSON配置
  document.getElementById('trans-browse-json').addEventListener('click', async () => {
    const selected = await open({
      filters: [{
        name: 'JSON',
        extensions: ['json']
      }],
      title: '选择JSON配置文件'
    });
    if (selected) {
      document.getElementById('trans-json').value = selected;
    }
  });

  // 添加语言目录
  document.getElementById('trans-add-dir').addEventListener('click', () => {
    addLangDir();
  });

  // 浏览输出文件
  document.getElementById('trans-browse-output').addEventListener('click', async () => {
    const selected = await open({
      filters: [{
        name: 'Excel',
        extensions: ['xlsx']
      }],
      title: '选择输出文件'
    });
    if (selected) {
      document.getElementById('trans-output').value = selected;
    }
  });

  // 开始提取
  document.getElementById('trans-start').addEventListener('click', async () => {
    const jsonConfig = document.getElementById('trans-json').value;
    const outputFile = document.getElementById('trans-output').value;

    if (!jsonConfig || !outputFile) {
      alert('请选择JSON配置文件和输出文件');
      return;
    }

    if (langDirs.length === 0) {
      alert('请至少添加一个语言目录');
      return;
    }

    updateStatus('正在提取翻译内容...');
    clearResult('trans-result');
    showResult('trans-result', '开始提取多语言翻译内容...\n');

    try {
      const result = await invoke('run_translation_extractor', {
        jsonConfig,
        langDirs,
        outputFile
      });
      showResult('trans-result', result);
      updateStatus('提取完成');
    } catch (error) {
      showResult('trans-result', `错误: ${error}`);
      updateStatus('提取失败');
    }
  });

  // 清空结果
  document.getElementById('trans-clear').addEventListener('click', () => {
    clearResult('trans-result');
  });
}

// 添加语言目录
function addLangDir() {
  const container = document.getElementById('trans-lang-dirs');
  const index = langDirs.length;
  
  const dirItem = document.createElement('div');
  dirItem.className = 'lang-dir-item';
  dirItem.innerHTML = `
    <input type="text" id="lang-dir-${index}" placeholder="选择语言目录" readonly />
    <button class="btn btn-secondary" id="lang-browse-${index}">浏览</button>
    <button class="btn btn-remove" id="lang-remove-${index}">移除</button>
  `;
  
  container.appendChild(dirItem);
  langDirs.push('');
  
  // 浏览按钮
  document.getElementById(`lang-browse-${index}`).addEventListener('click', async () => {
    const selected = await open({
      directory: true,
      multiple: false,
      title: '选择语言目录'
    });
    if (selected) {
      document.getElementById(`lang-dir-${index}`).value = selected;
      langDirs[index] = selected;
    }
  });
  
  // 移除按钮
  document.getElementById(`lang-remove-${index}`).addEventListener('click', () => {
    dirItem.remove();
    langDirs.splice(index, 1);
  });
}
