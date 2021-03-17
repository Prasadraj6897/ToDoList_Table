const INCREMENT = "INCREMENT";
const DECREMENT = "DECREMENT";

let increment_action = (increment) => {
    console.log("increment", increment.value)
    return {
        type : INCREMENT,
        payload: increment.value
    }
}

let decrement_action = (decrement) => {
    // console.log("decrement", decrement)
    return {
        type : DECREMENT,
        payload: decrement.value
    }
}

export {INCREMENT, DECREMENT, increment_action, decrement_action}

