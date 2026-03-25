/* ========== 全局工具函数 ========== */

function getToken() {
  const m = document.cookie.match(/(?:^|;\s*)token=([^;]*)/);
  return m ? decodeURIComponent(m[1]) : null;
}

function setToken(t) {
  document.cookie = `token=${encodeURIComponent(t)};path=/;max-age=86400;SameSite=Lax`;
}

function removeToken() {
  document.cookie = 'token=;path=/;max-age=0';
}

function logout() {
  removeToken();
  location.href = '/login';
}

// 需要登录的页面检查
function requireAuth() {
  if (!getToken()) { location.href = '/login'; return false; }
  return true;
}

// API 请求封装
async function api(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`/api${path}`, { ...opts, headers });
  if (res.status === 401) { logout(); throw new Error('未授权'); }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `请求失败 (${res.status})`);
  }
  return res.json();
}

// 顶栏初始化
async function initHeader() {
  if (!getToken()) return;
  try {
    const u = await api('/auth/me');
    const el = document.getElementById('header-user');
    if (el) el.textContent = u.display_name || u.username;
  } catch(e) {}
  try {
    const s = await api('/alarms/stats');
    const total = (s.critical || 0) + (s.warning || 0) + (s.info || 0);
    const badge = document.getElementById('alarm-badge');
    if (badge && total > 0) { badge.textContent = total; badge.classList.remove('hidden'); }
  } catch(e) {}
}

// 数字格式化
function fmtNum(v, digits = 1) {
  if (v == null) return '-';
  const n = Number(v);
  if (isNaN(n)) return '-';
  if (Math.abs(n) >= 10000) return (n / 10000).toFixed(digits) + '万';
  return n.toFixed(digits);
}

// 状态标签
function statusBadge(status) {
  const map = {
    normal: ['正常', 'badge-green'], online: ['在线', 'badge-green'],
    fault: ['故障', 'badge-red'], offline: ['离线', 'badge-gray'],
    alarm: ['告警', 'badge-yellow'],
    critical: ['严重', 'badge-red'], warning: ['警告', 'badge-orange'], info: ['信息', 'badge-blue'],
    active: ['活跃', 'badge-red'], confirmed: ['已确认', 'badge-yellow'], recovered: ['已恢复', 'badge-green'],
    pending: ['待处理', 'badge-yellow'], in_progress: ['进行中', 'badge-blue'], completed: ['已完成', 'badge-green'], closed: ['已关闭', 'badge-gray'],
    enabled: ['启用', 'badge-green'], disabled: ['禁用', 'badge-gray'],
  };
  const [label, cls] = map[status] || [status || '-', 'badge-gray'];
  return `<span class="badge ${cls}">${label}</span>`;
}

// 优先级标签
function priorityBadge(p) {
  const map = { low: ['低', 'badge-gray'], medium: ['中', 'badge-blue'], high: ['高', 'badge-orange'], urgent: ['紧急', 'badge-red'] };
  const [label, cls] = map[p] || [p || '-', 'badge-gray'];
  return `<span class="badge ${cls}">${label}</span>`;
}

// 角色标签
function roleBadge(r) {
  const map = { admin: ['管理员', 'badge-red'], operator: ['运维员', 'badge-blue'], viewer: ['查看者', 'badge-gray'] };
  const [label, cls] = map[r] || [r || '-', 'badge-gray'];
  return `<span class="badge ${cls}">${label}</span>`;
}

// 日期格式化
function fmtDate(d) {
  if (!d) return '-';
  return new Date(d).toLocaleString('zh-CN');
}
function fmtDay(d) {
  if (!d) return '-';
  return d.substring(0, 10);
}

// 创建数据卡片 HTML
function dataCard(icon, label, value, unit, color) {
  return `<div class="data-card">
    <div class="icon-box bg-${color}">${icon}</div>
    <div><div class="label">${label}</div><div class="value">${value}<span class="unit">${unit || ''}</span></div></div>
  </div>`;
}

// 简单 toast 提示
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  const colors = { info: '#3b82f6', success: '#16a34a', error: '#dc2626' };
  el.style.cssText = `position:fixed;top:20px;right:20px;z-index:9999;padding:12px 20px;border-radius:8px;color:#fff;font-size:14px;background:${colors[type] || colors.info};box-shadow:0 4px 12px rgba(0,0,0,.15);transition:opacity .3s`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}
