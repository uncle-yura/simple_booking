'use strict';

class Event {
    constructor(event, id='', min_step=0) {
        this.event = new Object;
        Object.assign(this.event, event);

        this._pos_start = getPosFromStamp(this.event.start);
        this.pos_end = getPosFromStamp(this.event.end);
        this.duration = this.event.end - this.event.start;
        this.min_step = min_step;

        this.card = document.createElement('div');
        
        this.card.id = id;

        this._dragging = false;

        if(!id) {
            this.card.onclick =  this.click_callback.bind(this);
            this.card.className = "timetable_event bg-warning";
        } else {
            this.card.onmousedown = this.mouse_down.bind(this);
            this.card.onmouseup = this.mouse_up.bind(this);
            this.card.className = "timetable_event bg-success";
        }

        this.update_position();
        this.update_text();
    }

    mouse_down() {
        this.dragging = true;
    }

    mouse_up() {
        if(this.dragging) moveTimetable(this._pos_start - 1/6);

        this.dragging = false;
    }

    update_text() {
        this.card.innerHTML = "<div class='timetable_event_text'>"+getLocalText(this.card.id ? 'fromTo' : 'busyFromTo', getLocaleTimeString(this.event.start), getLocaleTimeString(this.event.end))+"</div>";
    }

    update_position() {
        this.card.style = "height: " + (this.pos_end - this._pos_start)*100 + "%; top: " + this._pos_start*100 + "%";

        if(this.card.id && !this.dragging) moveTimetable(this._pos_start - 1/6);
    }

    check_new_position(position_start) {
        if( position_start >= 1 || position_start<0 ) return false;

        let pos_duration = this.pos_end - this._pos_start;
        let position_end = pos_duration + position_start;
        let round_position = true;
        let next_start = 1;
        let previous_end = 0;

        for(let i=0; i<selectedDayEventsObjList.length; i++) {
            let event = selectedDayEventsObjList[i].event;
            let start = getPosFromStamp(event.start);
            let end = getPosFromStamp(event.end);
    
            if(end < position_start) {
                previous_end = end;
            }
            
            if(start > position_end) {
                next_start = start;
            }

            if( checkPosition(position_start, position_end, event) ) {
                continue;
            } 
            else {
                round_position = false;
                let dif_next;
                let dif_prev;
                if(end+pos_duration<1) {
                    if((i==selectedDayEventsObjList.length-1) || (i<selectedDayEventsObjList.length-1) && 
                            checkPosition(end, end+pos_duration, selectedDayEventsObjList[i+1].event)) {
                        dif_next = end - position_start;
                    }
                }
                
                if(start - pos_duration>=0){
                    if(i==0 || (i>0 && checkPosition(start - pos_duration, start, selectedDayEventsObjList[i-1].event))) {
                        dif_prev = (start - pos_duration) - position_start;
                    } 
                }
      
                if((dif_next && dif_prev == undefined) || 
                    (!(dif_next==undefined) && !(dif_prev==undefined) && (dif_next < Math.abs(dif_prev)))) {
                    position_start += dif_next;
                }
                else if((dif_next == undefined && dif_prev) || 
                    (!(dif_next==undefined) && !(dif_prev==undefined) && (dif_next > Math.abs(dif_prev)))) {
                    position_start += dif_prev;
                }
                else {
                    return false;
                }
                
            }
        }
        if(round_position) {
            let timeout = this.min_step/1440;
            position_start = previous_end + Math.round((position_start - previous_end)/timeout)*timeout;
        }

        return position_start;
    }

    get dragging() {
        return this._dragging;
    }

    set dragging(value) {
        this._dragging = value;
        if(!value) {
            $(this.card).removeClass('draggable');
        } else {
            $(this.card).addClass('draggable');
        }
    }

    get pos_start() {
        return this._pos_start;
    }

    set pos_start(value) {
        if((value=this.check_new_position(value)) === false) return;

        this._pos_start = value;
        this.pos_end = value + this.duration/86400000;
        this.event.start = getStampFromPos(this._pos_start,this.event.start);
        this.event.end = this.event.start+this.duration;
        
        this.update_position();    
        this.update_text();

        updateDateStrings(this.event.start);
    }

    click_callback() {
        drawNewEvent(this._pos_start + (this.pos_end-this._pos_start)/2);
    }
}
