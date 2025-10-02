/**
 * Toast notification system - replacement for alert() and prompt()
 */

// Show inline toast message instead of alert()
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.style.cssText = `
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 250px;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    `;

    toast.innerHTML = `
        <span style="font-size: 18px; font-weight: bold;">${icons[type] || icons.info}</span>
        <span style="flex: 1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            opacity: 0.7;
        ">×</button>
    `;

    container.appendChild(toast);

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // Add animations
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Show inline input dialog instead of prompt()
function showInputDialog(message, defaultValue = '', callback) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    // Create dialog
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        background: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        min-width: 400px;
        max-width: 90%;
    `;

    dialog.innerHTML = `
        <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #1f2937;">${message}</h3>
        <input type="text" id="dialog-input" value="${defaultValue}" style="
            width: 100%;
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 16px;
            box-sizing: border-box;
        "/>
        <div style="display: flex; gap: 8px; justify-content: flex-end;">
            <button id="dialog-cancel" style="
                padding: 8px 16px;
                border: 1px solid #d1d5db;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            ">Cancel</button>
            <button id="dialog-ok" style="
                padding: 8px 16px;
                border: none;
                background: #3b82f6;
                color: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            ">OK</button>
        </div>
    `;

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    const input = dialog.querySelector('#dialog-input');
    const okBtn = dialog.querySelector('#dialog-ok');
    const cancelBtn = dialog.querySelector('#dialog-cancel');

    input.focus();
    input.select();

    const cleanup = (value) => {
        overlay.remove();
        callback(value);
    };

    okBtn.onclick = () => cleanup(input.value);
    cancelBtn.onclick = () => cleanup(null);

    input.onkeydown = (e) => {
        if (e.key === 'Enter') cleanup(input.value);
        if (e.key === 'Escape') cleanup(null);
    };

    overlay.onclick = (e) => {
        if (e.target === overlay) cleanup(null);
    };
}

// Show confirmation dialog instead of confirm()
function showConfirmDialog(message, callback) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    const dialog = document.createElement('div');
    dialog.style.cssText = `
        background: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        min-width: 400px;
        max-width: 90%;
    `;

    dialog.innerHTML = `
        <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #1f2937;">${message}</h3>
        <div style="display: flex; gap: 8px; justify-content: flex-end;">
            <button id="confirm-no" style="
                padding: 8px 16px;
                border: 1px solid #d1d5db;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            ">Cancel</button>
            <button id="confirm-yes" style="
                padding: 8px 16px;
                border: none;
                background: #ef4444;
                color: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            ">Confirm</button>
        </div>
    `;

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    const yesBtn = dialog.querySelector('#confirm-yes');
    const noBtn = dialog.querySelector('#confirm-no');

    const cleanup = (result) => {
        overlay.remove();
        callback(result);
    };

    yesBtn.onclick = () => cleanup(true);
    noBtn.onclick = () => cleanup(false);

    overlay.onclick = (e) => {
        if (e.target === overlay) cleanup(false);
    };

    document.onkeydown = (e) => {
        if (e.key === 'Escape') {
            cleanup(false);
            document.onkeydown = null;
        }
    };
}
