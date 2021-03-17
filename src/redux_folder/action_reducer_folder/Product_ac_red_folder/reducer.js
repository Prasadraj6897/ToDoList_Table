import {INCREMENT, DECREMENT} from "./action"

let initial_state  = {
    Product_Name : "TIMEX Analog Watch - For Men",
    Product_Price : 1200,
    Product_Image : "https://rukminim1.flixcart.com/image/800/960/jvo4scw0/watch/g/q/u/tw000r424-timex-original-imafggytsgybedyq.jpeg?q=50",
    Product_Quantity : 1
}

let Product_reducer = (state = initial_state, action) =>{
    // console.log("decrement payload", action.payload)
    switch(action.type){
        case INCREMENT :
            
            return {
                ...state,
                Product_Quantity :state.Product_Quantity + 1,
            }
            case DECREMENT :
           
            return {
                ...state,
                Product_Quantity :state.Product_Quantity - 1,
            }
        default:
            return state;
    }
}

export {Product_reducer};