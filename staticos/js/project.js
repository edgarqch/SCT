window.onload = function(){
    var fecha = new Date(); //Fecha actual
    var mes = fecha.getMonth()+1; //obteniendo mes
    var dia = fecha.getDate(); //obteniendo dia
    var ano = fecha.getFullYear(); //obteniendo año
    if(dia<10)
      dia='0'+dia; //agrega cero si el menor a 10
    if(mes<10)
      mes='0'+mes //agrega cero si el menor a 10
    document.getElementById('fechaActual').value=ano+"-"+mes+"-"+dia;
    
    
    var hora = new Date();
    var horaActual = hora.getHours();
    var minuto = hora.getMinutes();
    var segundos = hora.getSeconds();
    if(minuto<10)
    minuto = '0'+minuto;
    document.getElementById('horaActual').value = horaActual+":"+minuto+":"+segundos;
    
    var anio = new Date();
    var year = anio.getFullYear();
    document.getElementById('year').value=year;
  }


// var fecha = new Date();
// var txtfecha = document.getElementById("txtfecha");
// txtfecha.value = (fecha.getDate() + "/" + (fecha.getMonth() +1) + "/" + fecha.getFullYear());

    $(function(){
      $('#dynamic_select').on('change', function () {
          var url = $(this).val(); // get selected value
          if (url) { // require a URL
              window.location = url; // redirect
          }
          return false;
      });
    });