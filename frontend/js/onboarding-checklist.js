/**
 * Onboarding Checklist
 * 
 * Manages the checklist on the onboarding dashboard.
 */

window.loadOnboardingChecklist = async function() {
    console.log('📋 loadOnboardingChecklist called');
    const container = document.getElementById('onboarding-checklist-container');
    if (!container) return;

    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const data = await response.json();
            renderChecklist(data.checklist_state);
        }
    } catch (error) {
        console.error('Failed to load checklist:', error);
    }
}

function renderChecklist(state) {
    const container = document.getElementById('onboarding-checklist-container');
    if (!container) return;

    const tasks = [
        { id: 'complete_profile', title: 'Complete Your Profile' },
        { id: 'create_event', title: 'Create First Event' },
        { id: 'add_team', title: 'Add a Team' },
        { id: 'invite_volunteers', title: 'Invite Volunteers' },
        { id: 'run_schedule', title: 'Run First Schedule' }
    ];

    let html = '<ul class="checklist-items" style="list-style: none; padding: 0;">';
    tasks.forEach(task => {
        const completed = state[task.id];
        html += `
            <li style="margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                <span class="checkbox" style="font-size: 1.5rem;">${completed ? '✅' : '⭕'}</span>
                <span class="task-title" style="${completed ? 'text-decoration: line-through; color: #666;' : 'font-weight: 500;'}">${task.title}</span>
            </li>
        `;
    });
    html += '</ul>';

    container.innerHTML = html;
}
