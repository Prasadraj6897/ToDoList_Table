import React, {useState}  from "react";
import { MDBContainer, MDBRow, MDBCol,MDBDataTable, MDBTable, MDBTableBody, MDBTableHead, MDBBtn,MDBDataTableV5  } from "mdbreact";
import {User_action} from "../redux_folder/action_reducer_folder/TableAppFolder/action.table"
import {useDispatch, useSelector} from "react-redux"



let DataList = (props) =>{
    const usedispatch = useDispatch();
    let rows =  props.TableData
    let columns =  props.TableData
     
    let datatable = null
    if(rows == {})
    {
        // rows = {}
    }
    else{
        console.log(rows);
        

        datatable =  {columns: [
            {
              label: 'id',
              field: 'id',
              width: 150,
              attributes: {
                'aria-controls': 'DataTable',
                'aria-label': 'Name',
              },
            },
            {
              label: 'title',
              field: 'title',
              width: 270,
            },
            {
              id: 'completed' ,
              label: 'completed',
              field: 'completed',
              width: 200,
              
            },
 
          ],
          rows
        }
          
    }

    
    // console.log(columns)
    let data = {rows}
    // data = columns
    // const [datas, setTabledata] = useState({})
    // setTabledata({columns},[])
    let handleView = (data) => {
        // props.putData(contact)
        console.log("data--data", data.id)
        usedispatch(User_action(data.id))
        props.putData(data)
    }
    return (
        
            <MDBContainer>
            
               
            <pre>{JSON.stringify(data)}</pre>
                    
                        {/* <MDBDataTable
                            striped
                            bordered
                            small
                            data={...data}
                        /> */}
                  {/* {rows !=" " ? <MDBDataTableV5 hover entriesOptions={[5, 20, 25]} entries={5} pagesAmount={4} data={datatable} entriesLabel="Show entries" searchTop searchBottom={false} />: ""} */}
                    <MDBTable striped hover>
                
    
                
                            <MDBTableHead color="primary-color" textWhite>
                                <tr>
                                    <th>TableID</th>
                                    <th>Title</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                    
                                    
                                </tr>
                            </MDBTableHead>
                            <MDBTableBody>
                                {columns != null ? (
                                    <>
                                    {columns.map((data, id) => {
                                        return ( 
                                            <tr key = {id}  >
                                                <td>{data.id}</td>
                                                <td>{data.title}</td>
                                                <td>{data.completed.toString()}</td>
                                                
                                                <td>
                                                <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {() =>handleView(data)} >view</MDBBtn>
                                                    
                                                </td>
                                            </tr>
                                        )
                                    })

                                    }
                                    </>
                                    ) : null}
                            </MDBTableBody>
                    </MDBTable> 
            </MDBContainer>        
        
    )
}

export default DataList;