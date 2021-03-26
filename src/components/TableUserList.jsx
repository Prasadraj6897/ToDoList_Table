import React from "react";
import { MDBContainer, MDBBtn, MDBCard, MDBCardBody, MDBCardImage, MDBCardTitle, MDBCardText, MDBRow, MDBCol, MDBView, MDBIcon } from 'mdbreact';



let TableUserList = (props) => {
    let user = props.selectedUSer

    let userId = props.userId
    let title = props.title
    return  (
         
        <MDBContainer>
            {/* <pre>{JSON.stringify(value)}</pre> */}
            {user != null ? (
                <MDBCard>
                    {/* <pre>{JSON.stringify(user)}</pre> */}
                    
                    
                    <MDBCardBody cascade className='text-center'>
                        <MDBCardTitle className='card-title'>
                        <strong>User Detail</strong>
                        </MDBCardTitle>

                        <p className='font-weight-bold blue-text'>{user.id}</p>

                        <MDBCardText>
                            {userId}<br></br>
                            {title}<br></br>
                        {user.name}<br></br>
                        {user.email}
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

export default TableUserList;