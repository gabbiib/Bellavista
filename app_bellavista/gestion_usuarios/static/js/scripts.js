
function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    const opciones = { year: 'numeric', month: 'short', day: 'numeric' };
    return fecha.toLocaleDateString('en-US', opciones);
}

function toggleEditForm(id) {
    var editFormTask = document.getElementById('editForm' + id); // Formulario de edición para Tareas
    var editFormAssignment = document.getElementById('editRow' + id); // Formulario de edición para Asignaciones

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

// Mostrar/Ocultar el formulario de filtros
function toggleFilterForm() {
    var form = document.getElementById('filterForm');
    var createTaskForm = document.getElementById('createTaskForm');  // Formulario de crear tarea

    // Ocultar el formulario de creación de tareas si está abierto
    if (createTaskForm.style.display !== 'none') {
        createTaskForm.style.display = 'none';
    }

    // Mostrar u ocultar el formulario de filtros
    form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'block' : 'none';
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





// Mostrar/Ocultar los filtros adicionales para tareas asignadas
function toggleAssignedFilters() {
    var filterList = document.getElementById('filterList').value;
    var commonFilters = document.getElementById('commonFilters');
    var assignedTaskFilters = document.getElementById('assignedTaskFilters');

    if (filterList === 'asignadas') {
        // Mostrar los filtros específicos de tareas asignadas y los comunes
        commonFilters.style.display = 'block';
        assignedTaskFilters.style.display = 'block';
    } else {
        // Mostrar solo los filtros comunes
        commonFilters.style.display = 'block';
        assignedTaskFilters.style.display = 'none';
    }
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

    // Manejador de evento para formularios de asignación de tareas
    $(document).on('submit', '.assign-task-form', function(e) {
        e.preventDefault(); // Previene el envío por defecto del formulario

        var form = $(this);
        var taskId = form.data('task-id'); // Obtiene el ID de la tarea
        var trabajadorId = form.find('select[name="trabajador_id"]').val();
        var url = form.data('url');  // Obtiene la URL de data-url

        if (!trabajadorId) {
            alert('Por favor, seleccione un trabajador.');
            return;
        }

        // Confirmación antes de asignar
        if (!confirm('¿Asignar esta tarea?')) {
            return;
        }

        $.ajax({
            type: 'POST',
            url: asignarTareaUrl,
            data: {
                'tarea_id': taskId,
                'trabajador_id': trabajadorId,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                alert(response.message);
                
                // Eliminar la fila de la tarea asignada de la lista de tareas no asignadas
                $('#formAsignar' + taskId).closest('tr').remove();
        
                // Recargar ambas tablas para asegurarnos de que estén actualizadas
                recargarTablaAsignacion();
                recargarTablaTareas();
            },
            error: function(xhr, status, error) {
                alert('Error al asignar la tarea.');
                console.error(xhr.responseText);
            }
        });        
        
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
        var tareaId = form.data('tarea-id');
        var url = form.data('url');
    
        if (!confirm('¿Eliminar esta tarea?')) {
            return;
        }
    
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'tarea_id': tareaId,
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
                        <form method="POST" id="formEliminarTarea${tareaId}" class="delete-task-form" data-tarea-id="${tareaId}" data-url="${form.data('url')}">
                            <input type="hidden" name="tarea_id" value="${tareaId}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button type="submit" class="btn btn-icon">
                                <img src="${staticUrl}delete-icon.png" alt="Eliminar">
                            </button>
                        </form>
                        <button type="button" class="btn btn-icon" onclick="toggleEditForm('${tareaId}')">
                            <img src="${staticUrl}edit-icon.png" alt="Editar">
                        </button>
                    </td>
                `);
                cancelEdit(tareaId);
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




// Función para aplicar filtros con AJAX
$(document).on('submit', '#filterForm', function(e) {
    e.preventDefault();
    var form = $(this);
    var url = form.attr('action');
    var filterList = form.find('#filterList').val();  // Verifica qué lista está seleccionada
    var filterName = form.find('input[name="filterName"]').val();
    var filterPriority = form.find('select[name="filterPriority"]').val();
    var filterState = form.find('select[name="filterState"]').val();
    var filterDate = form.find('input[name="filterDate"]').val();
    var filterWorker = form.find('select[name="filterWorker"]').val();
    var hideCompleted = $('#hideCompleted').is(':checked') ? 'on' : 'off';

    if (hideCompleted === 'on') {
        filterState = ['En espera', 'En progreso'];  // Filtrar solo por estos estados
    }

    var requestData = {
        'filterList': filterList,
        'filterName': filterName,
        'filterPriority': filterPriority,
        'filterState': filterState,
        'filterDate': filterDate,
        'filterWorker': filterWorker,
        'hideCompleted': hideCompleted,
    };

    if (filterList === 'tareas') {
        // Filtra solo la lista de tareas
        $.ajax({
            type: 'GET',
            url: url,
            data: requestData,
            success: function(response) {
                $('#taskTable tbody').html(response.html_tareas);
            },
            error: function(xhr, status, error) {
                alert('Error al aplicar los filtros en lista de tareas.');
                console.error(xhr.responseText);
            }
        });
    } else if (filterList === 'asignadas') {
        // Filtra solo las tareas asignadas
        $.ajax({
            type: 'GET',
            url: url,
            data: requestData,
            success: function(response) {
                $('#assignmentTable tbody').html(response.html_asignaciones);
            },
            error: function(xhr, status, error) {
                alert('Error al aplicar los filtros en tareas asignadas.');
                console.error(xhr.responseText);
            }
        });
    }
});


// Función para limpiar los filtros sin recargar la página
$('#clearFilters').on('click', function() {
    $('#filterForm').trigger('reset'); // Resetear el formulario de filtros
    
    $('#filterName').val('');  // Limpiar el campo de nombre
    $('#filterPriority').val('');  // Limpiar el campo de prioridad
    $('#filterState').val('');  // Limpiar el campo de estado
    $('#filterDate').val('');  // Limpiar el campo de fecha
    $('#filterWorker').val('');  // Limpiar el campo de trabajador
    $('#hideCompleted').prop('checked', false);

    // Restablecer el select de estado para que muestre todas las opciones, incluso cuando el checkbox está marcado
    $('#filterState').prop('disabled', false);  // Asegurarse de que el campo estado no esté deshabilitado
    $('#filterState option').show();  // Mostrar todas las opciones de estado
    
    // Recargar ambas tablas sin filtros
    $.ajax({
        type: 'GET',
        url: '/obtener-tabla-tareas/',  // Ruta que devuelve la tabla de tareas sin filtrar
        success: function(data) {
            $('#taskTable tbody').html(data.html);  // Recargar la tabla de tareas
        }
    });
    $.ajax({
        type: 'GET',
        url: '/obtener-tabla-asignaciones/',  // Ruta que devuelve la tabla de asignaciones sin filtrar
        success: function(data) {
            $('#assignmentTable tbody').html(data.html);  // Recargar la tabla de asignaciones
        }
    });
});

// Función para cancelar los filtros sin recargar la página
$('#cancelFilters').on('click', function() {
    toggleFilterForm();  // Ocultar el formulario de filtros
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
    document.getElementById('createTaskBtn').addEventListener('click', toggleNewTaskForm);
    document.getElementById('filterBtn').addEventListener('click', toggleFilterForm);
});

