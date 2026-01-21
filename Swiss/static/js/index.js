
// Handler for single player submission
async function handleSingleSubmit(e) {
    e.preventDefault();
    const input = document.querySelector('#player_name');
    const formData = new FormData();
    formData.append('player_name', input.value);
    
    const res = await fetch(addPlayerURL, {
    method: 'POST',
    body: formData
    });
    const data = await res.json();
    
    if (data.success) {
    input.value = '';
    updatePlayerList(data);
    }
}

// Remove player via AJAX
function attachRemoveListeners() {
    document.querySelectorAll('#player-list form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const playerName = form.querySelector('input[name="player_name"]').value;
        const formData = new FormData();
        formData.append('player_name', playerName);
        
        const res = await fetch(removePlayerURL, {
        method: 'POST',
        body: formData
        });
        const data = await res.json();
        
        if (data.success) {
        updatePlayerList(data);
        }
    });
    });
}

// Update UI after add/remove
function updatePlayerList(data) {
    const list = document.querySelector('#player-list');
    list.innerHTML = data.player_list.map(player => `
    <li>
        <span class="player-name">${player}</span>
        <form method="post" style="display:inline;">
        <input type="hidden" name="player_name" value="${player}">
        <button type="submit" class="danger">Remove</button>
        </form>
    </li>
    `).join('');
    
    document.querySelector('h2').textContent = `Players (${data.count})`;
    
    // Update number of rounds in header
    document.querySelector('header p strong').textContent = data.number_of_rounds;
    
    // Update Remove All button (create if doesn't exist)
    let removeAllWrap = document.querySelector('.remove-all-wrap');
    if (!removeAllWrap) {
    removeAllWrap = document.createElement('div');
    removeAllWrap.className = 'remove-all-wrap';
    removeAllWrap.style.cssText = 'text-align:center; margin-top:12px;';
    list.parentNode.appendChild(removeAllWrap);
    }
    
    if (data.count > 0) {
        removeAllWrap.innerHTML = `
            <button id="remove-all-btn" class="danger">Remove All</button>
        `;
        removeAllWrap.querySelector('#remove-all-btn').addEventListener('click', async () => {
            const res = await fetch(removeAllURL, { method: 'POST' });
            const data = await res.json();
            if (data.success) updatePlayerList(data);
        });
    } else {
        removeAllWrap.innerHTML = '';
    }
    
    const controls = document.querySelector('#controls');
    if (data.count > 1) {
    controls.innerHTML = `<a id="start-btn" href="${startTournamentURL}">Start Tournament</a>`;
    } else {
    controls.innerHTML = '';
    }
    
    attachRemoveListeners();
}

attachRemoveListeners();

// Switch between input and textarea for multiple player input
let isTextareaMode = false;

document.getElementById('switch-add-type').addEventListener('click', function() {
    const form = document.querySelector('form');
    const currentInput = document.querySelector('#player_name');
    
    if (!isTextareaMode) {
        // Switch to textarea mode
        const textarea = document.createElement('textarea');
        textarea.id = 'player_name';
        textarea.name = 'player_name';
        textarea.placeholder = 'Enter player names (one per line)';
        textarea.style.width = '100%';
        textarea.style.minHeight = '100px';
        
        currentInput.parentNode.replaceChild(textarea, currentInput);
        this.textContent = 'Switch to Single';
        isTextareaMode = true;
        
        // Update form submission to handle multiple names
        form.removeEventListener('submit', handleSingleSubmit);
        form.addEventListener('submit', handleMultipleSubmit);
    } else {
        // Switch back to input mode
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'player_name';
        input.name = 'player_name';
        input.placeholder = 'Enter player name';
        input.required = true;
        
        currentInput.parentNode.replaceChild(input, currentInput);
        this.textContent = 'Switch to Multiple';
        isTextareaMode = false;
        
        // Update form submission back to single name
        form.removeEventListener('submit', handleMultipleSubmit);
        form.addEventListener('submit', handleSingleSubmit);
    }
});

// Handler for single player submission
async function handleSingleSubmit(e) {
    e.preventDefault();
    const input = document.querySelector('#player_name');
    const formData = new FormData();
    formData.append('player_name', input.value);
    
    const res = await fetch(addPlayerURL, {
        method: 'POST',
        body: formData
    });
    const data = await res.json();
    
    if (data.success) {
        input.value = '';
        updatePlayerList(data);
    }
}

// Handler for multiple player submission
async function handleMultipleSubmit(e) {
    e.preventDefault();
    const textarea = document.querySelector('#player_name');
    const names = textarea.value
        .split('\n')
        .map(name => name.trim())
        .filter(name => name.length > 0);
    
    if (names.length === 0) return;
    
    // Add each player one by one
    let lastData = null;
    for (const name of names) {
        const formData = new FormData();
        formData.append('player_name', name);
        
        const res = await fetch(addPlayerURL, {
            method: 'POST',
            body: formData
        });
        lastData = await res.json();
    }
    
    if (lastData && lastData.success) {
        textarea.value = '';
        updatePlayerList(lastData);
    }
}

// Attach the single submit handler initially
document.querySelector('form').addEventListener('submit', handleSingleSubmit);