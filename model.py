from path import Station, Path
import datetime
from datetime import datetime, time, timedelta, date
import raw_req

def get_path(dep_st: Station, arr_st: Station, date : time = datetime.now(), col: int = 10) -> list[Path]: 
    json = raw_req.get_path(dep_st.id, arr_st.id, date) 
    
    timeobj = date
    cur_time = timedelta(hours=timeobj.hour, minutes=timeobj.minute, seconds=timeobj.second)
    
    cur_list = list()
    
    for path in json:
        
        if (cur_time > raw_req.str_to_time(path["departureTime"])):
            continue
        
        cur_list.append(
            Path(
                path["scheduleId"],
                dep_st, arr_st,
                Station(path['startStationId'], path['startStationName']), Station(path['finishStationId'], path["finishStationName"]),
                raw_req.str_to_time(path["departureTime"]), raw_req.str_to_time(path["arrivalTime"]),
                path["cost"], not (path["trainCategoryId"] == 4)
            )
        )
        
        if len(cur_list) == col:
            break
        
    return cur_list

def req(station_from: str, station_to: str, col: int = 10) -> None:
    return get_path(get_station(station_from), get_station(station_to), col=col)

def get_station(station: str) -> Station:
    json = raw_req.get_station(station)
    return Station(
                    json["id"],
                    json["name"]
                  )
    

def get_whole_path(id: int) -> list[tuple[str|bool]]:
    return raw_req.get_whole_path(id)