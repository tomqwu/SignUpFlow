(function () {
  'use strict'

  function statusElement() {
    return document.getElementById('request-status')
  }

  function showStatus(message) {
    var status = statusElement()
    if (!status) return
    status.textContent = message
    status.hidden = false
  }

  function clearStatus() {
    var status = statusElement()
    if (!status) return
    status.textContent = ''
    status.hidden = true
  }

  function requestControls(element) {
    if (!element) return []
    if (element.matches && element.matches('button, input[type="submit"]')) {
      return [element]
    }
    if (element.querySelectorAll) {
      return Array.from(element.querySelectorAll('button[type="submit"], input[type="submit"]'))
    }
    return []
  }

  function setPending(element, pending) {
    requestControls(element).forEach(function (control) {
      control.disabled = pending
      control.setAttribute('aria-busy', pending ? 'true' : 'false')
    })
  }

  document.body.addEventListener('htmx:beforeRequest', function (event) {
    clearStatus()
    setPending(event.detail.elt, true)
  })

  document.body.addEventListener('htmx:afterRequest', function (event) {
    setPending(event.detail.elt, false)
    if (event.detail.successful) clearStatus()
  })

  document.body.addEventListener('htmx:sendError', function (event) {
    setPending(event.detail.elt, false)
    showStatus('Request failed. Check your connection and try again. Your entries are still here.')
  })

  document.body.addEventListener('htmx:timeout', function (event) {
    setPending(event.detail.elt, false)
    showStatus('Request timed out. Check your connection and try again. Your entries are still here.')
  })

  document.body.addEventListener('htmx:sseError', function () {
    showStatus('Live updates were interrupted. Reconnecting now.')
  })

  document.body.addEventListener('htmx:sseOpen', function (event) {
    clearStatus()
    var refresh = event.target.querySelector('[data-sse-refresh]')
    if (!refresh) return
    window.htmx.ajax('GET', refresh.getAttribute('hx-get'), {
      target: '#solution-assignments',
      swap: 'outerHTML'
    })
  })
})()
