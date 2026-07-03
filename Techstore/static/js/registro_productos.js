// ====================================================
// Manejo del formulario de registro / edición de productos
// ====================================================

console.log("registro_producto.js cargado correctamente");

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM listo, buscando formulario...");

    const form = document.getElementById('formProducto');

    if (!form) {
        console.error("No se encontró el formulario con id 'formProducto'. Revisa el HTML.");
        return;
    }

    const productoIdInput = document.getElementById('producto_id');

    if (!productoIdInput) {
        console.error("No se encontró el input oculto con id 'producto_id'. Revisa el HTML.");
        return;
    }

    const productoId = productoIdInput.value;
    const esEdicion = productoId !== '';

    console.log("Modo edición:", esEdicion, "| ID:", productoId);

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        console.log("Formulario interceptado, enviando datos...");

        // Construcción de los datos del formulario
        const datos = new FormData();
        datos.append('codigo', document.getElementById('codigo').value.trim());
        datos.append('nombre', document.getElementById('nombre').value.trim());
        datos.append('precio', document.getElementById('precio').value.trim());
        datos.append('categoria', document.getElementById('categoria').value.trim());

        // Define la ruta según sea registro nuevo o edición
        const url = esEdicion ? `/actualizar_producto/${productoId}` : '/guardar_producto';
        console.log("Enviando a:", url);

        fetch(url, {
            method: 'POST',
            body: datos
        })
            .then(response => {
                console.log("Respuesta recibida, status:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("Datos:", data);
                if (data.success) {
                    Swal.fire({
                        title: esEdicion ? "Actualizado" : "Registrado",
                        text: esEdicion
                            ? "Producto actualizado correctamente."
                            : "Producto registrado correctamente.",
                        icon: "success"
                    }).then(() => {
                        window.location.href = '/productos';
                    });
                } else {
                    Swal.fire({
                        title: "Error",
                        text: data.message || (esEdicion ? "Error al actualizar." : "Error al guardar."),
                        icon: "error"
                    });
                }
            })
            .catch((err) => {
                console.error("Error en la petición:", err);
                Swal.fire({
                    title: "Error",
                    text: esEdicion ? "Error al actualizar el producto." : "Error al guardar el producto.",
                    icon: "error"
                });
            });
    });
});