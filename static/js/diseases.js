document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('diseaseForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        fetch('/disease', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction) {
                document.getElementById('result').innerHTML = "Predicted disease: <br><span>" + data.prediction + "</span>";
            } else {
                document.getElementById('result').innerHTML = "Error: Unable to identify disease";
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});