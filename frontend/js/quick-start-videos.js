/**
 * Quick Start Videos
 *
 * Manages video playback and progress tracking for onboarding videos.
 * Tracks which videos have been watched and updates onboarding progress.
 */

// Note: Using window.authFetch (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

// Video configuration
const VIDEOS = [
    {
        id: 'getting_started',
        title: 'Getting Started',
        description: 'Learn the basics of SignUpFlow',
        duration: '2:30',
        url: 'https://www.youtube.com/embed/dQw4w9WgXcQ', // Placeholder
        thumbnail: '/images/video-thumbnails/getting-started.jpg'
    },
    {
        id: 'creating_events',
        title: 'Creating Events',
        description: 'Set up your first event',
        duration: '3:00',
        url: 'https://www.youtube.com/embed/dQw4w9WgXcQ', // Placeholder
        thumbnail: '/images/video-thumbnails/creating-events.jpg'
    },
    {
        id: 'managing_volunteers',
        title: 'Managing Volunteers',
        description: 'Add and organize your team',
        duration: '2:45',
        url: 'https://www.youtube.com/embed/dQw4w9WgXcQ', // Placeholder
        thumbnail: '/images/video-thumbnails/managing-volunteers.jpg'
    },
    {
        id: 'running_solver',
        title: 'Running the Solver',
        description: 'Auto-generate fair schedules',
        duration: '3:15',
        url: 'https://www.youtube.com/embed/dQw4w9WgXcQ', // Placeholder
        thumbnail: '/images/video-thumbnails/running-solver.jpg'
    }
];

/**
 * Open video player modal
 */
window.playVideo = function(videoId) {
    const video = VIDEOS.find(v => v.id === videoId);
    if (!video) {
        console.error('Video not found:', videoId);
        return;
    }

    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'video-modal';
    modal.innerHTML = `
        <div class="video-modal-overlay" onclick="window.closeVideoModal()"></div>
        <div class="video-modal-content">
            <div class="video-modal-header">
                <h3>${video.title}</h3>
                <button class="close-btn" onclick="window.closeVideoModal()">×</button>
            </div>
            <div class="video-player-container">
                <iframe
                    id="video-player"
                    width="100%"
                    height="500"
                    src="${video.url}?autoplay=1"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                ></iframe>
            </div>
            <div class="video-modal-footer">
                <p>${video.description}</p>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Track video view after 10 seconds (simulates partial watch)
    setTimeout(() => {
        window.markVideoWatched(videoId);
    }, 10000);
}

/**
 * Close video player modal
 */
window.closeVideoModal = function() {
    const modal = document.querySelector('.video-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Mark video as watched
 */
window.markVideoWatched = async function(videoId) {
    try {
        // Get current watched videos
        const watchedVideos = await getWatchedVideos();

        // Add this video if not already watched
        if (!watchedVideos.includes(videoId)) {
            watchedVideos.push(videoId);

            // Save to onboarding progress
            const response = await window.authFetch('/api/onboarding/progress', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    videos_watched: watchedVideos
                })
            });

            if (response.ok) {
                console.log('Video marked as watched:', videoId);

                // Update UI to show video as watched
                updateVideoCardStatus(videoId, true);

                // Check if all videos watched
                if (watchedVideos.length === VIDEOS.length) {
                    showVideoCompletionMessage();
                }
            }
        }
    } catch (error) {
        console.error('Failed to mark video as watched:', error);
    }
}

/**
 * Get list of watched videos from API
 */
async function getWatchedVideos() {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const data = await response.json();
            return data.videos_watched || [];
        }
    } catch (error) {
        console.error('Failed to load watched videos:', error);
    }
    return [];
}

/**
 * Update video card UI to show watched status
 */
function updateVideoCardStatus(videoId, watched) {
    const videoCard = document.querySelector(`[data-video-id="${videoId}"]`);
    if (videoCard) {
        if (watched) {
            videoCard.classList.add('watched');

            // Add checkmark indicator
            const thumbnail = videoCard.querySelector('.video-thumbnail');
            if (thumbnail && !thumbnail.querySelector('.watched-badge')) {
                const badge = document.createElement('div');
                badge.className = 'watched-badge';
                badge.innerHTML = '✓ Watched';
                thumbnail.appendChild(badge);
            }
        } else {
            videoCard.classList.remove('watched');

            const badge = videoCard.querySelector('.watched-badge');
            if (badge) {
                badge.remove();
            }
        }
    }
}

/**
 * Show completion message when all videos watched
 */
function showVideoCompletionMessage() {
    const message = document.createElement('div');
    message.className = 'video-completion-toast';
    message.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">🎉</span>
            <span class="toast-message">Great job! You've watched all quick start videos!</span>
        </div>
    `;

    document.body.appendChild(message);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        message.classList.add('fade-out');
        setTimeout(() => message.remove(), 500);
    }, 5000);
}

/**
 * Render video grid with current watch status
 */
window.renderVideoGrid = async function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const watchedVideos = await getWatchedVideos();

    container.innerHTML = `
        <div class="video-grid">
            ${VIDEOS.map(video => `
                <div class="video-card ${watchedVideos.includes(video.id) ? 'watched' : ''}" data-video-id="${video.id}">
                    <div class="video-thumbnail" onclick="window.playVideo('${video.id}')">
                        <div class="play-icon">▶</div>
                        ${watchedVideos.includes(video.id) ? '<div class="watched-badge">✓ Watched</div>' : ''}
                    </div>
                    <h3 data-i18n="onboarding.dashboard.videos.${video.id}">${video.title}</h3>
                    <p data-i18n="onboarding.dashboard.videos.${video.id}_desc">${video.description}</p>
                    <span class="video-duration">${video.duration}</span>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Initialize videos on page load
 */
window.initVideos = async function() {
    // Check if video grid container exists
    const container = document.querySelector('.video-grid');
    if (container && container.parentElement) {
        await window.renderVideoGrid(container.parentElement.id);
    }
}
