import React, {useState} from 'react'
import {  MDBContainer, MDBRow, MDBCol, MDBBtn  } from 'mdbreact';
import {useDispatch, useSelector} from "react-redux"
import {Data_action} from "../redux_folder/action_reducer_folder/TableAppFolder/action.table"
import DataList from "./Table_List"
import TableUserList from "./TableUserList"

let Table_Task = () =>{
    var data= ""
    // let userdata = ""
    const [userdata, setNewuserdata] = useState({});
    const usedispatch = useDispatch();
    let Table_list = useSelector((state) =>{
        // console.log("state.Table_root_reducer.Table_Data",state.Table_root_reducer.Table_Data)
        // setNewData({data:state.Table_root_reducer.Table_Data})
        let data = state.Table_root_reducer.Table_Data
        
        return data
    })

   

    
    let User_list = useSelector((state) =>{
        // console.log(state.Table_root_reducer.Table_Data)
        data = state.User_root_reducer.User_Data
        // console.log("data", data)
        
        return data
    })
    let handleView = () =>{
        console.log("handleView")
        usedispatch(Data_action())
    }
    let PutData = (data) =>{
      
      
        
        
        setNewuserdata(data)
        console.log("Putdata", userdata);
      }

    return (
        <div>
            <h1>Contact List Redux</h1>
            {/* <pre>{JSON.stringify({Table_list})}</pre> */}
            <MDBRow>
                <MDBCol size="8">
                    <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {handleView} >Show Table</MDBBtn>
                    <DataList TableData={Table_list} 
                        putData={PutData}
                    />
                </MDBCol>
                <MDBCol size="4">
							<TableUserList selectedUSer={data} userId = {userdata.userId} title={userdata.title}/>
                </MDBCol>
            </MDBRow>
            </div>
    )
}

export default Table_Task;