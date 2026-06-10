/* ============================================================================
   Expense Tracker — Application Logic
   Supabase JS SDK v2 — Zero backend, direct database access with RLS
   ============================================================================ */

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CONFIGURATION — Paste your Supabase credentials here                      ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const SUPABASE_URL  = 'https://zfaiogutpwabzkxoeohe.supabase.co';
const SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpmYWlvZ3V0cHdhYnpreG9lb2hlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEwNzMzNDIsImV4cCI6MjA5NjY0OTM0Mn0.xAMWaBsGDJVCPDvUoKbL0YTG2LE7C2-WyU-w6qWQSjo';

// ── Chart.js Color Palette ──────────────────────────────────────────────────
const CHART_COLORS = [
    '#6C63FF', '#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B',
    '#10B981', '#EF4444', '#06B6D4', '#F97316', '#84CC16',
];

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  SUPABASE CLIENT                                                           ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

let supabase = null;
let supabaseReady = false;

try {
    if (window.supabase && SUPABASE_URL.startsWith('http') && SUPABASE_ANON.length > 20) {
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON);
        supabaseReady = true;
    }
} catch (e) {
    console.warn('Supabase init failed:', e.message);
}

// Global state
let currentUser = null;
let categoriesCache = [];
let pieChart = null;
let barChart = null;

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  INITIALIZATION                                                            ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

document.addEventListener('DOMContentLoaded', async () => {
    // Set default dates first (always works)
    setDefaultDates();

    // Enter key support for auth forms
    document.getElementById('loginPassword').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
    document.getElementById('regConfirm').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleRegister();
    });

    // Month pickers on change
    document.getElementById('dashboardMonth').addEventListener('change', loadDashboard);
    document.getElementById('budgetsMonth').addEventListener('change', loadBudgetsPage);

    // If Supabase is not configured, show auth page with a warning
    if (!supabaseReady) {
        showAuth();
        showToast('⚠️ Paste your Supabase URL and anon key in app.js to get started', 'error');
        return;
    }

    // Listen for auth state changes
    supabase.auth.onAuthStateChange((event, session) => {
        if (session && session.user) {
            currentUser = session.user;
            showApp();
        } else {
            currentUser = null;
            showAuth();
        }
    });

    // Check initial session
    const { data: { session } } = await supabase.auth.getSession();
    if (session && session.user) {
        currentUser = session.user;
        showApp();
    } else {
        showAuth();
    }
});


function setDefaultDates() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const monthStr = `${yyyy}-${mm}`;
    const dateStr = `${yyyy}-${mm}-${dd}`;

    document.getElementById('dashboardMonth').value = monthStr;
    document.getElementById('budgetsMonth').value = monthStr;
    document.getElementById('expDate').value = dateStr;
    document.getElementById('incDate').value = dateStr;

    // History: last 30 days
    const thirtyAgo = new Date(today);
    thirtyAgo.setDate(thirtyAgo.getDate() - 30);
    document.getElementById('histStartDate').value = formatDateISO(thirtyAgo);
    document.getElementById('histEndDate').value = dateStr;
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  AUTH FUNCTIONS                                                            ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

function switchAuthTab(tab) {
    const loginBtn  = document.getElementById('tabLogin');
    const regBtn    = document.getElementById('tabRegister');
    const loginForm = document.getElementById('loginForm');
    const regForm   = document.getElementById('registerForm');

    if (tab === 'login') {
        loginBtn.classList.add('active');
        regBtn.classList.remove('active');
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
    } else {
        regBtn.classList.add('active');
        loginBtn.classList.remove('active');
        regForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}


async function handleLogin() {
    if (!supabaseReady) {
        showToast('⚠️ Configure Supabase credentials in app.js first', 'error');
        return;
    }

    const email    = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    showToast('✅ Login successful!', 'success');
}


async function handleRegister() {
    if (!supabaseReady) {
        showToast('⚠️ Configure Supabase credentials in app.js first', 'error');
        return;
    }

    const displayName     = document.getElementById('regDisplayName').value.trim();
    const email           = document.getElementById('regEmail').value.trim();
    const password        = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirm').value;

    if (!displayName || !email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    if (displayName.length < 3) {
        showToast('Display name must be at least 3 characters', 'error');
        return;
    }
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            data: { display_name: displayName }
        }
    });
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    // If email confirmation is disabled, user is logged in immediately
    if (data.session) {
        showToast('✅ Account created! Welcome!', 'success');
    } else {
        showToast('✅ Account created! Please check your email to confirm, then log in.', 'success');
        switchAuthTab('login');
    }
}


async function handleLogout() {
    await supabase.auth.signOut();
    showToast('Logged out', 'info');
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  APP SHELL — show/hide, navigation                                        ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

function showAuth() {
    document.getElementById('authPage').classList.remove('hidden');
    document.getElementById('appShell').classList.add('hidden');
}


function showApp() {
    document.getElementById('authPage').classList.add('hidden');
    document.getElementById('appShell').classList.remove('hidden');

    // Set username in sidebar
    const name = currentUser.user_metadata?.display_name || currentUser.email;
    document.getElementById('sidebarUsername').textContent = `👤 ${name}`;

    // Load initial data
    loadCategories().then(() => {
        loadDashboard();
    });
}


function navigateTo(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === page);
    });

    // Show the target page section
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.toggle('active', section.id === `page-${page}`);
    });

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');

    // Load page-specific data
    switch (page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'add-expense':
            populateCategoryDropdown('expCategory');
            renderCategoryBadges();
            break;
        case 'add-income':
            break;
        case 'budgets':
            populateCategoryDropdown('budCategory');
            loadBudgetsPage();
            break;
        case 'history':
            populateCategoryDropdown('histCategory', true);
            loadHistoryData();
            break;
    }
}


function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CATEGORIES                                                                ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

async function loadCategories() {
    const { data, error } = await supabase
        .from('categories')
        .select('*')
        .order('name');

    if (error) {
        showToast(`Failed to load categories: ${error.message}`, 'error');
        return;
    }
    categoriesCache = data || [];
}


function populateCategoryDropdown(selectId, includeAll = false) {
    const sel = document.getElementById(selectId);
    sel.innerHTML = '';

    if (includeAll) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'All Categories';
        sel.appendChild(opt);
    }

    categoriesCache.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = cat.name;
        sel.appendChild(opt);
    });
}


function renderCategoryBadges() {
    const container = document.getElementById('categoryBadges');
    container.innerHTML = '';

    categoriesCache.forEach(cat => {
        const badge = document.createElement('span');
        badge.className = cat.user_id ? 'badge badge-custom' : 'badge badge-default';
        badge.textContent = cat.name;
        container.appendChild(badge);
    });
}


async function handleAddCategory() {
    const nameInput = document.getElementById('newCatName');
    const name = nameInput.value.trim();

    if (!name) {
        showToast('Category name is required', 'error');
        return;
    }

    // Check for duplicates locally
    const exists = categoriesCache.some(c =>
        c.name.toLowerCase() === name.toLowerCase()
    );
    if (exists) {
        showToast(`Category '${name}' already exists`, 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase
        .from('categories')
        .insert({ name, user_id: currentUser.id })
        .select()
        .single();
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    showToast(`✅ Category "${name}" created!`, 'success');
    nameInput.value = '';

    // Refresh categories
    await loadCategories();
    populateCategoryDropdown('expCategory');
    renderCategoryBadges();
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  EXPENSES                                                                  ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

async function handleAddExpense() {
    const amount     = parseFloat(document.getElementById('expAmount').value);
    const categoryId = parseInt(document.getElementById('expCategory').value);
    const date       = document.getElementById('expDate').value;
    const note       = document.getElementById('expNote').value.trim();

    if (!amount || amount <= 0) {
        showToast('Amount must be greater than zero', 'error');
        return;
    }
    if (!categoryId) {
        showToast('Please select a category', 'error');
        return;
    }
    if (!date) {
        showToast('Please select a date', 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase
        .from('expenses')
        .insert({
            amount,
            category_id: categoryId,
            date,
            note: note || null,
            user_id: currentUser.id,
        })
        .select()
        .single();
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    const catName = categoriesCache.find(c => c.id === categoryId)?.name || 'Unknown';
    showToast(`✅ Expense of ${formatCurrency(amount)} added to ${catName}!`, 'success');

    // Reset form
    document.getElementById('expAmount').value = '';
    document.getElementById('expNote').value = '';
}


async function fetchExpenses(startDate, endDate, categoryId) {
    let query = supabase
        .from('expenses')
        .select('*, categories(name)')
        .order('date', { ascending: false });

    if (startDate) query = query.gte('date', startDate);
    if (endDate)   query = query.lte('date', endDate);
    if (categoryId) query = query.eq('category_id', categoryId);

    const { data, error } = await query;
    if (error) {
        showToast(`Failed to load expenses: ${error.message}`, 'error');
        return [];
    }
    return data || [];
}


async function updateExpense(id, updates) {
    const { data, error } = await supabase
        .from('expenses')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return null;
    }
    return data;
}


async function deleteExpense(id) {
    const { error } = await supabase
        .from('expenses')
        .delete()
        .eq('id', id);

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return false;
    }
    return true;
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  INCOME                                                                    ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

async function handleAddIncome() {
    const amount = parseFloat(document.getElementById('incAmount').value);
    const source = document.getElementById('incSource').value.trim();
    const date   = document.getElementById('incDate').value;

    if (!amount || amount <= 0) {
        showToast('Amount must be greater than zero', 'error');
        return;
    }
    if (!source) {
        showToast('Please enter an income source', 'error');
        return;
    }
    if (!date) {
        showToast('Please select a date', 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase
        .from('incomes')
        .insert({
            amount,
            source,
            date,
            user_id: currentUser.id,
        })
        .select()
        .single();
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    showToast(`✅ Income of ${formatCurrency(amount)} from ${source} added!`, 'success');

    // Reset form
    document.getElementById('incAmount').value = '';
    document.getElementById('incSource').value = '';
}


async function fetchIncomes(startDate, endDate) {
    let query = supabase
        .from('incomes')
        .select('*')
        .order('date', { ascending: false });

    if (startDate) query = query.gte('date', startDate);
    if (endDate)   query = query.lte('date', endDate);

    const { data, error } = await query;
    if (error) {
        showToast(`Failed to load income: ${error.message}`, 'error');
        return [];
    }
    return data || [];
}


async function updateIncome(id, updates) {
    const { data, error } = await supabase
        .from('incomes')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return null;
    }
    return data;
}


async function deleteIncome(id) {
    const { error } = await supabase
        .from('incomes')
        .delete()
        .eq('id', id);

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return false;
    }
    return true;
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  BUDGETS                                                                   ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

async function handleSetBudget() {
    const categoryId = parseInt(document.getElementById('budCategory').value);
    const amount     = parseFloat(document.getElementById('budAmount').value);
    const month      = document.getElementById('budgetsMonth').value;

    if (!categoryId) {
        showToast('Please select a category', 'error');
        return;
    }
    if (!amount || amount <= 0) {
        showToast('Amount must be greater than zero', 'error');
        return;
    }

    showLoading();
    const { data, error } = await supabase
        .from('budgets')
        .upsert({
            user_id: currentUser.id,
            category_id: categoryId,
            amount,
            month,
        }, { onConflict: 'user_id,category_id,month' })
        .select()
        .single();
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    const catName = categoriesCache.find(c => c.id === categoryId)?.name || 'Unknown';
    showToast(`✅ Budget of ${formatCurrency(amount)} set for ${catName} in ${month}!`, 'success');

    document.getElementById('budAmount').value = '';
    loadBudgetsPage();
}


async function fetchBudgets(month) {
    const { data, error } = await supabase
        .from('budgets')
        .select('*, categories(name)')
        .eq('month', month);

    if (error) {
        showToast(`Failed to load budgets: ${error.message}`, 'error');
        return [];
    }
    return data || [];
}


async function handleDeleteBudget(id) {
    showLoading();
    const { error } = await supabase
        .from('budgets')
        .delete()
        .eq('id', id);
    hideLoading();

    if (error) {
        showToast(`❌ ${error.message}`, 'error');
        return;
    }

    showToast('Budget limit deleted!', 'success');
    loadBudgetsPage();
}


async function loadBudgetsPage() {
    const month = document.getElementById('budgetsMonth').value;
    document.getElementById('budgetMonthLabel').textContent = month;

    const budgets = await fetchBudgets(month);
    const container = document.getElementById('budgetListContainer');
    const emptyEl   = document.getElementById('budgetListEmpty');

    if (budgets.length === 0) {
        container.innerHTML = '';
        container.appendChild(emptyEl);
        emptyEl.classList.remove('hidden');
        return;
    }

    emptyEl.classList.add('hidden');

    // Build a table for configured budgets
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Budget Limit</th>
                    <th style="text-align:right">Action</th>
                </tr>
            </thead>
            <tbody>
    `;

    budgets.forEach(b => {
        const catName = b.categories?.name || 'Unknown';
        html += `
            <tr>
                <td><strong>${escapeHtml(catName)}</strong></td>
                <td>${formatCurrency(b.amount)}</td>
                <td style="text-align:right">
                    <button class="btn-icon danger" onclick="handleDeleteBudget(${b.id})" title="Remove Budget">🗑️</button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  DASHBOARD                                                                 ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

async function loadDashboard() {
    const monthStr = document.getElementById('dashboardMonth').value; // YYYY-MM
    if (!monthStr) return;

    showLoading();

    // Parse month boundaries
    const [year, month] = monthStr.split('-').map(Number);
    const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
    const lastDay   = new Date(year, month, 0).getDate();
    const endDate   = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

    // Fetch this month's data
    const [expenses, incomes] = await Promise.all([
        fetchExpenses(startDate, endDate),
        fetchIncomes(startDate, endDate),
    ]);

    const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
    const totalIncome   = incomes.reduce((sum, i) => sum + i.amount, 0);
    const netSavings    = totalIncome - totalExpenses;

    // ── Update Metric Cards ─────────────────────────────────────────────
    document.getElementById('metricIncome').textContent   = formatCurrency(totalIncome);
    document.getElementById('metricExpenses').textContent  = formatCurrency(totalExpenses);
    document.getElementById('metricSavings').textContent   = formatCurrency(netSavings);

    const deltaEl = document.getElementById('metricSavingsDelta');
    if (netSavings >= 0) {
        deltaEl.textContent = '▲ Surplus';
        deltaEl.className = 'metric-delta positive';
    } else {
        deltaEl.textContent = '▼ Deficit';
        deltaEl.className = 'metric-delta negative';
    }

    // ── Category Breakdown ──────────────────────────────────────────────
    const breakdown = computeCategoryBreakdown(expenses, totalExpenses);

    // Pie chart
    renderPieChart(breakdown);

    // Breakdown table
    const breakdownSection = document.getElementById('breakdownSection');
    const breakdownBody    = document.getElementById('breakdownBody');
    if (breakdown.length > 0) {
        breakdownSection.classList.remove('hidden');
        breakdownBody.innerHTML = breakdown.map((b, i) => `
            <tr>
                <td>${i + 1}</td>
                <td>${escapeHtml(b.category_name)}</td>
                <td>${formatCurrency(b.total)}</td>
                <td>${b.percentage.toFixed(1)}%</td>
            </tr>
        `).join('');
    } else {
        breakdownSection.classList.add('hidden');
    }

    // ── 6-Month Bar Chart ───────────────────────────────────────────────
    await renderBarChart(year, month);

    // ── Budget Progress ─────────────────────────────────────────────────
    await renderBudgetProgress(monthStr, expenses);

    hideLoading();
}


function computeCategoryBreakdown(expenses, totalExpenses) {
    const map = {};
    expenses.forEach(e => {
        const catName = e.categories?.name || 'Unknown';
        if (!map[catName]) map[catName] = 0;
        map[catName] += e.amount;
    });

    const breakdown = Object.entries(map).map(([name, total]) => ({
        category_name: name,
        total: Math.round(total * 100) / 100,
        percentage: totalExpenses > 0 ? (total / totalExpenses * 100) : 0,
    }));

    breakdown.sort((a, b) => b.total - a.total);
    return breakdown;
}


function renderPieChart(breakdown) {
    const canvas  = document.getElementById('chartPie');
    const emptyEl = document.getElementById('pieEmpty');

    if (breakdown.length === 0) {
        canvas.parentElement.style.display = 'none';
        emptyEl.classList.remove('hidden');
        if (pieChart) { pieChart.destroy(); pieChart = null; }
        return;
    }

    canvas.parentElement.style.display = 'block';
    emptyEl.classList.add('hidden');

    const labels = breakdown.map(b => b.category_name);
    const values = breakdown.map(b => b.total);
    const colors = breakdown.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]);

    if (pieChart) pieChart.destroy();

    pieChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: '#0E1117',
                borderWidth: 2,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '45%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FAFAFA',
                        font: { family: 'Inter', size: 11 },
                        padding: 15,
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    backgroundColor: '#1A1D29',
                    titleColor: '#FAFAFA',
                    bodyColor: '#9CA3AF',
                    borderColor: 'rgba(108, 99, 255, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: (ctx) => {
                            const v = ctx.parsed;
                            const pct = breakdown[ctx.dataIndex].percentage.toFixed(1);
                            return ` ${formatCurrency(v)} (${pct}%)`;
                        },
                    },
                },
            },
        },
    });
}


async function renderBarChart(currentYear, currentMonth) {
    const canvas = document.getElementById('chartBar');
    const monthsData = [];

    // Fetch 6 months of summaries
    for (let i = 5; i >= 0; i--) {
        let m = currentMonth - i;
        let y = currentYear;
        while (m <= 0) { m += 12; y--; }

        const startDate = `${y}-${String(m).padStart(2, '0')}-01`;
        const lastDay   = new Date(y, m, 0).getDate();
        const endDate   = `${y}-${String(m).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

        const [expenses, incomes] = await Promise.all([
            fetchExpenses(startDate, endDate),
            fetchIncomes(startDate, endDate),
        ]);

        const monthName = new Date(y, m - 1, 1).toLocaleString('en-US', { month: 'short', year: 'numeric' });
        monthsData.push({
            label: monthName,
            income: incomes.reduce((s, i) => s + i.amount, 0),
            expenses: expenses.reduce((s, e) => s + e.amount, 0),
        });
    }

    if (barChart) barChart.destroy();

    barChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: monthsData.map(d => d.label),
            datasets: [
                {
                    label: 'Income',
                    data: monthsData.map(d => d.income),
                    backgroundColor: '#10B981',
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Expenses',
                    data: monthsData.map(d => d.expenses),
                    backgroundColor: '#EF4444',
                    borderRadius: 6,
                    borderSkipped: false,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FAFAFA',
                        font: { family: 'Inter' },
                        padding: 15,
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    backgroundColor: '#1A1D29',
                    titleColor: '#FAFAFA',
                    bodyColor: '#9CA3AF',
                    borderColor: 'rgba(108, 99, 255, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: 'rgba(108, 99, 255, 0.08)' },
                    ticks: { color: '#9CA3AF', font: { family: 'Inter' } },
                },
                y: {
                    grid: { color: 'rgba(108, 99, 255, 0.08)' },
                    ticks: {
                        color: '#9CA3AF',
                        font: { family: 'Inter' },
                        callback: (v) => formatCurrencyShort(v),
                    },
                    beginAtZero: true,
                },
            },
        },
    });
}


async function renderBudgetProgress(monthStr, expenses) {
    const section = document.getElementById('budgetProgressSection');
    const container = document.getElementById('budgetProgressBars');

    const budgets = await fetchBudgets(monthStr);

    if (budgets.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');

    // Aggregate expenses by category
    const spentByCategory = {};
    expenses.forEach(e => {
        spentByCategory[e.category_id] = (spentByCategory[e.category_id] || 0) + e.amount;
    });

    let html = '';
    budgets.forEach(b => {
        const catName    = b.categories?.name || 'Unknown';
        const spent      = spentByCategory[b.category_id] || 0;
        const percentage = b.amount > 0 ? (spent / b.amount * 100) : 0;
        const clamped    = Math.min(percentage, 100);

        let fillClass, badgeHtml;
        if (percentage <= 80) {
            fillClass = 'safe';
            badgeHtml = `<span class="progress-badge-safe">✅ Safe (${percentage.toFixed(1)}%)</span>`;
        } else if (percentage <= 100) {
            fillClass = 'warning';
            badgeHtml = `<span class="progress-badge-warning">⚠️ Approaching Limit (${percentage.toFixed(1)}%)</span>`;
        } else {
            fillClass = 'danger';
            const over = spent - b.amount;
            badgeHtml = `<span class="progress-badge-danger">🚨 Exceeded by ${formatCurrency(over)} (${percentage.toFixed(1)}%)</span>`;
        }

        html += `
            <div class="progress-item">
                <div class="progress-header">
                    <span class="progress-label">${escapeHtml(catName)}</span>
                    <div class="progress-stats">
                        <span class="progress-amount">${formatCurrency(spent)} of ${formatCurrency(b.amount)}</span>
                        ${badgeHtml}
                    </div>
                </div>
                <div class="progress-track">
                    <div class="progress-fill ${fillClass}" style="width: ${clamped}%"></div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  HISTORY                                                                   ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

function switchHistoryTab(tab) {
    document.querySelectorAll('#page-history .tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase().includes(tab));
    });
    document.getElementById('histTab-expenses').classList.toggle('active', tab === 'expenses');
    document.getElementById('histTab-income').classList.toggle('active', tab === 'income');
}


async function loadHistoryData() {
    const startDate  = document.getElementById('histStartDate').value;
    const endDate    = document.getElementById('histEndDate').value;
    const categoryId = document.getElementById('histCategory').value || null;

    showLoading();
    const [expenses, incomes] = await Promise.all([
        fetchExpenses(startDate, endDate, categoryId),
        fetchIncomes(startDate, endDate),
    ]);
    hideLoading();

    renderExpensesList(expenses);
    renderIncomesList(incomes);
}


function renderExpensesList(expenses) {
    const listEl     = document.getElementById('expensesList');
    const emptyEl    = document.getElementById('expensesEmpty');
    const statsBar   = document.getElementById('expenseStatsBar');
    const countEl    = document.getElementById('expenseCount');
    const totalEl    = document.getElementById('expenseTotal');

    if (expenses.length === 0) {
        listEl.innerHTML = '';
        emptyEl.classList.remove('hidden');
        statsBar.classList.add('hidden');
        return;
    }

    emptyEl.classList.add('hidden');
    statsBar.classList.remove('hidden');

    const total = expenses.reduce((s, e) => s + e.amount, 0);
    countEl.textContent = expenses.length;
    totalEl.textContent = `Total: ${formatCurrency(total)}`;

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Date</th>
                    <th>Note</th>
                    <th style="text-align:right">Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    expenses.forEach(e => {
        const catName = e.categories?.name || 'Unknown';
        html += `
            <tr id="expense-row-${e.id}">
                <td><strong>${formatCurrency(e.amount)}</strong></td>
                <td><span class="badge badge-accent">${escapeHtml(catName)}</span></td>
                <td>📅 ${e.date}</td>
                <td class="text-muted">${escapeHtml(e.note || '—')}</td>
                <td style="text-align:right">
                    <button class="btn-icon" onclick="showEditExpense(${e.id}, ${e.amount}, ${e.category_id}, '${e.date}', '${escapeAttr(e.note || '')}')" title="Edit">✏️</button>
                    <button class="btn-icon danger" onclick="confirmDeleteExpense(${e.id})" title="Delete">🗑️</button>
                </td>
            </tr>
            <tr id="expense-edit-${e.id}" class="hidden">
                <td colspan="5">
                    <div class="edit-row">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Amount</label>
                                <input class="form-input" type="number" id="editExpAmt-${e.id}" value="${e.amount}" min="0.01" step="0.5">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Category</label>
                                <select class="form-select" id="editExpCat-${e.id}">
                                    ${categoriesCache.map(c => `<option value="${c.id}" ${c.id === e.category_id ? 'selected' : ''}>${escapeHtml(c.name)}</option>`).join('')}
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Note</label>
                                <input class="form-input" type="text" id="editExpNote-${e.id}" value="${escapeAttr(e.note || '')}">
                            </div>
                        </div>
                        <div class="edit-actions">
                            <button class="btn btn-primary btn-sm" onclick="saveEditExpense(${e.id})">💾 Save</button>
                            <button class="btn btn-secondary btn-sm" onclick="cancelEditExpense(${e.id})">❌ Cancel</button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    listEl.innerHTML = html;
}


function showEditExpense(id) {
    document.getElementById(`expense-edit-${id}`).classList.remove('hidden');
}

function cancelEditExpense(id) {
    document.getElementById(`expense-edit-${id}`).classList.add('hidden');
}

async function saveEditExpense(id) {
    const amount     = parseFloat(document.getElementById(`editExpAmt-${id}`).value);
    const categoryId = parseInt(document.getElementById(`editExpCat-${id}`).value);
    const note       = document.getElementById(`editExpNote-${id}`).value.trim();

    if (!amount || amount <= 0) {
        showToast('Amount must be greater than zero', 'error');
        return;
    }

    showLoading();
    const result = await updateExpense(id, {
        amount,
        category_id: categoryId,
        note: note || null,
    });
    hideLoading();

    if (result) {
        showToast('Expense updated!', 'success');
        loadHistoryData();
    }
}

async function confirmDeleteExpense(id) {
    if (!confirm('Delete this expense?')) return;
    showLoading();
    const success = await deleteExpense(id);
    hideLoading();
    if (success) {
        showToast('Expense deleted!', 'success');
        loadHistoryData();
    }
}


function renderIncomesList(incomes) {
    const listEl   = document.getElementById('incomesList');
    const emptyEl  = document.getElementById('incomesEmpty');
    const statsBar = document.getElementById('incomeStatsBar');
    const countEl  = document.getElementById('incomeCount');
    const totalEl  = document.getElementById('incomeTotal');

    if (incomes.length === 0) {
        listEl.innerHTML = '';
        emptyEl.classList.remove('hidden');
        statsBar.classList.add('hidden');
        return;
    }

    emptyEl.classList.add('hidden');
    statsBar.classList.remove('hidden');

    const total = incomes.reduce((s, i) => s + i.amount, 0);
    countEl.textContent = incomes.length;
    totalEl.textContent = `Total: ${formatCurrency(total)}`;

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Amount</th>
                    <th>Source</th>
                    <th>Date</th>
                    <th style="text-align:right">Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    incomes.forEach(inc => {
        html += `
            <tr id="income-row-${inc.id}">
                <td><strong>${formatCurrency(inc.amount)}</strong></td>
                <td><span class="badge badge-green">${escapeHtml(inc.source)}</span></td>
                <td>📅 ${inc.date}</td>
                <td style="text-align:right">
                    <button class="btn-icon" onclick="showEditIncome(${inc.id})" title="Edit">✏️</button>
                    <button class="btn-icon danger" onclick="confirmDeleteIncome(${inc.id})" title="Delete">🗑️</button>
                </td>
            </tr>
            <tr id="income-edit-${inc.id}" class="hidden">
                <td colspan="4">
                    <div class="edit-row">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Amount</label>
                                <input class="form-input" type="number" id="editIncAmt-${inc.id}" value="${inc.amount}" min="0.01">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Source</label>
                                <input class="form-input" type="text" id="editIncSrc-${inc.id}" value="${escapeAttr(inc.source)}">
                            </div>
                        </div>
                        <div class="edit-actions">
                            <button class="btn btn-primary btn-sm" onclick="saveEditIncome(${inc.id})">💾 Save</button>
                            <button class="btn btn-secondary btn-sm" onclick="cancelEditIncome(${inc.id})">❌ Cancel</button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    listEl.innerHTML = html;
}


function showEditIncome(id) {
    document.getElementById(`income-edit-${id}`).classList.remove('hidden');
}

function cancelEditIncome(id) {
    document.getElementById(`income-edit-${id}`).classList.add('hidden');
}

async function saveEditIncome(id) {
    const amount = parseFloat(document.getElementById(`editIncAmt-${id}`).value);
    const source = document.getElementById(`editIncSrc-${id}`).value.trim();

    if (!amount || amount <= 0) {
        showToast('Amount must be greater than zero', 'error');
        return;
    }
    if (!source) {
        showToast('Source is required', 'error');
        return;
    }

    showLoading();
    const result = await updateIncome(id, { amount, source });
    hideLoading();

    if (result) {
        showToast('Income updated!', 'success');
        loadHistoryData();
    }
}

async function confirmDeleteIncome(id) {
    if (!confirm('Delete this income entry?')) return;
    showLoading();
    const success = await deleteIncome(id);
    hideLoading();
    if (success) {
        showToast('Income deleted!', 'success');
        loadHistoryData();
    }
}


// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  UI UTILITIES                                                              ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

function formatCurrency(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function formatCurrencyShort(amount) {
    if (amount >= 100000) return '₹' + (amount / 100000).toFixed(1) + 'L';
    if (amount >= 1000)   return '₹' + (amount / 1000).toFixed(1) + 'K';
    return '₹' + amount;
}

function formatDateISO(d) {
    const yyyy = d.getFullYear();
    const mm   = String(d.getMonth() + 1).padStart(2, '0');
    const dd   = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeAttr(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    // Auto-remove after animation
    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 4000);
}
