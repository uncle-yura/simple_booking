'use strict';

function moveTimetable(pos) {
    $("#id_timetable_body").animate({ scrollTop: document.getElementById("id_timetable_body").scrollHeight*pos }, 600);
}

function getPosFromStamp(timestamp) {
    let time = new Date(timestamp);
    return (time.getHours() + time.getMinutes()/60)*(1/24);
}

function getStampFromPos(pos, timestamp = 0) {
    let time = new Date(timestamp);
    let hours = Math.floor(pos*24);
    let minutes = Math.floor(((pos*24) % 1)*60);
    return time.setHours(hours,minutes,0,0);
}

function checkPosition(new_start, new_end, event) {
    let event_start = getPosFromStamp(event.start);
    let event_end = getPosFromStamp(event.end);
    if( (new_start <= event_start && new_end >= event_end) || 
        (new_end > event_start && new_end < event_end) || 
        (new_start >= event_start && new_start <= event_end) ) {
        return false;
    }
    return true;
}

function normalize_date(date, event){
    let eventDate = new Date(event);
    if(eventDate.getTime() > date.setHours(23,59,59,999)) {
        return date.getTime();
    }
    else if(eventDate.getTime() < date.setHours(0,0,0,0)) {
        return date.getTime();
    }
    else {
        return eventDate.getTime();
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

function updateDateStrings(event) {
    document.getElementById("id_booking_date").value = (new Date(event)).toISOString();
    document.getElementById("selected_datetime").innerHTML = getLocalText('selDate',
        (new Date(event)).toLocaleTimeString([], {month:'long', day: '2-digit', hour: '2-digit', minute:'2-digit'}));
}

function drawNewEvent(position_start) {
    if( !total_time ) return false;
    if( position_start >= 1 || position_start<0 ) return false;

    if(!selectedDayEventsObjList.hasOwnProperty("new_event")) {
        let start_stamp = getStampFromPos(position_start,selectedDay)
        selectedDayEventsObjList.new_event = new Event({
            'start':start_stamp, 
            'end':start_stamp+total_time*1000},"id_timetable_new_date");
        $("#id_timetable_events").append(selectedDayEventsObjList.new_event.card);

        selectedDayEventsObjList.new_event.pos_start = position_start;
    }
    else {
        selectedDayEventsObjList.new_event.pos_start = position_start;
    }
}

function drawTimetable(date) {
    let currentDate = new Date(date);

    $("#id_timetable_header").html("Booking on " + currentDate.toLocaleDateString());
    
    selectedDayEventsObjList = []
    $("#id_timetable_events").html("");

    let selectedDayList = []

    let eventsList = $.parseJSON(sessionStorage.getItem('events'));

    function filterSelectedDay(date) {
    return eventsList.filter(function(event) {
        let start = new Date(event.start);
        let end = new Date(event.end);
        return (start >= date.setHours(0,0,0,0) && start < date.setHours(23,59,59,999)) ||
            (end > date.setHours(0,0,0,0) && end <= date.setHours(23,59,59,999));
        });
    }

    selectedDayList = filterSelectedDay(currentDate);

    selectedDayList.forEach((event)=>{
        event.start = normalize_date(currentDate, event.start);
        event.end = normalize_date(currentDate, event.end);
    });

    selectedDayList.sort(function (a, b) {
        return a.start - b.start;
    });
    
    for(let event of selectedDayList) {
        let new_event = new Event(event);
        selectedDayEventsObjList.push(new_event)
        $('#id_timetable_events').append(new_event.card);  
    }
}

function drawCalendar(booking_range) {
    $("#id_calendar_body").html("");

    function addMonthName(parent, date) {
        let monthName = document.createElement('div');
        monthName.className = "calendar_month_name";
        monthName.innerHTML = getLocalText('monthNames').split(',')[date.getMonth()];
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
            selectedDay = this.getAttribute("value");
            drawTimetable(selectedDay);
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