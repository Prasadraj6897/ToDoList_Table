import {GETDATAREQUEST,GETTABLEDATA} from "./action.table"

let initial_state  = {
    ToDoID : "",
    Title : "",
    Status : "",
   
}

let Table_reducer = (state = initial_state, action) =>{
    // console.log("decrement payload", action.payload)
    switch(action.type){
        case GETDATAREQUEST :           
            return {
                ...state,
            }
        case GETTABLEDATA :
           
            return {
                state,
                Table_Data :action.payload,
            }
        
        default:
            return state;
    }
}

export {Table_reducer};