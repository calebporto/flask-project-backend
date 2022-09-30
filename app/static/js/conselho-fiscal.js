$(document).ready(function(){
    var clickCheck = false
    $('#addAdmButton').on('click', function(){
        if (clickCheck == false) {
            $(".add-adm").append("<div class='add-function'></div>");
            $(".add-function").append("<form class='form' action='/painel-administrativo/conselho-fiscal' method='post'></form>");
            $(".form").append("<select name='add_id' id='select'></select>")
            $("#select").append("<option value='' disabled selected>-- Selecione um usuário--</option>")
            $.getJSON('/painel-administrativo/conselho-fiscal?is_admin=1', function(dados){
                if (dados) {
                    for (var i = 0; i < dados.length; i++) {
                        $("#select").append("<option value='"+ dados[i].id +"'>"+ (dados[i].name).replace(/(^\w{1})|(\s+\w{1})/g, letra => letra.toUpperCase()) +"</option>")
                    };
                };
            });
            $('.form').append('<button type="button" class="add-function-button" data-bs-toggle="modal" data-bs-target="#adicionar">Adicionar</button>')
            $('.form').append('<div class="modal fade" id="adicionar" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">')
            $('#adicionar').append('<div class="modal-dialog" id="modal-dialog">')
            $('#modal-dialog').append('<div class="modal-content" id="modal-content">')
            $('#modal-content').append('<div class="modal-header" id="modal-header">')
            $('#modal-header').append('<h5 class="modal-title" id="exampleModalLabel">Tem certeza?</h5>')
            $('#modal-header').append('<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>')
            $('#modal-content').append('<div class="modal-body" id="modal-body">')
            $('#modal-body').append('Tem certeza que deseja adicionar esse conselheiro fiscal?')
            $('#modal-content').append('<div class="modal-footer" id="modal-footer">')
            $('#modal-footer').append('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>')
            $('#modal-footer').append('<button type="submit" class="btn btn-danger">Confirmar</button>')
        }
        clickCheck = true
    })
})