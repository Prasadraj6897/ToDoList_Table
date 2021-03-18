import axios from "axios";

const GETCONTACTREQUEST = "GETCONTACTREQUEST";
const GETCONTACTDATA = "GETCONTACTDATA";

let contact_action = () => {
    console.log("contact_action")
    return async (dispatch) => {
        // console.log("1")
        try{
            
            dispatch({type : GETCONTACTREQUEST})
            // console.log("2")
            let data = await axios.get("https://gist.githubusercontent.com/narasimhareddyprostack/7e344f346f47bc53a889d78b5258d0c9/raw/56d531cb936d9c79e2417e5d0e5d8c9c876800f2/contactlist");
            // console.log("3")
            dispatch({type : GETCONTACTDATA, payload: data.data})
        }catch(error){

        }
    } 
}

export {GETCONTACTREQUEST, GETCONTACTDATA, contact_action}