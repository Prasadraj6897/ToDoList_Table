const INCREMENT = "INCREMENT";
const DECREMENT = "DECREMENT";

let increment_action = () => {
    
    return {
        type : INCREMENT,
        
    }
}

let decrement_action = () => {
  
    return {
        type : DECREMENT,
        
    }
}

export {INCREMENT, DECREMENT, increment_action, decrement_action}