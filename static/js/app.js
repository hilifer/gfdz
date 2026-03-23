/* 光伏电站监控平台 - 公共JS */

/**
 * 通用API请求封装
 */
async function api(url, method = 'GET', body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);

    const resp = await fetch(url, opts);
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: '请求失败' }));
        alert(`错误: ${err.detail || JSON.stringify(err)}`);
        throw new Error(err.detail);
    }
    return resp.json();
}

/**
 * 状态徽章
 */
function statusBadge(status) {
    const map = {
        normal: '<span class="badge bg-success">正常</span>',
        fault: '<span class="badge bg-danger">故障</span>',
        offline: '<span class="badge bg-secondary">离线</span>',
    };
    return map[status] || `<span class="badge bg-secondary">${status}</span>`;
}

/**
 * 同步单个电站
 */
async function syncStation(stationId) {
    try {
        const result = await api(`/api/sync/station/${stationId}`, 'POST');
        if (result.success) {
            alert('同步成功');
            location.reload();
        } else {
            alert(`同步失败: ${result.error}`);
        }
    } catch (e) {
        console.error('同步出错:', e);
    }
}

/**
 * 同步所有电站
 */
async function syncAll() {
    if (!confirm('确定同步所有电站数据？')) return;
    try {
        const result = await api('/api/sync/all', 'POST');
        alert(`同步完成！成功: ${result.success}, 失败: ${result.failed}`);
        location.reload();
    } catch (e) {
        console.error('同步出错:', e);
    }
}
