import {GETCONTACTREQUEST, GETCONTACTDATA} from "./action.contact"

let initial_state  = {
    ID : "",
    NAME : "",
    AGE : "",
    EMAIL : ""
}

let Contact_reducer = (state = initial_state, action) =>{
    // console.log("decrement payload", action.payload)
    switch(action.type){
        case GETCONTACTREQUEST :           
            return {
                ...state,
            }
            case GETCONTACTDATA :
           
            return {
                // state,
                Contact_Data :action.payload,
            }
        default:
            return state;
    }
}

export {Contact_reducer};