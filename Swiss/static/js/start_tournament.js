const restartForm = document.getElementById('restart-form');

if (restartForm) {
    restartForm.addEventListener('submit', function (e) {
        const confirmed = confirm("Are you sure you want to restart the tournament? All current data will be lost.");

        if (!confirmed) {
            e.preventDefault(); // stop submit
        }
    });
}