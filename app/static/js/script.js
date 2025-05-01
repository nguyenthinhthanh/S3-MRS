async function fetchSpaces() {
    const res = await fetch('/api/spaces');
    const spaces = await res.json();
    const tbody = document.querySelector('#spaces-table tbody');
    tbody.innerHTML = '';
    spaces.forEach(sp => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${sp.name}</td>
        <td>${sp.type}</td>
        <td>${sp.equipment.join(', ')}</td>
        <td>${sp.status}${sp.reserved_until ? ' until ' + new Date(sp.reserved_until).toLocaleTimeString() : ''}</td>
        <td>
        ${sp.status === 'available'  ? `<button onclick="reserve(${sp.id})">Reserve</button>`
        : sp.status === 'reserved'  ? `<button onclick="checkin(${sp.id})">Check-In</button>`
        : `<button onclick="checkout(${sp.id})">Check-Out</button>`}
        </td>
    `;
    tbody.appendChild(tr);
    });
}

async function reserve(id) {
    const duration = prompt('Duration in minutes?', '60');
    if (!duration) return;
    await fetch('/api/reserve', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id, duration})
    });
    fetchSpaces();
}

async function checkin(id) {
    await fetch('/api/checkin', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id})
    });
    fetchSpaces();
}

async function checkout(id) {
    await fetch('/api/checkout', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id})
    });
    fetchSpaces();
}

window.onload = fetchSpaces;