import {INCREMENT} from "./action"

let initial_state  = {
    init_value : 0
}
// let counter = 0

let increment_reducer = (state = initial_state, action) =>{
    // console.log("increment payload", action.payload)
    console.log(" action.payload",  action.payload)
    switch(action.type){
        case INCREMENT :
            // state = action.payload
            // if(counter == 0)
            // {
                // counter++
                let incre_value  = state.init_value + action.payload
                state.init_value = incre_value
                
                
                console.log("state.init_value", state.init_value)
                return {
                    // ...state,
                    incre_value
                
                // }
            }
            // else {
            //     state.init_value = 
            // }
        default:
            return state;
    }
    
}

export {increment_reducer}