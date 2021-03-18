import React from "react";
import { MDBContainer, MDBBtn, MDBCard, MDBCardBody, MDBCardImage, MDBCardTitle, MDBCardText, MDBRow, MDBCol, MDBView, MDBIcon } from 'mdbreact';



let ContactCard = (props) => {
    let contact = props.selectedContact
    return  (
         
        <MDBContainer>
            {contact != null ? (
                <MDBCard>
                    {/* <pre>{JSON.stringify(contact)}</pre> */}
                    
                    <MDBCardImage
                        hover
                        overlay='white-light'
                        className='card-img-top'
                        src={contact.picture.large}
                        alt='man'
                    />

                    <MDBCardBody cascade className='text-center'>
                        <MDBCardTitle className='card-title'>
                        <strong>{contact.name.last}</strong>
                        </MDBCardTitle>

                        <p className='font-weight-bold blue-text'>{contact.email}</p>

                        <MDBCardText>
                        {contact.location.city}
                        </MDBCardText>

                        <MDBCol md='12' className='d-flex justify-content-center'>
                        <MDBBtn rounded floating color='fb'>
                            <MDBIcon size='lg' fab icon='facebook-f'></MDBIcon>
                        </MDBBtn>

                        <MDBBtn rounded floating color='tw'>
                            <MDBIcon size='lg' fab icon='twitter'></MDBIcon>
                        </MDBBtn>

                        <MDBBtn rounded floating color='dribbble'>
                            <MDBIcon size='lg' fab icon='dribbble'></MDBIcon>
                        </MDBBtn>
                        </MDBCol>
                    </MDBCardBody>
                </MDBCard>
            ): null}  
        </MDBContainer>
    )

}

export default ContactCard;