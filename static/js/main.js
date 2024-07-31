function openForm() {
    document.getElementById('popupForm').style.display = 'flex';
}

function closeForm() {
    document.getElementById('popupForm').style.display = 'none';
}

function deleteNote(noteId) {
    fetch(`/delete/${noteId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.result === 'success') {
            document.getElementById(`note-${noteId}`).remove();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
