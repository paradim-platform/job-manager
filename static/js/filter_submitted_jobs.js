const filterBtnSuccess = document.getElementById('filter-btn-success');
const filterBtnPending = document.getElementById('filter-btn-pending');
const filterBtnFailure = document.getElementById('filter-btn-failure');
const filterBtnAll = document.getElementById('filter-btn-all');

const buttons = document.querySelectorAll('.filter-btn');

filterBtnSuccess.addEventListener('click', updateFilter)
filterBtnPending.addEventListener('click', updateFilter)
filterBtnFailure.addEventListener('click', updateFilter)
filterBtnAll.addEventListener('click', updateFilter)


function updateFilter(_) {
    const submissions = document.querySelectorAll('.submission-item');

    // Update active status
    buttons.forEach(btn => {
        if (btn.id === this.id) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Filter on (success, pending, failure, all)
    const toFilterOn = this.id.replace('filter-btn-', 'submission-');

    if (toFilterOn === 'submission-all') {
        submissions.forEach(submission => {
            submission.hidden = false;
        })
    } else {
        submissions.forEach(submission => {
            submission.hidden = !submission.classList.contains(toFilterOn);
        })
    }
}