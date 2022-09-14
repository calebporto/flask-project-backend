$(document).ready(function() {
    $('#time').on('change', function() {
        $('.table.table-sm').text('');
        $('.table.table-sm').append('<div class="spinner-grow text-danger" role="status"><span class="sr-only"></span></div>');

        let period = $(this).val()
        window.location.href = "/painel-administrativo/historico-de-dizimos?time="+ period +"";
    })
})