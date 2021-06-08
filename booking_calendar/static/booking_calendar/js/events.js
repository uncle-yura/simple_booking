'use strict';

$(document).ready(function () {
    $('#id_work_type').empty();
    $('#id_work_type').select2({
        width: '100%' 
    });
    $('#id_master').val($("#id_master option:contains('---------')").val());

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

$('body').on("mouseup", function() {
    if(selectedDayEventsObjList.hasOwnProperty("new_event")) {
        selectedDayEventsObjList.new_event.mouse_up();
    }
});

$('body').on("mousemove", function(e) {
    if(selectedDayEventsObjList.hasOwnProperty("new_event") &&
        selectedDayEventsObjList.new_event.dragging) {
            let timetable = document.getElementById("id_timetable_body")
           
            selectedDayEventsObjList.new_event.pos_start = (
                timetable.scrollTop + 
                e.pageY - 
                $(timetable).offset().top - 
                selectedDayEventsObjList.new_event.card.offsetHeight / 2 ) / timetable.scrollHeight;
        }
    });

$('#id_day_view_modal').on('shown.bs.modal', function () {
    moveTimetable(1/3);
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

        $('#order_total_price').text(getLocalText('priceTotal',total_price));
        $('#order_total_time').text(getLocalText('timeTotal',total_time/60));
    });
