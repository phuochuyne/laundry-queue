// Show specific error messaging based on error code from URL params or data attributes
(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const errorCode = urlParams.get('code') || document.body.getAttribute('data-error-code');
  
  if (errorCode) {
    const errorAlert = document.querySelector(`[data-error-code="${errorCode}"]`);
    if (errorAlert) {
      errorAlert.style.display = 'flex';
    }
  }
})();