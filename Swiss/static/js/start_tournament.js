const restartForm = document.getElementById('restart-form');
const submitResultsForm = document.getElementById('submit-results-form');

if (restartForm) {
    restartForm.addEventListener('submit', function (e) {
        const confirmed = confirm("Are you sure you want to restart the tournament? All current data will be lost.");

        if (!confirmed) {
            e.preventDefault(); // stop submit
        }
    });
}

if (submitResultsForm) {
    submitResultsForm.addEventListener('submit', function (e) {
        const confirmed = confirm("Are you sure you want to submit the round results? This will advance to the next round.");

        if (!confirmed) {
            e.preventDefault(); // stop submit
            return;
        }

        // Temporarily re-enable all disabled selects so their values are submitted
        const disabledSelects = submitResultsForm.querySelectorAll('select:disabled');
        disabledSelects.forEach(select => {
            select.disabled = false;
        });

        // The form will submit normally, then re-disable the selects after a short delay
        setTimeout(() => {
            disabledSelects.forEach(select => {
                select.disabled = true;
            });
        }, 100);
    });
}

// Timer functionality - AJAX polling version
let timerInterval;
let lastRemaining;
let durationInputModified = false;

function getTimerData() {
    const timerData = document.getElementById('timer-data');
    if (!timerData) return { duration: 6000, start: null, paused: true };
    
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

// Toggle switch functionality for locking/unlocking results
function initializeToggles() {
    // Get all toggle checkboxes
    const toggles = document.querySelectorAll('input[type="checkbox"][id^="lock-"]');
    const submitButton = document.querySelector('input[type="submit"][value="Submit Results"]');
    
    function updateSubmitButton() {
        const allLocked = Array.from(toggles).every(toggle => toggle.checked);
        if (submitButton) {
            submitButton.disabled = !allLocked;
            submitButton.style.opacity = allLocked ? '1' : '0.6';
            submitButton.style.cursor = allLocked ? 'pointer' : 'not-allowed';
        }
    }
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            // Extract player names from toggle ID (format: lock-player1-player2)
            const toggleId = this.id;
            const players = toggleId.replace('lock-', '').split('-');
            const selectId = `select-${players[0]}-${players[1]}`;
            const selectElement = document.getElementById(selectId);
            
            if (selectElement) {
                selectElement.disabled = this.checked;
                // Add visual feedback
                selectElement.style.opacity = this.checked ? '0.6' : '1';
            }
            
            // Update submit button state
            updateSubmitButton();
        });
    });
    
    // Initial check
    updateSubmitButton();
}

// Initialize timer polling
document.addEventListener('DOMContentLoaded', function() {
    pollTimer(); // Initial poll
    timerInterval = setInterval(pollTimer, 1000); // Poll every second
    initializeToggles(); // Initialize toggle switches
});