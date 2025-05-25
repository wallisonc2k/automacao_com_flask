// Estado da aplicação
let pallets = [];
let currentPallet = null;
let currentItem = null;
let editMode = false;

// Elementos DOM
const palletList = document.getElementById('pallet-list');
const addPalletBtn = document.getElementById('add-pallet-btn');
const filterBtn = document.getElementById('filter-btn');
const palletModalOverlay = document.getElementById('pallet-modal-overlay');
const itemModalOverlay = document.getElementById('item-modal-overlay');
const modalClose = document.getElementById('modal-close');
const itemModalClose = document.getElementById('item-modal-close');
const savePalletBtn = document.getElementById('save-pallet-btn');
const imprimirPalletBtn = document.getElementById('imprimir-pallet-btn');
const saveItemBtn = document.getElementById('save-item-btn');
const deletePalletBtn = document.getElementById('delete-pallet-btn');
const addItemBtn = document.getElementById('add-item-btn');
const itemContainer = document.getElementById('item-container');
const tabButtons = document.querySelectorAll('.tab-button');
const loading = document.getElementById('loading');

// Event Listeners
document.addEventListener('DOMContentLoaded', init);
addPalletBtn.addEventListener('click', () => openPalletModal());
filterBtn.addEventListener('click', filterPallets);
modalClose.addEventListener('click', closePalletModal);
itemModalClose.addEventListener('click', closeItemModal);
savePalletBtn.addEventListener('click', savePallet);
imprimirPalletBtn.addEventListener('click', imprimirPallet)
saveItemBtn.addEventListener('click', saveItem);
deletePalletBtn.addEventListener('click', deletePallet);
addItemBtn.addEventListener('click', () => openItemModal());

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and panels
        tabButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        
        // Add active class to clicked button and corresponding panel
        button.classList.add('active');
        document.getElementById(`tab-${button.dataset.tab}`).classList.add('active');
    });
});

// Funções de inicialização
function init() {
    loadPallets();
    preencherSelects();
}

// API Functions
async function loadPallets(filters = {}) {
    showLoading();
    try {
        let url = `${API_BASE_URL}/pallets`;
        
        // Add query params for filters
        const queryParams = new URLSearchParams();
        if (filters.cliente) queryParams.append('cliente', filters.cliente);
        if (filters.tipo_de_caixa) queryParams.append('tipo_de_caixa', filters.tipo_de_caixa);
        if (filters.data_inicial) queryParams.append('data_inicial', filters.data_inicial);
        if (filters.data_final) queryParams.append('data_final', filters.data_final);
        
        const queryString = queryParams.toString();
        if (queryString) {
            url += `?${queryString}`;
        }
        
        // In a real application, you would fetch the data from the API
        // For this example, we'll use mock data
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load pallets');
        const data = await response.json();
        pallets = data.pallets;
        
        populateSelect("caixa-filter", data.filtros.tipos_de_caixa, "Selecione o tipo de caixa");
        populateSelect("cliente-filter", data.filtros.clientes, "Selecione o cliente");
        renderPallets();
    } catch (error) {
        showToast('Erro ao carregar pallets: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
    * Preenche um <select> com options a partir de um array de itens.
    *
    * @param {string} selectId - id do elemento <select> no DOM
    * @param {Array<{ valor: any, texto: string }>} items - lista de opções
    * @param {string} [placeholderText] - texto da opção placeholder (opcional)
    */
function populateSelect(selectId, items, placeholderText) {
    const selectEl = document.getElementById(selectId);
    if (!selectEl) {
        console.error(`populateSelect: nenhum <select> encontrado com id="${selectId}"`);
        return;
    }

    // Limpa as options existentes
    selectEl.innerHTML = "";

    // Se houver texto de placeholder, adiciona uma opção desabilitada no topo
    if (placeholderText) {
        const placeholderOpt = document.createElement("option");
        placeholderOpt.value = "";
        placeholderOpt.textContent = placeholderText;
        placeholderOpt.selected = true;
        placeholderOpt.disabled = true;
        selectEl.appendChild(placeholderOpt);
    }

    // Cria e adiciona as opções
    items.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.valor;
        opt.textContent = item.texto;
        selectEl.appendChild(opt);
    });
}


async function preencherSelects() {
    for (const campo of CAMPOS_SELECT) {
        try {
            const response = await fetch(`${API_BASE_URL}/configuracoes/${campo}`);
            if (!response.ok) {
                console.warn(`Erro ao buscar ${campo}: ${response.statusText}`);
                continue;
            }

            const data = await response.json();
            const options = data.valor_json;
            const selectEl = document.getElementById(campo.replace(/_/g, '-'));

            if (selectEl && options) {
                // Limpa as opções atuais
                selectEl.innerHTML = '<option value="">Selecione</option>';

                // Adiciona novas opções
                for (const [value, label] of Object.entries(options)) {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    selectEl.appendChild(option);


                }
            }
        } catch (error) {
            console.error(`Erro ao carregar ${campo}:`, error);
        }
    }
}

async function getPalletById(id) {
    showLoading();
    try {
        // In a real application, fetch from API
        const response = await fetch(`${API_BASE_URL}/pallets/${id}`);
        if (!response.ok) throw new Error('Failed to load pallet details');
        return await response.json();
        
        // For demo, return from mock data
        // const pallet = pallets.find(p => p.id === id);
        // if (!pallet) throw new Error('Pallet não encontrado');
        // return pallet;
    } catch (error) {
        showToast('Erro ao carregar detalhes do pallet: ' + error.message, 'error');
        return null;
    } finally {
        hideLoading();
    }
}

async function createPallet(palletData) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(palletData)
        });
        if (!response.ok) throw new Error('Failed to create pallet');
        return await response.json();
        
        // For demo, just add to mock data
        // const newId = pallets.length > 0 ? Math.max(...pallets.map(p => p.id)) + 1 : 1;
        // const newPallet = {
        //     id: newId,
        //     ...palletData,
        //     data_criacao: new Date().toISOString()
        // };
        // pallets.push(newPallet);
        // return newPallet;
    } catch (error) {
        showToast('Erro ao criar pallet: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function createPalletGvsSystem(palletData) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets/lancar_pallet_gvssystem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(palletData)
        });
        if (!response.ok) throw new Error('Falha ao criar pallet no GvsSystem');
        return await response.json();
    
    } catch (error) {
        showToast('Erro ao criar pallet: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function updatePallet(id, palletData) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(palletData)
        });
        if (!response.ok) throw new Error('Failed to update pallet');
        return await response.json();
        
        // For demo, update in mock data
        // const index = pallets.findIndex(p => p.id === id);
        // if (index === -1) throw new Error('Pallet não encontrado');
        // pallets[index] = {
        //     ...pallets[index],
        //     ...palletData
        // };
        // return pallets[index];
    } catch (error) {
        showToast('Erro ao atualizar pallet: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function deletePalletById(id) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete pallet');
        
        // For demo, remove from mock data
        // const index = pallets.findIndex(p => p.id === id);
        // if (index === -1) throw new Error('Pallet não encontrado');
        // pallets.splice(index, 1);
        // return true;
    } catch (error) {
        showToast('Erro ao excluir pallet: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function addItemToPallet(palletId, itemData) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets/${palletId}/itens`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(itemData)
        });
        if (!response.ok) throw new Error('Failed to add item');
        return await response.json();
        
        // For demo, add to mock data
        // const pallet = pallets.find(p => p.id === palletId);
        // if (!pallet) throw new Error('Pallet não encontrado');
        
        // const newItemId = pallet.itens.length > 0 
        //     ? Math.max(...pallet.itens.map(i => i.id)) + 1 
        //     : 1;
        
        // const newItem = {
        //     id: newItemId,
        //     ...itemData
        // };
        
        // pallet.itens.push(newItem);
        // return newItem;
    } catch (error) {
        showToast('Erro ao adicionar item: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function deleteItem(itemId) {
    showLoading();
    try {
        // In a real application, send to API
        const response = await fetch(`${API_BASE_URL}/pallets/itens/${itemId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete item');
    
    } catch (error) {
        showToast('Erro ao excluir item: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// UI Functions
function renderPallets() {
    palletList.innerHTML = '';
    
    if (pallets.length === 0) {
        palletList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <h3>Nenhum pallet encontrado</h3>
                <p>Clique em "Novo Pallet" para adicionar um pallet.</p>
            </div>
        `;
        return;
    }
    
    pallets.forEach(pallet => {
        const totalCaixas = pallet.itens.reduce((sum, item) => sum + item.q_caixas, 0);
        const card = document.createElement('div');
        card.className = 'pallet-card';
        card.innerHTML = `
            <div class="pallet-header">
                <h3>Pallet #${pallet.id}</h3>
            </div>
            <div class="pallet-body">
                <div class="pallet-info"><strong>Produto:</strong> ${pallet.cabecalho.tex_descProduto}</div>
                <div class="pallet-info"><strong>Cliente:</strong> ${pallet.cabecalho.tex_cliente}</div>
                <div class="pallet-info"><strong>Caixas:</strong> ${totalCaixas}</div>
                <div class="pallet-info"><strong>Processo:</strong> ${pallet.cabecalho.processo_interno}</div>
                <div class="pallet-info"><strong>Pallets:</strong> ${pallet.cabecalho.q_pallets}</div>
                <div class="pallet-info"><strong>Data:</strong> ${new Date(pallet.data_criacao).toLocaleDateString()}</div>
            </div>
            <div class="pallet-footer">
                <span class="badge badge-success">${pallet.itens.length} itens</span>
                <button class="btn btn-sm btn-primary view-btn">Ver Detalhes</button>
            </div>
        `;
        
        card.querySelector('.view-btn').addEventListener('click', () => openPalletModal(pallet.id));
        palletList.appendChild(card);
    });
}

function renderItems() {
    if (!currentPallet) return;
    
    itemContainer.innerHTML = '';
    
    if (currentPallet.itens.length === 0) {
        itemContainer.innerHTML = `
            <div class="empty-state">
                <p>Nenhum item adicionado</p>
                <p>Clique em "Adicionar Item" para incluir itens ao pallet.</p>
            </div>
        `;
        return;
    }
    
    currentPallet.itens.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'item-card';
        itemElement.innerHTML = `
            <button class="item-delete" data-id="${item.id}">&times;</button>
            <div class="item-row">
                <strong>Esteira:</strong> ${item.tex_esteira}
                <strong>Latada:</strong> ${item.latada}
            </div>
            <div class="item-row">
                <strong>Caixas:</strong> ${item.q_caixas}
                <strong>Cor:</strong> ${item.cor}
            </div>
            <div class="item-row">
                <strong>Calibre:</strong> ${item.calibre}
                <strong>Brix:</strong> ${item.brix}
            </div>
            ${item.observacoes ? `<div class="item-row"><strong>Obs:</strong> ${item.observacoes}</div>` : ''}
        `;
        
        // Add event listeners
        itemElement.querySelector('.item-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            const itemId = parseInt(e.target.dataset.id);
            confirmDeleteItem(itemId);
        });
        
        itemElement.addEventListener('click', () => {
            openItemModal(item.id);
        });
        
        itemContainer.appendChild(itemElement);
    });
}

function fillPalletForm(pallet) {
    document.getElementById('pallet-id').value = pallet.id || '';
    document.getElementById('tipo-caixa').value = pallet.cabecalho.tipo_de_caixa || '';
    document.getElementById('produto').value = pallet.cabecalho.des_produto || '';
    document.getElementById('cliente').value = pallet.cabecalho.cliente || '';
    document.getElementById('tipo-etiqueta').value = pallet.cabecalho.tipo_de_etiqueta || '';
    document.getElementById('local-estoque').value = pallet.cabecalho.local_de_estoque || '';
    document.getElementById('processo-interno').value = pallet.cabecalho.processo_interno || '';
    document.getElementById('q_pallets').value = pallet.cabecalho.q_pallets || '';
}

function fillItemForm(item) {
    document.getElementById('item-id').value = item.id || '';
    document.getElementById('esteira').value = item.esteira || '';
    document.getElementById('latada').value = item.latada || '';
    document.getElementById('q-caixas').value = item.q_caixas || '';
    document.getElementById('cor').value = item.cor || '';
    document.getElementById('calibre').value = item.calibre || '';
    document.getElementById('brix').value = item.brix || '';
    document.getElementById('observacoes').value = item.observacoes || '';
}

function getPalletFormData() {
    return {
        cabecalho: {
            tipo_de_caixa: parseInt(document.getElementById('tipo-caixa').value),
            tex_tipoCaixa: document.getElementById('tipo-caixa').options[document.getElementById('tipo-caixa').selectedIndex].text,
            des_produto: parseInt(document.getElementById('produto').value),
            tex_descProduto: document.getElementById('produto').options[document.getElementById('produto').selectedIndex].text,
            cliente: parseInt(document.getElementById('cliente').value),
            tex_cliente: document.getElementById('cliente').options[document.getElementById('cliente').selectedIndex].text,
            tipo_de_etiqueta: parseInt(document.getElementById('tipo-etiqueta').value),
            tex_tipoEtiqueta: document.getElementById('tipo-etiqueta').options[document.getElementById('tipo-etiqueta').selectedIndex].text,
            local_de_estoque: parseInt(document.getElementById('local-estoque').value),
            tex_localEstoque: document.getElementById('local-estoque').options[document.getElementById('local-estoque').selectedIndex].text,
            processo_interno: document.getElementById('processo-interno').value,
            q_pallets: document.getElementById('q_pallets').value
        },
        itens: currentPallet ? [...currentPallet.itens] : []
    };
}

function getItemFormData() {
    const esteiraElement = document.getElementById('esteira');
    const latadaElement = document.getElementById('latada');
    const calibre = parseInt(document.getElementById('calibre').value);
    const brix = parseInt(document.getElementById('brix').value);

    return {
        esteira: parseInt(esteiraElement.value) || 0,
        tex_esteira: esteiraElement.options[esteiraElement.selectedIndex].text,
        latada: latadaElement.value.toString(), // 👈 garantir string
        q_caixas: parseInt(document.getElementById('q-caixas').value) || 0,
        cor: document.getElementById('cor').value || "",
        calibre: isNaN(calibre) ? 0 : calibre, // 👈 evitar NaN
        brix: isNaN(brix) ? 0 : brix,           // 👈 evitar NaN
        observacoes: document.getElementById('observacoes').value || ""
    };
}


// Modal Functions
async function openPalletModal(palletId = null) {
    editMode = !!palletId;
    
    // Reset form
    document.getElementById('pallet-form').reset();
    
    // Reset tabs
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    document.querySelector('.tab-button[data-tab="info"]').classList.add('active');
    document.getElementById('tab-info').classList.add('active');
    
    if (editMode) {
        // Load pallet details
        currentPallet = await getPalletById(palletId);
        if (!currentPallet) return;
        
        document.getElementById('modal-title').textContent = `Editar Pallet #${palletId}`;
        fillPalletForm(currentPallet);
        renderItems();
        deletePalletBtn.style.display = 'block';
        imprimirPalletBtn.style.display = 'block';
    } else {
        // New pallet
        currentPallet = {
            cabecalho: {},
            itens: []
        };
        document.getElementById('modal-title').textContent = 'Novo Pallet';
        itemContainer.innerHTML = '';
        deletePalletBtn.style.display = 'none';
        imprimirPalletBtn.style.display = 'none';
    }
    
    // Show modal
    palletModalOverlay.classList.add('active');
}

function closePalletModal() {
    palletModalOverlay.classList.remove('active');
    currentPallet = null;
}

function openItemModal(itemId = null) {
    if (!currentPallet) return;
    
    // Reset form
    document.getElementById('item-form').reset();
    
    if (itemId) {
        // Edit existing item
        currentItem = currentPallet.itens.find(item => item.id === itemId);
        if (!currentItem) return;
        
        document.getElementById('item-modal-title').textContent = 'Editar Item';
        fillItemForm(currentItem);
    } else {
        // New item
        currentItem = null;
        document.getElementById('item-modal-title').textContent = 'Adicionar Item';
    }
    
    // Show modal
    itemModalOverlay.classList.add('active');
}

function closeItemModal() {
    itemModalOverlay.classList.remove('active');
    currentItem = null;
}

// Action Functions
async function savePallet() {
    try {
        if (!validatePalletForm()) return;
        
        const palletData = getPalletFormData();
        
        if (editMode) {
            // Update existing pallet
            await updatePallet(currentPallet.id, palletData);
            showToast('Pallet atualizado com sucesso', 'success');
        } else {
            // Create new pallet
            await createPallet(palletData);
            showToast('Pallet criado com sucesso', 'success');
        }
        
        closePalletModal();
        loadPallets();
    } catch (error) {
        showToast('Erro ao salvar pallet: ' + error.message, 'error');
    }
}

async function imprimirPallet() {
    try {
        if (!validatePalletForm()) return;
        
        const palletData = getPalletFormData();
        
        // Create new pallet in GvsSystem
        await createPalletGvsSystem(palletData);
        showToast('Pallet criado com sucesso no GvsSystem', 'success');

        
        closePalletModal();
        loadPallets();
    } catch (error) {
        showToast('Erro ao imprimir pallet: ' + error.message, 'error');
    }
}


async function saveItem() {
    try {
        if (!validateItemForm()) return;
        
        const itemData = getItemFormData();
        
        if (currentItem) {
            // Update existing item
            const index = currentPallet.itens.findIndex(i => i.id === currentItem.id);
            if (index !== -1) {
                currentPallet.itens[index] = {
                    ...currentPallet.itens[index],
                    ...itemData
                };
                showToast('Item atualizado com sucesso', 'success');
            }
        } else {
            // Add new item
            const response = await addItemToPallet(currentPallet.id, itemData);
            currentPallet.itens.push(response.data);
            showToast('Item adicionado com sucesso', 'success');
        }
        
        closeItemModal();
        renderItems();
    } catch (error) {
        showToast('Erro ao salvar item: ' + error.message, 'error');
    }
}

async function deletePallet() {
    if (!currentPallet) return;
    
    if (confirm(`Tem certeza que deseja excluir o Pallet #${currentPallet.id}?`)) {
        try {
            await deletePalletById(currentPallet.id);
            showToast('Pallet excluído com sucesso', 'success');
            closePalletModal();
            loadPallets();
        } catch (error) {
            showToast('Erro ao excluir pallet: ' + error.message, 'error');
        }
    }
}

async function confirmDeleteItem(itemId) {
    if (confirm('Tem certeza que deseja excluir este item?')) {
        try {
            await deleteItem(itemId);
            showToast('Item excluído com sucesso', 'success');
            
            // Update current pallet item list
            if (currentPallet) {
                currentPallet.itens = currentPallet.itens.filter(i => i.id !== itemId);
                renderItems();
            }
        } catch (error) {
            showToast('Erro ao excluir item: ' + error.message, 'error');
        }
    }
}

function filterPallets() {
    const cliente = document.getElementById('cliente-filter').value;
    const tipo_de_caixa = document.getElementById('caixa-filter').value;
    const dataInicial = document.getElementById('data-inicial-filter').value;
    const dataFinal = document.getElementById('data-final-filter').value;
    
    loadPallets({
        cliente,
        tipo_de_caixa,
        data_inicial: dataInicial,
        data_final: dataFinal
    });
}

// Validation Functions
function validatePalletForm() {
    const form = document.getElementById('pallet-form');
    return form.checkValidity();
}

function validateItemForm() {
    const form = document.getElementById('item-form');
    return form.checkValidity();
}

// Helper Functions
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function showLoading() {
    loading.classList.add('active');
}

function hideLoading() {
    loading.classList.remove('active');
}
function toggleFilters() {
    const filters = document.querySelector('.responsive-filters');
    filters.classList.toggle('show');
}