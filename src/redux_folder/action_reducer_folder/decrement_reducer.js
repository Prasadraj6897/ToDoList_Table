import {DECREMENT} from "./action"

let initial_state  = {
    init_value : 0
}

let decrement_reducer = (state = initial_state, action) =>{
    // console.log("decrement payload", action.payload)
    switch(action.type){
        case DECREMENT :
            state  = action.payload
            return {
                ...state,
                incre_value :state - 1,
            }
        default:
            return state;
    }
}

export {decrement_reducer}