const API = '/api';

// ── helpers ──────────────────────────────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function fmt(val) {
  if (typeof val === 'object' && val !== null) return JSON.stringify(val, null, 2);
  return val;
}

function showToast(id, msg, type = 'success') {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `toast ${type}`;
  setTimeout(() => el.classList.add('hidden'), 3500);
}

function statusBadge(status) {
  const cls = { pending: 'status-pending', shipped: 'status-shipped', delivered: 'status-delivered' }[status] || '';
  return `<span class="status-badge ${cls}">${status}</span>`;
}

// ── tabs ─────────────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ── health check ─────────────────────────────────────────────────────────────

async function checkHealth() {
  const badge = document.getElementById('status-badge');
  try {
    await apiFetch('/health');
    badge.textContent = 'DynamoDB Local ✓';
    badge.className = 'badge badge-ok';
  } catch {
    badge.textContent = 'DynamoDB Local ✗';
    badge.className = 'badge badge-error';
  }
}

checkHealth();
setInterval(checkHealth, 15000);

// ── seed / wipe ───────────────────────────────────────────────────────────────

document.getElementById('btn-seed').addEventListener('click', async () => {
  try {
    const r = await apiFetch('/seed', { method: 'POST' });
    showToast('toast-product', `Seeded: ${r.products} products, ${r.orders} orders`);
    loadProducts();
    loadOrders();
  } catch (e) {
    showToast('toast-product', e.message, 'error');
  }
});

document.getElementById('btn-wipe').addEventListener('click', async () => {
  if (!confirm('Wipe all data?')) return;
  try {
    const r = await apiFetch('/seed', { method: 'DELETE' });
    showToast('toast-product', `Wiped: ${r.deleted_products} products, ${r.deleted_orders} orders`);
    loadProducts();
    loadOrders();
  } catch (e) {
    showToast('toast-product', e.message, 'error');
  }
});

// ── products ─────────────────────────────────────────────────────────────────

async function loadProducts() {
  const tbody = document.getElementById('tbody-products');
  tbody.innerHTML = '<tr><td colspan="7" class="empty">Loading…</td></tr>';
  try {
    const items = await apiFetch('/products');
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty">No products. Click "Seed Data" to load sample data.</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(p => `
      <tr>
        <td><code>${p.productId}</code></td>
        <td>${p.name}</td>
        <td>${p.category}</td>
        <td>$${Number(p.price).toFixed(2)}</td>
        <td>${p.stock}</td>
        <td>${p.description || ''}</td>
        <td>
          <button class="btn-icon" onclick="editProduct(${JSON.stringify(JSON.stringify(p))})" title="Edit">✏️</button>
          <button class="btn-icon" onclick="deleteProduct('${p.productId}')" title="Delete">🗑️</button>
        </td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty">${e.message}</td></tr>`;
  }
}

function editProduct(jsonStr) {
  const p = JSON.parse(jsonStr);
  document.getElementById('form-product-title').textContent = 'Edit Product';
  document.getElementById('product-edit-id').value = p.productId;
  document.getElementById('p-productId').value = p.productId;
  document.getElementById('p-productId').disabled = true;
  document.getElementById('p-name').value = p.name;
  document.getElementById('p-category').value = p.category;
  document.getElementById('p-price').value = p.price;
  document.getElementById('p-stock').value = p.stock;
  document.getElementById('p-description').value = p.description || '';
  document.getElementById('form-product').classList.remove('hidden');
}

async function deleteProduct(id) {
  if (!confirm(`Delete product ${id}?`)) return;
  try {
    await apiFetch(`/products/${id}`, { method: 'DELETE' });
    showToast('toast-product', `Deleted product ${id}`);
    loadProducts();
  } catch (e) {
    showToast('toast-product', e.message, 'error');
  }
}

document.getElementById('btn-show-add-product').addEventListener('click', () => {
  document.getElementById('form-product-title').textContent = 'Add Product';
  document.getElementById('product-edit-id').value = '';
  document.getElementById('p-productId').disabled = false;
  document.getElementById('form-product').reset();
  document.getElementById('form-product').classList.remove('hidden');
});

document.getElementById('btn-cancel-product').addEventListener('click', () => {
  document.getElementById('form-product').classList.add('hidden');
  document.getElementById('p-productId').disabled = false;
});

document.getElementById('form-product').addEventListener('submit', async e => {
  e.preventDefault();
  const editId = document.getElementById('product-edit-id').value;
  const body = {
    productId: document.getElementById('p-productId').value.trim(),
    name: document.getElementById('p-name').value.trim(),
    category: document.getElementById('p-category').value,
    price: parseFloat(document.getElementById('p-price').value),
    stock: parseInt(document.getElementById('p-stock').value),
    description: document.getElementById('p-description').value.trim(),
  };
  try {
    if (editId) {
      await apiFetch(`/products/${editId}`, { method: 'PUT', body: JSON.stringify(body) });
      showToast('toast-product', `Updated product ${editId}`);
    } else {
      await apiFetch('/products', { method: 'POST', body: JSON.stringify(body) });
      showToast('toast-product', `Created product ${body.productId}`);
    }
    document.getElementById('form-product').classList.add('hidden');
    document.getElementById('p-productId').disabled = false;
    loadProducts();
  } catch (err) {
    showToast('toast-product', err.message, 'error');
  }
});

// ── orders ────────────────────────────────────────────────────────────────────

async function loadOrders() {
  const tbody = document.getElementById('tbody-orders');
  tbody.innerHTML = '<tr><td colspan="8" class="empty">Loading…</td></tr>';
  try {
    const items = await apiFetch('/orders');
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty">No orders. Click "Seed Data" to load sample data.</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(o => `
      <tr>
        <td><code>${o.orderId}</code></td>
        <td><code>${o.customerId}</code></td>
        <td><code>${o.productId}</code></td>
        <td>${o.quantity}</td>
        <td>${statusBadge(o.status)}</td>
        <td>$${Number(o.totalPrice).toFixed(2)}</td>
        <td>${o.createdAt ? o.createdAt.substring(0, 10) : ''}</td>
        <td>
          <button class="btn-icon" onclick="deleteOrder('${o.orderId}','${o.customerId}')" title="Delete">🗑️</button>
        </td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty">${e.message}</td></tr>`;
  }
}

async function deleteOrder(orderId, customerId) {
  if (!confirm(`Delete order ${orderId}?`)) return;
  try {
    await apiFetch(`/orders/${orderId}?customerId=${encodeURIComponent(customerId)}`, { method: 'DELETE' });
    showToast('toast-order', `Deleted order ${orderId}`);
    loadOrders();
  } catch (e) {
    showToast('toast-order', e.message, 'error');
  }
}

document.getElementById('btn-show-add-order').addEventListener('click', () => {
  document.getElementById('form-order').classList.remove('hidden');
});

document.getElementById('btn-cancel-order').addEventListener('click', () => {
  document.getElementById('form-order').classList.add('hidden');
});

document.getElementById('form-order').addEventListener('submit', async e => {
  e.preventDefault();
  const body = {
    orderId: document.getElementById('o-orderId').value.trim(),
    customerId: document.getElementById('o-customerId').value.trim(),
    productId: document.getElementById('o-productId').value.trim(),
    quantity: parseInt(document.getElementById('o-quantity').value),
    totalPrice: parseFloat(document.getElementById('o-totalPrice').value),
    status: document.getElementById('o-status').value,
    createdAt: document.getElementById('o-createdAt').value.trim() || new Date().toISOString(),
  };
  try {
    await apiFetch('/orders', { method: 'POST', body: JSON.stringify(body) });
    showToast('toast-order', `Created order ${body.orderId}`);
    document.getElementById('form-order').classList.add('hidden');
    loadOrders();
  } catch (err) {
    showToast('toast-order', err.message, 'error');
  }
});

// ── demo panel ────────────────────────────────────────────────────────────────

// DynamoDB on-demand pricing: $0.25 per million RCUs (eventually consistent = 0.5 RCU/item)
const RCU_PRICE_PER_MILLION = 0.25;
const EVENTUALLY_CONSISTENT_RCU = 0.5;
const SCALE_REQUESTS_PER_DAY = 100_000;
const DAYS_PER_MONTH = 30;

function calcCost(items) {
  return items * EVENTUALLY_CONSISTENT_RCU * (RCU_PRICE_PER_MILLION / 1_000_000);
}

function fmtUSD(n) {
  if (n < 0.01) return `$${n.toFixed(5)}`;
  return `$${n.toFixed(2)}`;
}

function renderResult(containerId, data) {
  const box = document.getElementById(containerId);
  const scanned = data.scanned_count;
  const returned = data.returned_count;
  const warnClass = scanned > returned ? 'warn' : '';

  const rcuScanned = scanned * EVENTUALLY_CONSISTENT_RCU;
  const rcuIdeal   = returned * EVENTUALLY_CONSISTENT_RCU;
  const wastePercent = scanned > 0 ? Math.round((scanned - returned) / scanned * 100) : 0;

  const costPerOp       = calcCost(scanned);
  const costPerOpIdeal  = calcCost(returned);
  const monthlyActual   = costPerOp      * SCALE_REQUESTS_PER_DAY * DAYS_PER_MONTH;
  const monthlyIdeal    = costPerOpIdeal * SCALE_REQUESTS_PER_DAY * DAYS_PER_MONTH;
  const monthlySavings  = monthlyActual  - monthlyIdeal;

  const costBlock = scanned > returned ? `
    <div class="cost-box">
      <div class="cost-row">
        <span class="cost-label">RCUs consumed (this op)</span>
        <span class="cost-bad">${rcuScanned.toFixed(1)} RCU</span>
        <span class="cost-label">vs ideal (Query/GSI)</span>
        <span class="cost-good">${rcuIdeal.toFixed(1)} RCU</span>
        <span class="cost-waste">${wastePercent}% wasted</span>
      </div>
      <div class="cost-row">
        <span class="cost-label">At ${SCALE_REQUESTS_PER_DAY.toLocaleString()} req/day × 30 days</span>
        <span class="cost-bad">${fmtUSD(monthlyActual)}/mo (scan)</span>
        <span class="cost-arrow">→</span>
        <span class="cost-good">${fmtUSD(monthlyIdeal)}/mo (with GSI)</span>
        <span class="cost-save">save ${fmtUSD(monthlySavings)}/mo</span>
      </div>
    </div>` : '';

  box.innerHTML = `
    <div class="result-meta">
      <span><span class="meta-label">operation: </span><span class="meta-value">${data.operation}</span></span>
      <span><span class="meta-label">scanned: </span><span class="meta-value ${warnClass}">${scanned}</span></span>
      <span><span class="meta-label">returned: </span><span class="meta-value">${returned}</span></span>
    </div>
    <div class="meta-label" style="margin-bottom:8px;font-size:11px;">${data.explanation}</div>
    ${costBlock}
    ${JSON.stringify(data.items, null, 2)}`;
  box.classList.remove('hidden');
}

document.getElementById('btn-scan').addEventListener('click', async () => {
  try {
    const r = await apiFetch('/demo/scan');
    renderResult('result-scan', r);
  } catch (e) {
    document.getElementById('result-scan').textContent = e.message;
    document.getElementById('result-scan').classList.remove('hidden');
  }
});

document.getElementById('btn-filter').addEventListener('click', async () => {
  const cat = document.getElementById('filter-category').value;
  const maxPrice = document.getElementById('filter-maxPrice').value;
  const params = new URLSearchParams();
  if (cat) params.set('category', cat);
  if (maxPrice) params.set('maxPrice', maxPrice);
  try {
    const r = await apiFetch('/demo/filter?' + params.toString());
    renderResult('result-filter', r);
  } catch (e) {
    document.getElementById('result-filter').textContent = e.message;
    document.getElementById('result-filter').classList.remove('hidden');
  }
});

document.getElementById('btn-query').addEventListener('click', async () => {
  const customerId = document.getElementById('query-customerId').value;
  try {
    const r = await apiFetch(`/demo/query?customerId=${customerId}`);
    renderResult('result-query', r);
  } catch (e) {
    document.getElementById('result-query').textContent = e.message;
    document.getElementById('result-query').classList.remove('hidden');
  }
});

// ── init ──────────────────────────────────────────────────────────────────────

loadProducts();
loadOrders();
