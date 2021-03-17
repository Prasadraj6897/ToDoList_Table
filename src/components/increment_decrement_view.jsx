import React, {Component} from "react"
import 'mdbreact/dist/css/mdb.css'

import { MDBContainer, MDBRow, MDBCol ,MDBInput, MDBBtn,  MDBIcon } from "mdbreact";
import {increment_action, decrement_action} from "../redux_folder/action_reducer_folder/action"
import { connect } from "react-redux"

class Increment_Decrement extends Component {
    constructor(props){
        super(props);
        this.state = {
            value: ''
          };
          this.handlechange = this.handlechange.bind(this)
          this.handleIncrement = this.handleIncrement.bind(this)
          this.handleDecrement = this.handleDecrement.bind(this)
    }
    handlechange (e)  {
        // console.log(e.target.name)
        let text = e.target.value
        this.state.value = parseInt(text, 10)
        this.setState({
            [e.target.name]: text
        })
    }
    handleIncrement(){
        // console.log("increment")
        let increment = {
            value: this.state.value
		} 
        if(this.props.Incre_root_reducer.incre_value)
		    {
                this.props.increment_action(this.props.Incre_root_reducer.incre_value)
            }
        else{
            
            this.props.increment_action(increment)
        }

		
    }
    handleDecrement(){
        // console.log("decrement")
        let decrement = {
            value: this.state.value
		} 

		this.props.decrement_action(decrement);
    }

    render(){
        const data1  = this.props.Incre_root_reducer;
        // const  data2  = this.props.Decre_root_reducer;
        
        return (
            <MDBContainer>
                <h3 className="font-weight-bold">Increment Decrement Using class component</h3>
                <pre>{JSON.stringify(data1)}</pre>
                {/* <pre>{JSON.stringify(data2)}</pre> */}
                <MDBRow>
                <MDBCol sm="6">
                    <MDBInput label="Enter Input value" type="text" name="inputvalue"  value = {this.state.value} size="sm" background onChange = {this.handlechange}/>
                </MDBCol>
                </MDBRow>
                <MDBRow>
                <MDBCol sm="3">
                    <MDBBtn tag="a" size="sm" floating gradient="purple" onClick = {this.handleIncrement}>
                        <MDBIcon icon="plus" />
                    </MDBBtn>
                </MDBCol>
                <MDBCol sm="3">
                    <MDBInput label="Input value" disabled type="number" value = {this.state.value}  background size="sm"/>
                </MDBCol>
                <MDBCol sm="3">
                    <MDBBtn tag="a" size="sm" floating gradient="peach" onClick = {this.handleDecrement}>
                        <MDBIcon icon="minus" />
                    </MDBBtn>
                </MDBCol>

                </MDBRow>

            </MDBContainer>

        )
    }



}
function mapStateToProps (state)  {

    return{
    
        Incre_root_reducer: state.Incre_root_reducer,
        // Decre_root_reducer : state.Decre_root_reducer
    }
    // console.log("Incre_root_reducer",Incre_root_reducer)
    
  };

export default connect(mapStateToProps, {
	increment_action, 
	decrement_action, 
	
})(Increment_Decrement);
