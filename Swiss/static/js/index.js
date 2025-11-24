
// Add player via AJAX
document.querySelector('form').addEventListener('submit', async (e) => {
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
});

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
        <form method="post" style="display:inline;">
        <button type="submit" class="danger">Remove All</button>
        </form>
    `;
    removeAllWrap.querySelector('form').addEventListener('submit', async (e) => {
        e.preventDefault();
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