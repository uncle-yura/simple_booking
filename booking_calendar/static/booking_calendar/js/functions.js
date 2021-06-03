'use strict';

function getPositionFromStamp(timestamp) {
    let time = new Date(timestamp);
    return (time.getHours() + time.getMinutes()/60)*(1/24);
}

function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
  }

function checkPosition(new_start, new_end, event_start, event_end) {
    if( (new_start < event_start && new_end > event_end) || 
        (new_end > event_start && new_end < event_end) || 
        (new_start > event_start && new_start < event_end) ) {
        return false;
    }
    return true;
}

function drawNewEvent(position_start) {
    if( !total_time ) return false;
    if( position_start >= 1 || position_start<0 ) return false;

    for(let i=0; i<selectedDayList.length; i++) {
        let event = selectedDayList[i];
        let start = getPositionFromStamp(event.start);
        let end = getPositionFromStamp(event.end);
        let position_end = (total_time/3600)/24 + position_start;

        if( checkPosition(position_start, position_end, start, end) ){
            continue;
         } else if(((i==selectedDayList.length-1) && (end+(total_time/3600)/24)<1) || 
                ((i<selectedDayList.length-1) && 
                (end+(total_time/3600)/24)<1 && 
                checkPosition(end, end+(total_time/3600)/24, getPositionFromStamp(selectedDayList[i+1].start), getPositionFromStamp(selectedDayList[i+1].end)) )) {
            position_start = end;
            position_end = end+(total_time/3600)/24;
            break;
        } else if((i==0 && (start - (total_time/3600)/24)>=0) || 
                (i>0 &&
                (start - (total_time/3600)/24)>0 && 
                checkPosition(start - (total_time/3600)/24, start, getPositionFromStamp(selectedDayList[i-1].start), getPositionFromStamp(selectedDayList[i-1].end))) ) {
            position_start = start - (total_time/3600)/24;
            position_end = start;
            break;
        } 
    }

    let new_event = document.getElementById("id_timetable_new_date")

    if(!new_event){
        new_event = document.createElement('div');
        new_event.className = "timetable_event";
        new_event.style = "height: "+ total_time/3600*4 +"%; top: "+position_start*100+"%";
        new_event.innerHTML = "New event from " + zeroPad(Math.floor(position_start*24),2) + ":" + zeroPad(Math.floor(((position_start*24) % 1)*60),2);
        new_event.id = "id_timetable_new_date";
        $("#id_timetable_events").append(new_event);
    }

    new_event.style = "height: "+ total_time/3600*4 +"%; top: "+position_start*100+"%";
    new_event.innerHTML = "New event from " + zeroPad(Math.floor(position_start*24),2) + ":" + zeroPad(Math.floor(((position_start*24) % 1)*60),2);
}

function normalize_date(date, event){
    if(event > date.setHours(23,59,59,999)) {
        return date.getTime();
    }
    else if(event < date.setHours(0,0,0,0)) {
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

function filterSelectedDay(event) {
    return (event.start > this.setHours(0,0,0,0)) && (event.start < this.setHours(23,59,59,999)) ||
        (event.end > this.setHours(0,0,0,0)) && (event.end < this.setHours(23,59,59,999));
    }

function drawTimetable(date) {
    let currentDate = new Date(date);

    $("#id_timetable_header").html("Booking on " + currentDate.toLocaleDateString());
    $("#id_timetable_events").html("");

    selectedDayList = eventsList.filter(filterSelectedDay,currentDate);
    selectedDayList.forEach((event)=>{
        event.start = normalize_date(currentDate, event.start);
        event.end = normalize_date(currentDate, event.end);
    });
    selectedDayList.sort(function (a, b) {
        return a.start - b.start;
    });

    for(let event of selectedDayList) {
        let card = document.createElement('div');
        card.className = "timetable_event";
        card.style = "height: "+(event.end - event.start)/864000+"%; top: "+getPositionFromStamp(event.start)*100+"%";
        card.innerHTML = "Busy from " + getLocaleTimeString(event.start) + " to " + getLocaleTimeString(event.end);
        card.onclick = function() {
            let timePosition = $(this).outerHeight()/2 + $(this).position().top ;
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
        monthName.innerHTML = monthNames.split(',')[date.getMonth()];
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