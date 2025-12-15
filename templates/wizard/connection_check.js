<script>
    function copyYaml() {
    const yamlContent = document.getElementById('yaml-content').textContent;
    navigator.clipboard.writeText(yamlContent).then(function() {
        alert('YAML copied to clipboard!');
    }, function(err) {
        alert('Failed to copy: ' + err);
    });
}

    // Check ESP32 connection
    function checkConnection() {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const portInfo = document.getElementById('portInfo');
    const statusDiv = document.getElementById('connectionStatus');

    statusText.textContent = 'Checking...';
    indicator.style.background = '#6c757d';

    fetch('{% url "check_esp32_connection" %}')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
        indicator.style.background = '#28a745';
    statusText.textContent = `Connected (${data.count} device${data.count > 1 ? 's' : ''})`;
    statusDiv.style.borderLeftColor = '#28a745';

                // Show port info
                portInfo.innerHTML = data.ports.map(p =>
    `<div>📍 <strong>${p.port}</strong> - ${p.description}</div>`
    ).join('');
    portInfo.style.display = 'block';
            } else {
        indicator.style.background = '#dc3545';
    statusText.textContent = 'Not Connected';
    statusDiv.style.borderLeftColor = '#dc3545';
    portInfo.innerHTML = '<div>⚠️ No ESP32 detected. Please connect your ESP32 via USB. <a href="#" onclick="document.querySelector(\'details\').open=true; return false;">See connection instructions</a></div>';
    portInfo.style.display = 'block';
            }
        })
        .catch(error => {
        indicator.style.background = '#ffc107';
    statusText.textContent = 'Error checking connection';
    console.error('Error:', error);
        });
}

    // Check connection on page load
    checkConnection();

    // Auto-refresh every 5 seconds
    setInterval(checkConnection, 5000);
</script>
