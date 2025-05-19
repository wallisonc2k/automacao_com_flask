const classificacao = ["Extra", "Extra A", "Extra AA", "Extra AAA"];
const modeloEtiquetas = ["30X50"];


function addCard(esteira) {
    const cardContainer = document.getElementById('cardContainer');
    var index = cardContainer.children.length + 1
    const newCard = createCard(esteira);
    cardContainer.appendChild(newCard);
    newCard.querySelector('.variedades').focus();
    updateIndicators();
}

function createCard(esteira) {
    const card = document.createElement('div');
    cabines = Array.from({ length: 32}, (_, i) => esteira + `-${String(i + 1).padStart(2, '0')}`);
    card.className = 'card';
    card.innerHTML = `
        <div class="card-indicator ${esteira}">Esteira ${esteira}</div>
        <label for="">Variedade:</label>
        <select class="variedades"></select>
        <label for="">Classificação:</label>
        <select class="classificacao"></select>
        <label for="">Peso</label>
        <input type="number" class="peso" placeholder="">
        <label for="">Total de Etiquetas</label>
        <input type="number" class="totalEtiquetas" placeholder="">
        <label for="">Modelo de Etiqueta:</label>
        <select class="modeloEtiquetas"></select>
        <label for="">Cabines:</label>
        <div class="cabines-container"></div>
        <div class="button-group">
            <button class="submit-button" onclick="handleSubmit(this)">Imprimir</button>
            <button class="delete" onclick="deleteCard(this)">Excluir</button>
        </div>
    `;
    
    
    populateSelect(card.querySelector('.variedades'), variedades);
    populateSelect(card.querySelector('.classificacao'), classificacao);
    populateSelect(card.querySelector('.modeloEtiquetas'), modeloEtiquetas);
    createCabineButtons(card.querySelector('.cabines-container'));
    return card;
}

function deleteCard(button) {
    const cardContainer = document.getElementById('cardContainer');
    const card = button.closest('.card');
    const cardIndex = Array.from(cardContainer.children).indexOf(card);

    card.remove();
    updateIndicators();

    // Ajustar o índice do indicador ativo
    /*const remainingCards = document.querySelectorAll('.card');
    if (remainingCards.length > 0) {
        const newActiveIndex = Math.min(cardIndex, remainingCards.length - 1);
        document.getElementById('cardContainer').scrollLeft = remainingCards[newActiveIndex].offsetLeft;
        updateActiveIndicator(newActiveIndex);
    }*/

    // Salvar as alterações no localStorage
    saveCardsToLocalStorage();
    showAlert('Card apagado!');
    
}

function populateSelect(selectElement, options) {
    selectElement.innerHTML = options.map(option => `<option value="${option}">${option}</option>`).join('');
}

let cabines = []
function createCabineButtons(container) {
    container.innerHTML = cabines.map(cabine => `
        <div class="cabine-button">${cabine}</div>
    `).join('');
    container.querySelectorAll('.cabine-button').forEach(button => {
        button.addEventListener('click', () => button.classList.toggle('selected'));
    });
}

function handleSubmit(button) {
    const card = button.closest('.card');
    const data = {
        variedades: card.querySelector('.variedades').value,
        classificacao: card.querySelector('.classificacao').value,
        peso: card.querySelector('.peso').value,
        total_etiquetas: card.querySelector('.totalEtiquetas').value,
        modelo_etiquetas: card.querySelector('.modeloEtiquetas').value,
        cabines: Array.from(card.querySelectorAll('.cabine-button.selected')).map(btn => btn.textContent)
    };

    // Enviar os dados ao servidor
    fetch('/api/cabines', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Sucesso:', data);
        showAlert('Dados enviados com sucesso!');
    })
    .catch(error => console.error('Erro:', error));

    // Salvar os dados no localStorage
    saveCardsToLocalStorage();
}

function saveCardsToLocalStorage() {
    const cards = Array.from(document.querySelectorAll('.card')).map(card => ({
        variedades: card.querySelector('.variedades').value,
        classificacao: card.querySelector('.classificacao').value,
        peso: card.querySelector('.peso').value,
        totalEtiquetas: card.querySelector('.totalEtiquetas').value,
        modeloEtiquetas: card.querySelector('.modeloEtiquetas').value,
        esteira: card.querySelector('.card-indicator').textContent.split(" ")[1],
        cabines: Array.from(card.querySelectorAll('.cabine-button.selected')).map(btn => btn.textContent)
    }));

    localStorage.setItem('cards', JSON.stringify(cards));
}

function loadCardsFromLocalStorage() {
    const savedCards = JSON.parse(localStorage.getItem('cards')) || [];

    savedCards.forEach((cardData, index) => {
        const cardContainer = document.getElementById('cardContainer');
        const newCard = createCard(cardData.esteira);
        
        cardContainer.appendChild(newCard);

        newCard.querySelector('.variedades').value = cardData.variedades;
        newCard.querySelector('.classificacao').value = cardData.classificacao;
        newCard.querySelector('.peso').value = cardData.peso;
        newCard.querySelector('.totalEtiquetas').value = cardData.totalEtiquetas;
        newCard.querySelector('.modeloEtiquetas').value = cardData.modeloEtiquetas;

        // Recriar os botões das cabines e marcar as selecionadas
        createCabineButtons(newCard.querySelector('.cabines-container'));

        cardData.cabines.forEach(cabine => {
            const button = Array.from(newCard.querySelectorAll('.cabine-button')).find(btn => btn.textContent === cabine);
            if (button) button.classList.add('selected');
        });
    });

    updateIndicators();
}

let observer; // Variável para armazenar o observador

function updateIndicators() {
    const indicator = document.getElementById('indicator');
    const cards = document.querySelectorAll('.card');
    indicator.innerHTML = '';

    cards.forEach((card, index) => {
        const button = document.createElement('button');
        button.className = index === 0 ? 'active' : '';
        button.addEventListener('click', () => {
            document.getElementById('cardContainer').scrollLeft = card.offsetLeft;
            updateActiveIndicator(index);
        });
        indicator.appendChild(button);
    });

    observeCards(); // Chama a função para observar os cards
}

function observeCards() {
    const cards = document.querySelectorAll('.card');

    // Desconecta o observador anterior, se existir
    if (observer) observer.disconnect();

    // Cria um novo observador
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const visibleCardIndex = Array.from(cards).indexOf(entry.target);
                updateActiveIndicator(visibleCardIndex);
            }
        });
    }, { threshold: 0.5 });

    // Adiciona o observador aos cards
    cards.forEach(card => observer.observe(card));
}

function updateActiveIndicator(activeIndex) {
    const buttons = document.querySelectorAll('.indicator button');
    buttons.forEach((button, index) => {
        button.className = index === activeIndex ? 'active' : '';
    });
}

function showAlert(message, title) {
    // Atualizar o tiulo do modal
    if (title === undefined) {
        document.querySelector('.modal-header').innerHTML = '';
    } else {
        document.getElementById('cardModalLabel').innerText = title;
    }
    // Atualiza a mensagem no modal
    document.getElementById('modalMessage').innerText = message;

    // Inicializa e exibe o modal
    const cardModal = new bootstrap.Modal(document.getElementById('cardModal'));
    cardModal.show();
}

window.onload = () => {
    loadCardsFromLocalStorage();
};