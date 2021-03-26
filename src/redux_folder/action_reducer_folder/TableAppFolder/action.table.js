import axios from "axios";

const GETDATAREQUEST = "GETDATAREQUEST";
const GETTABLEDATA = "GETTABLEDATA";
const GETUSEREREQUEST = "GETUSEREREQUEST";
const GETUSERTABLEDATA = "GETUSERTABLEDATA";

const link = "https://jsonplaceholder.typicode.com/users"
let Data_action = () => {
    // console.log("Data_action")
    return async (dispatch) => {
        // console.log("1")
        try{
            
            dispatch({type : GETDATAREQUEST})
            // console.log("2")
            let response = await axios.get("https://jsonplaceholder.typicode.com/todos");
            // console.log("3")
            dispatch({type : GETTABLEDATA, payload: response.data})
        }catch(error){

        }
    } 
}

let User_action = (id) => {
    // console.log("User_action")
    return async (dispatch) => {
        // console.log("1")
        try{
            
           
            let response = await axios.get(link + '/' + id);
            console.log("responseresponse", response.data)
            dispatch({type : GETUSERTABLEDATA, payload: response.data})
        }catch(error){

        }
    } 
}

export {GETDATAREQUEST,GETTABLEDATA, GETUSEREREQUEST, GETUSERTABLEDATA, Data_action, User_action}