import { GETUSEREREQUEST, GETUSERTABLEDATA} from "./action.table"
let initial_state  = {
    ToDoID : "",
    Title : "",
    Status : "",
   
}

let User_reducer = (state = initial_state, action) =>{
    // console.log("action.payload", action.payload)
    switch(action.type){
        
        case GETUSEREREQUEST :           
            return {
                state,
            }
        case GETUSERTABLEDATA :
           
            return {
                
                User_Data :action.payload,
            }
        default:
            return state;
    }
}

export {User_reducer};