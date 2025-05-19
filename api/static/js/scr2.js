// Função para apagar uma linha da tabela
function apagar_linha(botao) {
    var linha = botao.parentNode.parentNode;
    var id = linha.getAttribute('data-id'); // Obtém o ID da linha

    linha.parentNode.removeChild(linha); // Remove a linha da tabela

    // Remove o card correspondente
    apagar_card_por_id(id);
}

// Função para apagar um card
function apagar_card(botao) {
    var card = botao.closest('.card');
    var id = card.getAttribute('data-id'); // Obtém o ID do card

    // Remove o card
    card.parentNode.removeChild(card);

    // Remove a linha da tabela correspondente
    apagar_linha_por_id(id);
}

// Função para apagar um card pelo ID
function apagar_card_por_id(id) {
    const card = document.querySelector(`.card[data-id='${id}']`);
    if (card) {
        deletePallet(id)
        card.parentNode.removeChild(card);
    }
}

// Função para apagar uma linha da tabela pelo ID
function apagar_linha_por_id(id) {
    const linha = document.querySelector(`tr[data-id='${id}']`);
    if (linha) {
        deletePallet(id)
        linha.parentNode.removeChild(linha);
    }
}

const deletePallet = async (id) => {
    try {
        const response = await fetch(`/apagar_pallet/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            console.log('Item deletado com sucesso!');
        } else {
            console.error('Erro ao deletar o item:', response.statusText);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
};

function imprimirLinha(botao){
    var linha = botao.parentNode.parentNode;
    const dados_pallet = extrairDados(linha);
    lancarPallet(dados_pallet);

}

function imprimirCard(botao){
    var card = botao.closest('.card');
    var id = card.getAttribute('data-id');
    const linha = document.querySelector(`tr[data-id='${id}']`);
    
    const dados_pallet = extrairDados(linha);
    lancarPallet(dados_pallet);
    console.log(dados_pallet);

}


// Função para extrair dados de uma linha e enviar para o Python
function extrairDados(linha) {
    
    var colunas = linha.getElementsByTagName("td");

    var dados_pallets = {
        id: linha.dataset.id,
        tipo_de_caixa: colunas[0].textContent,
        des_produto: colunas[1].textContent,
        cliente: colunas[2].textContent,
        tipo_de_etiqueta: colunas[3].textContent,
        esteira: colunas[4].textContent,
        latada: colunas[5].textContent,
        q_caixas: colunas[6].textContent,
        cor: colunas[7].textContent,
        calibre: colunas[8].textContent,
        brix: colunas[9].textContent,
        q_pallets: colunas[10].textContent,
        local_de_estoque: colunas[11].textContent,
        processo_interno: colunas[12].textContent,
        observacoes: colunas[13].textContent,
        tex_tipoCaixa: colunas[14].textContent,
        tex_descProduto: colunas[15].textContent,
        tex_cliente: colunas[16].textContent,
        tex_tipoEtiqueta: colunas[17].textContent,
        tex_esteira: colunas[18].textContent,
        tex_localEstoque: colunas[25].textContent
    };
    return dados_pallets;
}

// Função para enviar dados para o Python
function lancarPallet(dados_pallets) {
    fetch('/processar_dados', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados_pallets)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Dados processados pelo Python:", data);
    })
    .catch(error => {
        console.error("Erro ao enviar dados para Python:", error);
    });
}

// Funcao para editar um card

function editarcard(botao){
    var card = botao.closest('.card');
    var id = card.getAttribute('data-id');
    const linha = document.querySelector(`tr[data-id='${id}']`);
    
    prencherFormulario(linha)
}

// Função para editar uma linha da tabela
function editarLinha(btn) {
    const linha = btn.parentNode.parentNode;
    prencherFormulario(linha)
}


function prencherFormulario(linha){
    const cells = linha.getElementsByTagName('td');

    document.getElementById('tipoCaixa').value = cells[0].textContent;
    document.getElementById('descProduto').value = cells[1].textContent;
    document.getElementById('cliente').value = cells[2].textContent;
    document.getElementById('tipoEtiqueta').value = cells[3].textContent;
    document.getElementById('esteira').value = cells[4].textContent;
    document.getElementById('latada').value = cells[5].textContent;
    document.getElementById('qCaixas').value = cells[6].textContent;
    document.getElementById('cor').value = cells[7].textContent;
    document.getElementById('calibre').value = cells[8].textContent;
    document.getElementById('brix').value = cells[9].textContent;
    document.getElementById('qntPallets').value = cells[10].textContent;
    document.getElementById('localEstoque').value = cells[11].textContent;

    const processoInternoRadios = document.getElementsByName('ProcessoInterno');
    processoInternoRadios.forEach(radio => {
        if (radio.value === cells[12].textContent) {
            radio.checked = true;
        }
    });
    
    // Preenchendo observacoes
    const selectObservacoes = document.getElementById('observacoes');
    const selectedValues = cells[13].textContent.split("+")
    Array.from(selectObservacoes.options).forEach(option => {
        if (selectedValues.includes(option.value)){
            option.selected = true;
        } else {
            option.selected = false;
        };
    });

    document.getElementById('formPreenchimento').dataset.editarRow = linha.rowIndex;
    const modal = new bootstrap.Modal(document.getElementById('formModal'));
    modal.show();
}


// Função para obter o valor e texto de um campo select
function obterValorTexto(selectid) {
    const camposelect = document.getElementById(selectid);
    const valorSelecionado = camposelect.value;
    const textoSelecionado = camposelect.options[camposelect.selectedIndex].text;

    return [valorSelecionado, textoSelecionado];
}

// Função para obter o valor selecionado dos radios
function getSelectedValue() {
    const radios = document.getElementsByName('ProcessoInterno');
    let selectedValue;

    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            selectedValue = radios[i].value;
            break;
        }
    }

    return selectedValue;
}

// Evento de submit do formulário
document.getElementById('formPreenchimento').addEventListener('submit', function (event) {
    event.preventDefault();

    // Coleta os valores dos campos do formulário
    const [tipoCaixa, tex_tipoCaixa] = obterValorTexto('tipoCaixa');
    const [descProduto, tex_descProduto] = obterValorTexto('descProduto');
    const [cliente, tex_cliente] = obterValorTexto('cliente');
    const [tipoEtiqueta, tex_tipoEtiqueta] = obterValorTexto('tipoEtiqueta');
    const [esteira, tex_esteira] = obterValorTexto('esteira');
    const latada = document.getElementById('latada').value;
    const qCaixas = document.getElementById('qCaixas').value;
    const cor = document.getElementById('cor').value;
    const calibre = document.getElementById('calibre').value;
    const brix = document.getElementById('brix').value;
    const qntPallets = document.getElementById('qntPallets').value;
    const [localEstoque, tex_localEstoque] = obterValorTexto('localEstoque');
    const processoInterno = getSelectedValue();
    const observacoes = getSelectedObservacoes()

    // Cria uma nova linha na tabela
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-id', 'unique-id-1'); // Adiciona um ID único à linha
    newRow.innerHTML = `
        <td class="d-none">${tipoCaixa}</td>
        <td class="d-none">${descProduto}</td>
        <td class="d-none">${cliente}</td>
        <td class="d-none">${tipoEtiqueta}</td>
        <td class="d-none">${esteira}</td>
        <td class="d-none">${latada}</td>
        <td class="d-none">${qCaixas}</td>
        <td class="d-none">${cor}</td>
        <td class="d-none">${calibre}</td>
        <td class="d-none">${brix}</td>
        <td class="d-none">${qntPallets}</td>
        <td class="d-none">${localEstoque}</td>
        <td class="d-none">${processoInterno}</td>
        <td class="d-none">${observacoes}</td>
        <td>${tex_tipoCaixa}</td>
        <td>${tex_descProduto}</td>
        <td>${tex_cliente}</td>
        <td>${tex_tipoEtiqueta}</td>
        <td>${tex_esteira}</td>
        <td>${latada}</td>
        <td>${qCaixas}</td>
        <td>${cor}</td>
        <td>${calibre}</td>
        <td>${brix}</td>
        <td>${qntPallets}</td>
        <td>${tex_localEstoque}</td>
        <td>${processoInterno}</td>
        <td>${observacoes}</td>
        <td>
            <a class="btn btn-primary" onclick="imprimirLinha(this)">Enviar</a>
            <a class="btn btn-danger" onclick="apagar_linha(this)">Apagar</a>
            <a class="btn btn-warning" onclick="editarLinha(this)">Editar</a>
        </td>
    `;

    // Adiciona a nova linha na tabela
    document.querySelector('#tabelaDados tbody').appendChild(newRow);

    // Cria um novo card
    const newCard = document.createElement('div');
    newCard.innerHTML = `
        <div class="card mb-1" data-id="unique-id-1">
            <div class="card-header bg-dark text-white">
                <h5 class="card-title">Detalhes do Produto</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-6">
                        <strong>Tipo de Caixa:</strong> ${tex_tipoCaixa}
                    </div>
                    <div class="col-6">
                        <strong>Des. Produto:</strong> ${tex_descProduto}
                    </div>
                    <div class="col-6">
                        <strong>Cliente:</strong> ${tex_cliente}
                    </div>
                    <div class="col-6">
                        <strong>Tipo de Etiqueta:</strong> ${tex_tipoEtiqueta}
                    </div>
                    <div class="col-6">
                        <strong>Esteira:</strong> ${tex_esteira}
                    </div>
                    <div class="col-6">
                        <strong>Latada:</strong> ${latada}
                    </div>
                    <div class="col-6">
                        <strong>Q. Caixas:</strong> ${qCaixas}
                    </div>
                    <div class="col-6">
                        <strong>Cor:</strong> ${cor}
                    </div>
                    <div class="col-6">
                        <strong>Calibre:</strong> ${calibre}
                    </div>
                    <div class="col-6">
                        <strong>Brix:</strong> ${brix}
                    </div>
                    <div class="col-6">
                        <strong>Qnt. Pallets:</strong> ${qntPallets}
                    </div>
                    <div class="col-6">
                        <strong>Local de Estoque:</strong> ${tex_localEstoque}
                    </div>
                    <div class="col-6">
                        <strong>Processo Interno:</strong> ${processoInterno}
                    </div>
                    <div class="col-6">
                        <strong>Observações:</strong> ${observacoes}
                    </div>
                    <div class="row mx-1">
                        <a class="btn btn-primary col-4" onclick="imprimirCard(this)">Enviar</a>
                        <a class="btn btn-danger col-4" onclick="apagar_card(this)">Apagar</a>
                        <a class="btn btn-warning col-4" onclick="editarcard(this)">Editar</a>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Adiciona o novo card
    document.querySelector('#cards').appendChild(newCard);

    // Fecha o modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('formModal'));
    modal.hide();

    // Limpa os campos do formulário
    document.getElementById('formPreenchimento').reset();

    // Salvar o Pallet
    salvarPallet(extrairDados(newRow))
});

// Função para adicionar novos pallets
function salvarPallet(dados_pallet) {
    fetch('/adicionar_pallet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados_pallet)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Dados processados pelo Python:", data);
    })
    .catch(error => {
        console.error("Erro ao enviar dados para Python:", error);
    });
}

// Carregar o conteúdo salvo ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    fetch('listar_pallets')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#tabelaDados tbody');
            const cardsContainer = document.querySelector('#cards');

            data.forEach(item => {
                // Adiciona uma nova linha na tabela
                const newRow = document.createElement('tr');
                newRow.setAttribute('data-id', item.id); // Adiciona um ID único à linha
                newRow.innerHTML = `
                    <td class="d-none">${item.tipo_de_caixa}</td>
                    <td class="d-none">${item.des_produto}</td>
                    <td class="d-none">${item.cliente}</td>
                    <td class="d-none">${item.tipo_de_etiqueta}</td>
                    <td class="d-none">${item.esteira}</td>
                    <td class="d-none">${item.latada}</td>
                    <td class="d-none">${item.q_caixas}</td>
                    <td class="d-none">${item.cor}</td>
                    <td class="d-none">${item.calibre}</td>
                    <td class="d-none">${item.brix}</td>
                    <td class="d-none">${item.q_pallets}</td>
                    <td class="d-none">${item.local_de_estoque}</td>
                    <td class="d-none">${item.processo_interno}</td>
                    <td class="d-none">${item.observacoes}</td>
                    <td>${item.tex_tipoCaixa}</td>
                    <td>${item.tex_descProduto}</td>
                    <td>${item.tex_cliente}</td>
                    <td>${item.tex_tipoEtiqueta}</td>
                    <td>${item.tex_esteira}</td>
                    <td>${item.latada}</td>
                    <td>${item.q_caixas}</td>
                    <td>${item.cor}</td>
                    <td>${item.calibre}</td>
                    <td>${item.brix}</td>
                    <td>${item.q_pallets}</td>
                    <td>${item.tex_localEstoque}</td>
                    <td>${item.processo_interno}</td>
                    <td>${item.observacoes}</td>
                    <td>
                        <a class="btn btn-primary" onclick="imprimirLinha(this)">Enviar</a>
                        <a class="btn btn-danger" onclick="apagar_linha(this)">Apagar</a>
                        <a class="btn btn-warning" onclick="editarLinha(this)">Editar</a>
                    </td>
                `;
                tableBody.appendChild(newRow);

                // Adiciona um novo card
                const newCard = document.createElement('div');
                newCard.innerHTML = `
                    <div class="card mb-1" data-id="${item.id}">
                        <div class="card-header bg-dark text-white">
                            <h5 class="card-title">Detalhes do Produto</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-6">
                                    <strong>Tipo de Caixa:</strong> ${item.tex_tipoCaixa}
                                </div>
                                <div class="col-6">
                                    <strong>Des. Produto:</strong> ${item.tex_descProduto}
                                </div>
                                <div class="col-6">
                                    <strong>Cliente:</strong> ${item.tex_cliente}
                                </div>
                                <div class="col-6">
                                    <strong>Tipo de Etiqueta:</strong> ${item.tex_tipoEtiqueta}
                                </div>
                                <div class="col-6">
                                    <strong>Esteira:</strong> ${item.tex_esteira}
                                </div>
                                <div class="col-6">
                                    <strong>Latada:</strong> ${item.latada}
                                </div>
                                <div class="col-6">
                                    <strong>Q. Caixas:</strong> ${item.q_caixas}
                                </div>
                                <div class="col-6">
                                    <strong>Cor:</strong> ${item.cor}
                                </div>
                                <div class="col-6">
                                    <strong>Calibre:</strong> ${item.calibre}
                                </div>
                                <div class="col-6">
                                    <strong>Brix:</strong> ${item.brix}
                                </div>
                                <div class="col-6">
                                    <strong>Qnt. Pallets:</strong> ${item.q_pallets}
                                </div>
                                <div class="col-6">
                                    <strong>Local de Estoque:</strong> ${item.tex_localEstoque}
                                </div>
                                <div class="col-6">
                                    <strong>Processo Interno:</strong> ${item.processo_interno}
                                </div>
                                <div class="col-6">
                                    <strong>Observações:</strong> ${item.observacoes}
                                </div>
                                <div class="row mx-1">
                                    <a class="btn btn-primary col-4" onclick="imprimirCard(this)">Enviar</a>
                                    <a class="btn btn-danger col-4" onclick="apagar_card(this)">Apagar</a>
                                    <a class="btn btn-warning col-4" onclick="editarcard(this)">Editar</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                cardsContainer.appendChild(newCard);
            });
        })
        .catch(error => console.error('Erro ao carregar os dados:', error));
});

// Função para atualizar as descrições de produtos com base no tipo de caixa
document.getElementById('descProduto').addEventListener('focus', function() {
    const tipoCaixa = document.getElementById('tipoCaixa').value;

    // Limpa as opções existentes
    descProduto.innerHTML = '';

    // Adiciona novas opções com base na seleção
    if (produtosPorEmbalagem[tipoCaixa]) {
        produtosPorEmbalagem[tipoCaixa].forEach(produto => {
            const option = document.createElement('option');
            option.value = produto.value;
            option.textContent = produto.text;
            descProduto.appendChild(option);
        });
    }
});

function getSelectedObservacoes(){
    const selectElement = document.getElementById("observacoes");
    const selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value);
    return selectedValues.length > 0 ? selectedValues.join("+") : "+";
}