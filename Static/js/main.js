document.addEventListener('DOMContentLoaded', function() {
    // Cargar estudiantes y materias para el profesor
    if (document.getElementById('formNota')) {
        fetch('/api/estudiantes')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('estudiante');
                data.forEach(estudiante => {
                    const option = document.createElement('option');
                    option.value = estudiante.id;
                    option.textContent = estudiante.nombre;
                    select.appendChild(option);
                });
            });

        fetch('/api/materias')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('materia');
                data.forEach(materia => {
                    const option = document.createElement('option');
                    option.value = materia.id;
                    option.textContent = materia.nombre;
                    select.appendChild(option);
                });
            });

        document.getElementById('formNota').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                estudiante: document.getElementById('estudiante').value,
                materia: document.getElementById('materia').value,
                calificacion: document.getElementById('calificacion').value
            };

            fetch('/api/asignar-nota', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Nota asignada correctamente');
                    document.getElementById('formNota').reset();
                } else {
                    alert('Error al asignar nota');
                }
            });
        });
    }
});