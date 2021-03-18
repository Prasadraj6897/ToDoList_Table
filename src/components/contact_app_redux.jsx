import React, { useState, useEffect } from "react";
import { MDBContainer, MDBRow, MDBCol, MDBTable, MDBTableBody, MDBTableHead, MDBBtn } from "mdbreact";
import {useDispatch, useSelector} from "react-redux"
import {contact_action } from "../redux_folder/action_reducer_folder/contactAppFolder/action.contact"
import ContactTable from "./contact_table"
import ContactCard from "./contact_card";

let ContactAppREdux = () =>{ 
    // const [contacts, setNewcontacts] = useState(null);
    const usedispatch = useDispatch();
    const [Contact, selectedContact] = useState(null);

    let contact_list = useSelector((state) =>{
        return state.Contact_root_reducer
    })

    let handleView = () =>{
        console.log("handleView")
        usedispatch(contact_action())
    }

    let PutData = (data) =>{
    
        selectedContact(data)
        console.log("Putdata", data);
      }

    return(
        <MDBContainer>
            <h1>Contact List Redux</h1>
            {/* <pre>{JSON.stringify({contact_list})}</pre> */}
            <MDBRow>
                <MDBCol size="8">
                <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {handleView} >Show Table</MDBBtn>
                    <ContactTable TableContact={contact_list} putData={PutData}/>
                </MDBCol>
                <MDBCol size="4">
							<ContactCard selectedContact={Contact} />
					</MDBCol>
            </MDBRow>
        </MDBContainer>
    )

}
export default ContactAppREdux;