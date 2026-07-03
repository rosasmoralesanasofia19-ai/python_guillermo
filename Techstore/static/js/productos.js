// ====================================================
// Manejo de la eliminación de productos (SweetAlert2)
// ====================================================

document.addEventListener('DOMContentLoaded', function () {
    const botonesEliminar = document.querySelectorAll('.btn-eliminar');

    // Estilo de botones de confirmación requerido con Bootstrap
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: "btn btn-success",
            cancelButton: "btn btn-danger"
        },
        buttonsStyling: false
    });

    botonesEliminar.forEach(function (boton) {
        boton.addEventListener('click', function () {
            const id = boton.getAttribute('data-id');

            swalWithBootstrapButtons.fire({
                title: "¿Está seguro?",
                text: "No podrá recuperar este producto.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar",
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    eliminarProducto(id);
                }
            });
        });
    });

    // Llama al backend para eliminar el producto seleccionado
    function eliminarProducto(id) {
        fetch(`/eliminar_producto/${id}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: "Eliminado",
                        text: "Producto eliminado correctamente.",
                        icon: "success"
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Error",
                        text: data.message || "Error al eliminar el producto.",
                        icon: "error"
                    });
                }
            })
            .catch(() => {
                Swal.fire({
                    title: "Error",
                    text: "Error al eliminar el producto.",
                    icon: "error"
                });
            });
    }
});