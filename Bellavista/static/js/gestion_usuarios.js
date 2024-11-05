
function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    const opciones = { year: 'numeric', month: 'short', day: 'numeric' };
    return fecha.toLocaleDateString('en-US', opciones);
}

function toggleEditForm(id) {
    var editFormTask = document.getElementById('editForm' + id); // Formulario de edición para Tareas
    
    // Mostrar u ocultar el formulario de edición si existe
    if (editFormTask) {
        editFormTask.style.display = (editFormTask.style.display === 'none' || editFormTask.style.display === '') ? 'table-row' : 'none';
    }
    
    if (editFormAssignment) {
        editFormAssignment.style.display = (editFormAssignment.style.display === 'none' || editFormAssignment.style.display === '') ? 'table-row' : 'none';
    } else {
        console.error('No se encontró el formulario de edición para la asignación con ID:', id);
    }

    // Ocultar otros formularios de edición abiertos
    var allEditForms = document.querySelectorAll('.edit-form-row');
    allEditForms.forEach(function(form) {
        if (form.id !== 'editRow' + id && form.id !== 'editForm' + id) {
            form.style.display = 'none';
        }
    });
}

function cancelEdit(id) {
    var formRow = document.getElementById('editRow' + id); // Para Asignadas
    var formEdit = document.getElementById('editForm' + id); // Para Lista 

    if (formRow) {
        formRow.style.display = 'none'; // Ocultar 
    }
    if (formEdit) {
        formEdit.style.display = 'none'; // Ocultar 
    }
}

// Mostrar/Ocultar el formulario para crear una nueva tarea
function toggleNewTaskForm() {
    var form = document.getElementById('createTaskForm');
    var filterForm = document.getElementById('filterForm');  // Formulario de filtros

    // Ocultar el formulario de filtros si está abierto
    if (filterForm.style.display !== 'none') {
        filterForm.style.display = 'none';
    }

    // Mostrar u ocultar el formulario de creación de tareas
    form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'block' : 'none';
}



$(document).ready(function() {
    // Función para obtener el token CSRF
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Comprueba si esta cookie comienza con el nombre que queremos
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    // Configuración de AJAX para incluir el token CSRF en el encabezado
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^GET|HEAD|OPTIONS|TRACE$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

   
    $(document).on('submit', '.delete-assignment-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var assignmentId = form.data('assignment-id');
        var url = form.data('url');
    
        if (!confirm('¿Eliminar esta asignación?')) {
            return;
        }
    
        $.ajax({
            type: 'POST',
            url: eliminarAsignacionUrl,
            data: {
                'asignacion_id': assignmentId,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                alert(response.message);

                form.closest('tr').remove();
    
                // Recargar ambas tablas después de eliminar la asignación
                recargarTablaAsignacion();
                recargarTablaTareas();
            },
            error: function(xhr, status, error) {
                alert('Error al eliminar la asignación.');
                console.error(xhr.responseText);
            }
        });
    });    
    
    $(document).on('submit', '.edit-assignment-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var assignmentId = form.data('assignment-id');
        var trabajadorId = form.find('select[name="trabajador_id"]').val();
        var estado = form.find('select[name="estado"]').val();
        var url = form.data('url');
    
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'asignacion_id': assignmentId,
                'trabajador_id': trabajadorId,
                'estado': estado,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                alert(response.message);
                // Actualizar el DOM como se hacía antes
                var row = $('#editRow' + assignmentId).prev();
                row.html(`
                    <td>${response.tarea_nombre}</td>
                    <td>${response.desc}</td>
                    <td>${response.prioridad}</td>
                    <td>${formatearFecha(response.fecha)}</td>
                    <td>${response.trabajador_nombre}</td>
                    <td>${response.estado}</td>
                    <td>
                        <div class="action-buttons asignadas"> 
                            <form method="POST" id="formEliminarAsignacion${assignmentId}" class="delete-assignment-form" data-assignment-id="${assignmentId}" data-url="${eliminarAsignacionUrl}">
                                <input type="hidden" name="asignacion_id" value="${assignmentId}">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                                <button type="submit" class="btn btn-icon">
                                    <img src="${staticUrl}delete-icon.png" alt="Eliminar">
                                </button>
                            </form>
                            <button type="button" class="btn btn-icon" onclick="toggleEditForm('${assignmentId}')">
                                <img src="${staticUrl}edit-icon.png" alt="Editar">
                            </button>
                        </div>
                    </td>
                `);
                // Ocultar el formulario de edición
                cancelEdit(assignmentId);
            },
            error: function(xhr, status, error) {
                alert('Error al editar la asignación.');
                console.error(xhr.responseText);
            }
        });
    });
    
    $(document).on('submit', '.delete-task-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var usuarioid = form.data('rut');
        var url = form.data('url');

        if (!confirm('¿Eliminar esta tarea?')) {
            return;
        }
    
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'rut': usuarioid,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                alert(response.message);
                form.closest('tr').remove();  // Remover la fila correspondiente a la tarea
                recargarTablaTareas();
            },
            error: function(xhr, status, error) {
                alert('Error al eliminar la tarea.');
                console.error(xhr.responseText);
            }
        });
    });
    
    $(document).on('submit', '.edit-tarea-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var tareaId = form.data('assignment-id');
        var nombre = form.find('input[name="nombre"]').val();
        var descripcion = form.find('input[name="descripcion"]').val();
        var prioridad = form.find('select[name="prioridad"]').val();
        var url = form.data('url');
    
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'tarea_id': tareaId,
                'nombre': nombre,
                'descripcion': descripcion,
                'prioridad': prioridad,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                alert(response.message);
                var trabajadores = response.trabajadores;  // Recibimos la lista de trabajadores
                var trabajadoresOptions = '<option value="">Selecciona un trabajador</option>';
                
                // Construimos el <option> para cada trabajador
                trabajadores.forEach(function(trabajador) {
                    trabajadoresOptions += `<option value="${trabajador.id}">${trabajador.nombre}</option>`;
                });
    
                var row = $('#editForm' + tareaId).prev();
                row.html(`
                    <td>${response.nombre}</td>
                    <td>${response.descripcion}</td>
                    <td>${response.prioridad}</td>
                    <td>
                        <form method="POST" id="formAsignar${tareaId}" class="assign-task-form" data-task-id="${tareaId}" data-url="${form.data('url')}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <input type="hidden" name="tarea_id" value="${tareaId}">
                            <div class="form-group">
                                <select name="trabajador_id" class="form-control" required>
                                    ${trabajadoresOptions}
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">Asignar</button>
                        </form>                    
                    </td>
                    <td>
                        <form method="POST" id="formEliminarTarea${usuarioid}" class="delete-task-form" data-tarea-id="${usuarioid}" data-url="${form.data('url')}">
                            <input type="hidden" name="tarea_id" value="${usuarioid}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button type="submit" class="btn btn-icon">
                                <img src="${staticUrl}delete-icon.png" alt="Eliminar">
                            </button>
                        </form>
                        <button type="button" class="btn btn-icon" onclick="toggleEditForm('${usuaioid}')">
                            <img src="${staticUrl}edit-icon.png" alt="Editar">
                        </button>
                    </td>
                `);
                cancelEdit(usuarioid);
            },
            error: function(xhr, status, error) {
                alert('Error al editar la tarea.');
                console.error(xhr.responseText);
            }
        });
    });    
    


});

function recargarTablaAsignacion() {
    $.ajax({
        url: '/obtener-tabla-asignaciones/',
        type: 'GET',
        success: function(data) {
            $('#assignmentTable tbody').html(data.html);
        },
        error: function(xhr, status, error) {
            console.error('Error al recargar la tabla de asignaciones:', error);
        }
    });
}

function recargarTablaTareas() {
    $.ajax({
        url: '/obtener-tabla-tareas/',
        type: 'GET',
        success: function(data) {
            $('#taskTable tbody').html(data.html);
        },
        error: function(xhr, status, error) {
            console.error('Error al recargar la tabla de tareas:', error);
        }
    });
}

$(document).ready(function() {
    $('#reporteProblema').on('change', function() {
        var selectedOption = $(this).find(':selected');
        var selectedId = selectedOption.val();
        var selectedTipo = selectedOption.text().split('-')[1]; // Extraer el tipo de incidente
        var selectedDescripcion = selectedOption.data('descripcion'); // Obtener la descripción del data-atributo

        if (selectedId) {
            $('#newTaskNombre').val(selectedId + ' - ' + selectedTipo.trim()); // ID + tipo
            $('#newTaskDescripcion').val(selectedDescripcion); // Descripción
        } else {
            $('#newTaskNombre').val('');
            $('#newTaskDescripcion').val('');
        }
    });

    $('#newTaskForm').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var nombre = form.find('input[name="nombre"]').val();
        var descripcion = form.find('input[name="descripcion"]').val();
        var prioridad = form.find('select[name="prioridad"]').val();

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'nombre': nombre,
                'descripcion': descripcion,
                'prioridad': prioridad,
            },
            success: function(response) {
                alert(response.message);
                $('#taskTable tbody').html(response.html);  // Recargar la tabla de tareas
                // Limpiar los campos del formulario
                $('#newTaskForm')[0].reset(); // Limpiar todos los campos del formulario
                toggleNewTaskForm();  // Cerrar el formulario de creación de tarea
            },
            error: function(xhr, status, error) {
                alert('Error al crear la tarea.');
                console.error(xhr.responseText);
            }
        });
    });
});




$('#hideCompleted').on('change', function() {
    var isChecked = $(this).is(':checked');
    var stateSelect = $('#filterState');
    var prioritySelect = $('#filterPriority');

    if (isChecked) {
        // Solo mostrar estados "En espera" y "En progreso" y deshabilitar el select de estado
        stateSelect.val('');
        stateSelect.find('option[value="Completada"]').hide();
        stateSelect.prop('disabled', true);  // Deshabilitar el select de estado

    } else {
        // Mostrar todas las opciones de estado y prioridad
        stateSelect.find('option[value="Completada"]').show();
        stateSelect.prop('disabled', false);

    }
});
 

$(document).ready(function() {
    document.getElementById('createUserBtn').addEventListener('click', toggleNewTaskForm);
});

