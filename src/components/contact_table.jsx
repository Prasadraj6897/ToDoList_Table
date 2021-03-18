import "../css/contactapp.css"

import React from "react";

import { MDBTable, MDBTableBody, MDBTableHead, MDBBtn } from "mdbreact";



let ContactTable = (props) =>{
    let TableContact = props.TableContact.Contact_Data

    let handleView = (contact) => {
        props.putData(contact)
        
    }
    return (
          	
                  
            <MDBTable striped hover>
                {/* <pre>{JSON.stringify(TableContact)}</pre> */}
    
                
            <MDBTableHead color="primary-color" textWhite>
                <tr>
                    <th>ID</th>
                    <th>NAME</th>
                    <th>AGE</th>
                    <th>EMAIL</th>
                    <th>VIEW</th>
                    
                </tr>
            </MDBTableHead>
            <MDBTableBody>
                {TableContact != null ? (
                    <>
                    {TableContact.map((contact, id) => {
                        return ( 
                            <tr key = {id} data-uuid={contact.login.uuid} >
                                <td>{contact.login.uuid}</td>
                                <td>{contact.name.last}</td>
                                <td>{contact.dob.age}</td>
                                <td>{contact.email}</td>
                                <td>
                                <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {() =>handleView(contact)} >view</MDBBtn>
                                    
                                </td>
                            </tr>
                        )
                    })

                    }
                    </>
                    ) : null}
            </MDBTableBody>
        </MDBTable> 
					
      
       
    )

}

export default ContactTable;