import React, {Component} from "react"
import 'mdbreact/dist/css/mdb.css'

import { MDBContainer, MDBRow, MDBCol ,MDBView, MDBBtn,  MDBIcon, MDBCard, MDBCardBody, MDBCardImage, MDBCardTitle, MDBCardText} from "mdbreact";
import {increment_action, decrement_action} from "../redux_folder/action_reducer_folder/Product_ac_red_folder/action"
import {useDispatch, useSelector} from "react-redux"
let Productlist = () => {
    let product_list = useSelector((state) =>{
        return state.Product_root_reducer
    })
    const usedispatch = useDispatch();
    let handleIncrement = () =>{
        usedispatch(increment_action())
    }
    let handleDecrement = () =>{
        usedispatch(decrement_action())
    }

    return(
        
        <MDBContainer>
            <pre>{JSON.stringify(product_list)}</pre>
            <MDBRow>
                <MDBCol md='4'>
                    <MDBCard narrow>
                        <MDBView cascade>
                            <MDBCardImage
                            hover
                            overlay='white-slight'
                            size="sm"
                            className="img-fluid"
                            src={product_list.Product_Image}
                            alt='food'
                            />
                        </MDBView>

                        <MDBCardBody>
                            <h5 className='pink-text'>
                            <MDBIcon icon='watch' /> {product_list.Product_Name}
                            </h5>

                            <MDBCardTitle className='font-weight-bold'>
                             {product_list.Product_Price * product_list.Product_Quantity}
                            </MDBCardTitle>

                            <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {handleIncrement}>
                                <MDBIcon icon="plus" />
                            </MDBBtn>

                            <MDBCardText>
                            {product_list.Product_Quantity}
                            </MDBCardText>
                            {product_list.Product_Quantity == 1 ? <MDBBtn tag="a" size="sm" floating gradient="peach" disabled>
                                <MDBIcon icon="minus" />
                            </MDBBtn> :  <MDBBtn tag="a" size="sm" floating gradient="peach" onClick = {handleDecrement}>
                                <MDBIcon icon="minus" />
                            </MDBBtn>}
                            
                        </MDBCardBody>
                    </MDBCard>
                </MDBCol>
            </MDBRow>
        </MDBContainer>
    )

}

export default Productlist;