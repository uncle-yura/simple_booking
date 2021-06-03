'use strict';

function drawNewEvent(position) {
    let new_event = document.getElementById("id_timetable_new_date")

    if(!new_event){
        new_event = document.createElement('div');
        new_event.className = "shadow-lg p-2 mb-1 rounded timetable_event";
        new_event.style = "height: 10%; top: "+position*100+"%";
        new_event.innerHTML = "New event from ";
        new_event.id = "id_timetable_new_date";
        $("#id_timetable_events").append(new_event);
    }

    new_event.style = "height: "+ total_time/3600*4 +"%; top: "+position*100+"%";
}

function normalize_date(date, event){
    if(event > date.setHours(23,59)) {
        return date.getTime();
    }
    else if(event < date.setHours(0,0)) {
        return date.getTime();
    }
    else {
        return event;
    }
}

function getLocaleTimeString(date) {
    let time = new Date(date);
    return time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

function getLastDayOfMonth(year, month) {    
    let date = new Date(year, month + 1, 0);
    return date.getDate();
}

function filterSelectedDay(a) {
    return (a.start > this.setHours(0,0)) && (a.start < this.setHours(23,59)) ||
        (a.end > this.setHours(0,0)) && (a.end < this.setHours(23,59));
    }

function drawTimetable(date) {
    let currentDate = new Date(date);

    $("#id_timetable_header").html("Booking on " + currentDate.toLocaleDateString());
    $("#id_timetable_events").html("");

    for(let event of eventsList.filter(filterSelectedDay,currentDate)) {
       
        let event_start = normalize_date(currentDate, event.start);
        let event_end = normalize_date(currentDate, event.end);

        let event_time_start = new Date(event_start);
        let event_position_start = (event_time_start.getHours() + event_time_start.getMinutes()/60)*(1/24)*100;

        let card = document.createElement('div');
        card.className = "shadow-lg p-2 mb-1 rounded timetable_event";
        card.style = "height: "+(event_end - event_start)/864000+"%; top: "+event_position_start+"%";
        card.innerHTML = "Busy from " + getLocaleTimeString(event_start) + " to " + getLocaleTimeString(event_end);
        card.onclick = function(e) {
            let timePosition = $(this).outerHeight() + $(this).position().top ;
            timePosition = timePosition/document.getElementById("id_timetable_body").scrollHeight;
            drawNewEvent(timePosition);
        }

        $('#id_timetable_events').append(card);  
    }
}

function drawCalendar(booking_range) {
    $("#id_calendar_body").html("");

    function addMonthName(parent, date) {
        let monthName = document.createElement('div');
        monthName.className = "calendar_month_name";
        monthName.innerHTML = monthStr.split(',')[date.getMonth()];
        parent.append(monthName);  
    }

    function addInactiveDays(parent, date) {
        for (let i=0; i<((date.getDay()||7)-1); i++) {
            let divInnactive = document.createElement('div');
            divInnactive.className = "calendar_day_inactive";
            parent.append(divInnactive);  
        }
    }
    
    let monthDays = document.getElementById("id_calendar_body");
    let firstDay = new Date();
    let lastDay = getLastDayOfMonth(firstDay.getFullYear(), firstDay.getMonth());      
        
    addMonthName(monthDays, firstDay);
    addInactiveDays(monthDays, firstDay);

    for(let i=0; i<booking_range; i++){
        let div = document.createElement('div');
        div.className = "calendar_day_active";
        div.setAttribute("value",firstDay.toISOString());

        div.onclick = function() {
            drawTimetable(this.getAttribute("value"));
            $("#id_day_view_modal").modal('show');
            };

        div.innerHTML = firstDay.getDate();
        monthDays.append(div);

        if (lastDay==firstDay.getDate()) {
            firstDay.setDate(firstDay.getDate()+1);  
            lastDay = getLastDayOfMonth(firstDay.getFullYear(), firstDay.getMonth());     
            if(i<booking_range-1) {                    
                addMonthName(monthDays, firstDay);
                addInactiveDays(monthDays, firstDay);
            }
        }
        else {
            firstDay.setDate(firstDay.getDate()+1);  
        }
    }
}