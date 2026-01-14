const restartForm = document.getElementById('restart-form');

if (restartForm) {
    restartForm.addEventListener('submit', function (e) {
        const confirmed = confirm("Are you sure you want to restart the tournament? All current data will be lost.");

        if (!confirmed) {
            e.preventDefault(); // stop submit
        }
    });
}

// Timer functionality - AJAX polling version
let timerInterval;
let lastRemaining;
let durationInputModified = false;

function getTimerData() {
    const timerData = document.getElementById('timer-data');
    if (!timerData) return { duration: 300, start: null, paused: true };
    
    return {
        duration: parseInt(timerData.dataset.duration),
        start: timerData.dataset.start === 'null' ? null : parseFloat(timerData.dataset.start),
        paused: timerData.dataset.paused === 'true'
    };
}

// Initialize with data from HTML
const initialData = getTimerData();
lastRemaining = initialData.duration;

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function updateTimerDisplay(remaining, paused) {
    const timerElement = document.getElementById('timer');
    timerElement.textContent = formatTime(remaining);
    
    if (remaining <= 0 && !paused) {
        timerElement.style.color = 'red';
        if (remaining < lastRemaining) { // Only alert once when it hits zero
            alert('Time is up!');
        }
    } else {
        timerElement.style.color = 'black';
    }
    
    lastRemaining = remaining;
}

function pollTimer() {
    fetch('/get_timer_state')
        .then(response => response.json())
        .then(data => {
            updateTimerDisplay(data.remaining, data.paused);
            
            // Update button states
            document.getElementById('start-timer').disabled = !data.paused;
            document.getElementById('pause-timer').disabled = data.paused;
            
            // Only update duration input if user hasn't modified it
            if (!durationInputModified) {
                document.getElementById('duration').value = Math.ceil(data.duration / 60);
            }
        })
        .catch(error => console.error('Error polling timer:', error));
}

function startTimer() {
    fetch('/start_timer', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pollTimer(); // Immediate update
            }
        })
        .catch(error => console.error('Error starting timer:', error));
}

function pauseTimer() {
    fetch('/pause_timer', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pollTimer(); // Immediate update
            }
        })
        .catch(error => console.error('Error pausing timer:', error));
}

function resetTimer() {
    fetch('/reset_timer', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                durationInputModified = false; // Reset modification flag
                pollTimer(); // Immediate update
            }
        })
        .catch(error => console.error('Error resetting timer:', error));
}

function setDuration() {
    const durationInput = document.getElementById('duration');
    const newDuration = parseInt(durationInput.value) * 60;

    fetch('/set_timer_duration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `duration=${newDuration}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            pollTimer(); // Immediate update
        }
    })
    .catch(error => console.error('Error setting duration:', error));
}

// Event listeners
document.getElementById('start-timer').addEventListener('click', startTimer);
document.getElementById('pause-timer').addEventListener('click', pauseTimer);
document.getElementById('reset-timer').addEventListener('click', resetTimer);
document.getElementById('set-duration-form').addEventListener('submit', function(e) {
    e.preventDefault();
    durationInputModified = false; // Reset flag after setting
    setDuration();
});

// Track when user modifies the duration input
document.getElementById('duration').addEventListener('input', function() {
    durationInputModified = true;
});

// Initialize timer polling
document.addEventListener('DOMContentLoaded', function() {
    pollTimer(); // Initial poll
    timerInterval = setInterval(pollTimer, 1000); // Poll every second
});