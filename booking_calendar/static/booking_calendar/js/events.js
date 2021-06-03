'use strict';

$(document).ready(function () {
    $('#id_work_type').empty();

    for(let i=0; i<7; i++) {
        let div = document.createElement('div');
        div.className = "calendar_weekday_name";
        div.innerHTML = dayNames.split(',')[i];
        $('#id_calendar_header').append(div);  
    }      

    let table = document.createElement('table');
    table.className = 'timetable_events_container';
    for(let i=0; i<24; i++){
        let tr = document.createElement('tr');
        tr.className = "timetable_hours";
        tr.innerHTML = "<td class='timetable_td'>"+i+":00</td>";
        table.append(tr);
    }      
    table.onclick = function(e) {
        let timePosition = (e.pageY - $(this).offset().top)/$(this).height();
        drawNewEvent(timePosition);
    }
    
    $('#id_timetable_body').append(table); 
    });

$('#id_day_view_modal').on('shown.bs.modal', function () {
    $("#id_timetable_body").animate({ scrollTop: document.getElementById("id_timetable_body").scrollHeight/3 }, 600);
    });

$('#id_master').change(function () {
    getMasterData($(this));
    });

$('#id_work_type').change(function () {
        total_price = 0;
        total_time = 0;
        for (let option of this.options) {
            if (option.selected) {
                total_price+=parseFloat(option.getAttribute('price'));
                total_time+=parseFloat(option.getAttribute('time'));
            }
        }

        $('#order_total_price').text("Total price: "+total_price)
        $('#order_total_time').text("Total time: "+total_time/60);
    });