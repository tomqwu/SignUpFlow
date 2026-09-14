(function () {
  'use strict';

  function token() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function protectForm(form) {
    var method = (form.getAttribute('method') || 'get').toLowerCase();
    if (method === 'get' || form.querySelector('input[name="csrf_token"]')) return;

    var field = document.createElement('input');
    field.type = 'hidden';
    field.name = 'csrf_token';
    field.value = token();
    form.appendChild(field);
  }

  function protectForms(root) {
    if (root.matches && root.matches('form')) protectForm(root);
    root.querySelectorAll('form').forEach(protectForm);
  }

  document.addEventListener('DOMContentLoaded', function () {
    protectForms(document);
  });
  document.addEventListener('submit', function (event) {
    protectForm(event.target);
  }, true);
  document.body.addEventListener('htmx:configRequest', function (event) {
    event.detail.headers['X-CSRF-Token'] = token();
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    protectForms(event.detail.target);
  });
})();
