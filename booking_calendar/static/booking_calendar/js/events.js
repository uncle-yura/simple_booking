'use strict';

$(document).ready(function () {
    updateDefaultStrings();

    $('#newOrderForm').submit( function(event) {
        if(!selectedDayEventsObjList.hasOwnProperty("new_event")) {
            $('#id_calendar_card').popover('show');
            setTimeout(function () {
                $('#id_calendar_card').popover('dispose');
            }, 2000);
            event.preventDefault();

        }
    });

    let select_input = $('#id_work_type');

    select_input.select2({width: '100%'});
    select_input.attr("data-container", "body");
    select_input.attr("data-toggle", "popover");
    select_input.attr("data-placement", "right");
    select_input.attr("data-content", getLocalText('typeError'));

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
    updateDefaultStrings();
    getMasterData($(this));
    });

$('#id_work_type').change(function () {
    updatePriceAndTimeStrigs();
});
